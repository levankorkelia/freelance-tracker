"""
ტესტები ანგარიშებისთვის.

სწორედ აქ ჩანს, რატომ ვამჯობინეთ, რომ reports.py ეკრანზე არაფერს ბეჭდავს:
ფუნქცია მონაცემებს აბრუნებს, ჩვენ კი პირდაპირ ვამოწმებთ რიცხვებს.
"""

from src import clients, projects, reports, time_entries


def test_earnings_are_hours_times_rate():
    """შემოსავალი უნდა იყოს საათების და ტარიფის ნამრავლი."""
    client_id = clients.add_client("ნინო")
    project_id = projects.add_project(client_id, "ვებგვერდი", hourly_rate=40)

    time_entries.add_entry(project_id, "2026-09-10", 3)

    totals = reports.project_totals()

    assert len(totals) == 1
    assert totals[0]["hours"] == 3
    assert totals[0]["earnings"] == 120


def test_project_without_entries_still_appears():
    """
    პროექტი, რომელზეც ჯერ არავითარი საათი არ ჩაწერილა,
    ანგარიშში მაინც უნდა გამოჩნდეს — ნულოვანი მაჩვენებლებით.

    ეს ამოწმებს LEFT JOIN-ს. ჩვეულებრივი JOIN ასეთ პროექტს გამოტოვებდა.
    """
    client_id = clients.add_client("გიორგი")
    projects.add_project(client_id, "ახალი პროექტი", hourly_rate=60)

    totals = reports.project_totals()

    assert len(totals) == 1
    assert totals[0]["hours"] == 0
    assert totals[0]["earnings"] == 0


def test_totals_are_sorted_by_hours():
    """ანგარიშში ყველაზე დატვირთული პროექტი პირველი უნდა იყოს."""
    client_id = clients.add_client("ანა")

    small = projects.add_project(client_id, "პატარა", hourly_rate=10)
    big = projects.add_project(client_id, "დიდი", hourly_rate=10)

    time_entries.add_entry(small, "2026-09-10", 2)
    time_entries.add_entry(big, "2026-09-10", 9)

    totals = reports.project_totals()

    assert totals[0]["title"] == "დიდი"
    assert totals[1]["title"] == "პატარა"


def test_grand_total_sums_every_project():
    """საერთო ჯამი ყველა პროექტის ჯამს უნდა უდრიდეს."""
    client_id = clients.add_client("დათო")

    first = projects.add_project(client_id, "პირველი", hourly_rate=20)
    second = projects.add_project(client_id, "მეორე", hourly_rate=50)

    time_entries.add_entry(first, "2026-09-10", 3)    # 60 ₾
    time_entries.add_entry(second, "2026-09-10", 2)   # 100 ₾

    summary = reports.grand_total()

    assert summary["hours"] == 5
    assert summary["earnings"] == 160


def test_monthly_totals_group_by_month():
    """
    ერთი თვის ჩანაწერები ერთ ჯგუფში უნდა მოხვდეს,
    სხვადასხვა თვისა კი — ცალკე.
    """
    client_id = clients.add_client("ლელა")
    project_id = projects.add_project(client_id, "პროექტი", hourly_rate=30)

    time_entries.add_entry(project_id, "2026-08-05", 4)
    time_entries.add_entry(project_id, "2026-08-20", 2)
    time_entries.add_entry(project_id, "2026-09-01", 7)

    months = reports.monthly_totals(2026)

    assert months == [
        {"month": "2026-08", "hours": 6},
        {"month": "2026-09", "hours": 7},
    ]


def test_monthly_totals_ignore_other_years():
    """სხვა წლის ჩანაწერები შედეგში არ უნდა მოხვდეს."""
    client_id = clients.add_client("ნიკა")
    project_id = projects.add_project(client_id, "პროექტი", hourly_rate=30)

    time_entries.add_entry(project_id, "2025-12-30", 5)
    time_entries.add_entry(project_id, "2026-01-02", 3)

    months = reports.monthly_totals(2026)

    assert len(months) == 1
    assert months[0]["month"] == "2026-01"
