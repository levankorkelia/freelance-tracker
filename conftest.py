"""
conftest.py — pytest-ის საერთო მომზადება ყველა ტესტისთვის.

ეს ფაილი პროექტის ძირში უნდა იყოს. pytest მას თავად პოულობს
და ტესტების გაშვებამდე კითხულობს — იმპორტი არსად არ გვჭირდება.
"""

import pytest

from src.database import ENV_DB_PATH, init_db


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    """
    ყოველი ტესტისთვის ქმნის ახალ, ცარიელ ბაზას დროებით საქაღალდეში.

    fixture არის pytest-ის ტერმინი: მომზადება, რომელიც ტესტის გაშვებამდე სრულდება.
    autouse=True ნიშნავს, რომ ის ავტომატურად ეშვება ყველა ტესტისთვის,
    ცალკე მითითების გარეშე.

    tmp_path — pytest-ის მიერ შექმნილი დროებითი საქაღალდე. ის ყოველი
    ტესტისთვის ახალია და ტესტის შემდეგ ავტომატურად იშლება.

    monkeypatch.setenv — დროებით აყენებს გარემოს ცვლადს და ტესტის
    დასრულებისას ყველაფერს უკან აბრუნებს.

    შედეგად ტესტები არასდროს შეეხება შენს ნამდვილ data/tracker.db-ს.
    """
    monkeypatch.setenv(ENV_DB_PATH, str(tmp_path / "test.db"))
    init_db()
