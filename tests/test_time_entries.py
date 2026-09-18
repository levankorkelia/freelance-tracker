"""
ტესტები დროის ჩანაწერებისთვის.

pytest-ის წესები მარტივია:
  * ფაილის სახელი იწყება test_-ით
  * ფუნქციის სახელი იწყება test_-ით
  * შემოწმებას ვწერთ assert-ით: „ეს ასე უნდა იყოს"

გაშვება პროექტის ძირიდან:  pytest
"""

import pytest

from src import clients, projects, time_entries


def create_sample_project(rate=50):
    """
    დამხმარე ფუნქცია: ქმნის კლიენტს და პროექტს და აბრუნებს პროექტის id-ს.

    თითქმის ყველა ტესტს სჭირდება პროექტი, რომელზეც საათებს ჩაწერს.
    ერთხელ ვწერთ და ყველგან ვიყენებთ.

    სახელი test_-ით არ იწყება, ამიტომ pytest მას ტესტად არ ჩათვლის.
    """
    client_id = clients.add_client("ტესტ კლიენტი")
    return projects.add_project(client_id, "ტესტ პროექტი", hourly_rate=rate)


def test_add_entry_saves_the_record():
    """ჩაწერილი საათები ბაზაში უნდა აღმოჩნდეს."""
    project_id = create_sample_project()

    time_entries.add_entry(project_id, "2026-09-10", 3.5)

    entries = time_entries.list_entries(project_id)

    assert len(entries) == 1
    assert entries[0].hours == 3.5
    assert entries[0].entry_date == "2026-09-10"


def test_zero_hours_is_rejected():
    """
    ნულოვანი საათი უაზროა და ბაზაში არ უნდა მოხვდეს.

    pytest.raises ამოწმებს, რომ კოდმა მართლაც დააგდო მოსალოდნელი შეცდომა.
    თუ შეცდომა არ დაეგდო, ტესტი ჩავარდება — და ეს სწორია:
    ვალიდაციის გაუქმება შეუმჩნეველი არ უნდა დარჩეს.
    """
    project_id = create_sample_project()

    with pytest.raises(ValueError):
        time_entries.add_entry(project_id, "2026-09-10", 0)


def test_more_than_24_hours_is_rejected():
    """ერთ დღეში 24 საათზე მეტი ვერ იქნება."""
    project_id = create_sample_project()

    with pytest.raises(ValueError):
        time_entries.add_entry(project_id, "2026-09-10", 25)


def test_total_hours_sums_all_entries():
    """ჯამური საათები ყველა ჩანაწერის ჯამს უნდა უდრიდეს."""
    project_id = create_sample_project()

    time_entries.add_entry(project_id, "2026-09-10", 2)
    time_entries.add_entry(project_id, "2026-09-11", 3.5)

    assert time_entries.total_hours_for_project(project_id) == 5.5


def test_total_hours_is_zero_when_no_entries():
    """
    როცა ჩანაწერები არ არის, შედეგი უნდა იყოს 0 და არა None.

    სწორედ ამას აკეთებს COALESCE SQL-ში. ეს ტესტი გვიცავს იმისგან,
    რომ ვინმემ მოგვიანებით COALESCE ამოიღოს და პროგრამა ჩავარდეს.
    """
    project_id = create_sample_project()

    assert time_entries.total_hours_for_project(project_id) == 0


def test_deleting_project_removes_its_entries():
    """
    პროექტის წაშლისას მისი დროის ჩანაწერებიც უნდა წაიშალოს.

    ეს ამოწმებს ბაზაში ჩაწერილ ON DELETE CASCADE-ს —
    ანუ იმას, რომ PRAGMA foreign_keys მართლაც ჩართულია.
    """
    project_id = create_sample_project()
    time_entries.add_entry(project_id, "2026-09-10", 4)

    projects.delete_project(project_id)

    assert time_entries.list_entries(project_id) == []
