"""
database.py — მონაცემთა ბაზასთან მუშაობა.

ამ ფაილის ერთადერთი პასუხისმგებლობაა SQLite ბაზასთან დაკავშირება
და ცხრილების შექმნა. აპლიკაციის დანარჩენი ნაწილი ბაზის დეტალებს
პირდაპირ არ ეხება — ის ყოველთვის აქედან იღებს კავშირს.
"""

import os
import sqlite3
from pathlib import Path

# ბაზის ფაილის მისამართი: პროექტის ძირში, data/ საქაღალდეში.
# Path(__file__) — ამ ფაილის მისამართი. .parent.parent — ორი დონით ზემოთ (src/ -> პროექტის ძირი).
BASE_DIR = Path(__file__).parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "tracker.db"

# გარემოს ცვლადის სახელი, რომლითაც ბაზის მისამართის შეცვლა შეიძლება.
ENV_DB_PATH = "TRACKER_DB"


def get_db_path():
    """
    აბრუნებს ბაზის ფაილის მისამართს.

    ჩვეულებრივ ეს არის data/tracker.db. მაგრამ თუ გარემოს ცვლადი
    TRACKER_DB დაყენებულია, ვიყენებთ მას.

    რატომ გვჭირდება ეს? ტესტებისთვის. ტესტი არ უნდა შეეხოს
    ნამდვილ მონაცემებს — მას დროებითი, ცარიელი ბაზა სჭირდება.
    ამ ერთი ფუნქციის წყალობით ტესტი ამბობს „ბაზა აქ იყოს"
    და დანარჩენი კოდი ცვლილების გარეშე მუშაობს.
    """
    custom_path = os.environ.get(ENV_DB_PATH)

    if custom_path:
        return Path(custom_path)

    return DEFAULT_DB_PATH


def get_connection():
    """
    აბრუნებს ბაზასთან კავშირს.

    თუ საქაღალდე არ არსებობს, ვქმნით მას — თორემ sqlite3 შეცდომას დააგდებს.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    # row_factory = sqlite3.Row ნიშნავს, რომ შედეგის სტრიქონებს
    # წავიკითხავთ სახელით: row["name"], და არა row[1]-ით.
    # ეს კოდს ბევრად უფრო წაკითხვადს ხდის.
    connection.row_factory = sqlite3.Row

    # ვრთავთ გარე გასაღებების შემოწმებას. SQLite-ს ეს ნაგულისხმევად გამორთული აქვს.
    # ამის გარეშე შესაძლებელი იქნებოდა პროექტის დამატება არარსებულ კლიენტზე.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """
    ქმნის ცხრილებს, თუ ისინი ჯერ არ არსებობს.

    ამ ფუნქციას ვიძახებთ პროგრამის ყოველ გაშვებაზე.
    "IF NOT EXISTS" გვიცავს იმისგან, რომ არსებული მონაცემები წაიშალოს.
    """
    connection = get_connection()

    # "with connection" ავტომატურად ინახავს ცვლილებებს (commit),
    # ხოლო შეცდომის შემთხვევაში აბრუნებს უკან (rollback).
    with connection:
        # --- კლიენტების ცხრილი ---
        connection.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                contact TEXT
            )
        """)

        # --- პროექტების ცხრილი ---
        # client_id აკავშირებს პროექტს კლიენტთან.
        # ON DELETE CASCADE — კლიენტის წაშლისას მისი პროექტებიც წაიშლება.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id   INTEGER NOT NULL,
                title       TEXT NOT NULL,
                hourly_rate REAL NOT NULL DEFAULT 0,
                status      TEXT NOT NULL DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)

        # --- დროის ჩანაწერების ცხრილი ---
        # თითოეული ჩანაწერი ეკუთვნის ერთ პროექტს.
        # თარიღს ვინახავთ ტექსტად, ფორმატით YYYY-MM-DD (მაგ. 2026-09-17).
        # ასეთი ჩაწერისას თარიღების დალაგება ჩვეულებრივი ტექსტის სორტირებითაც სწორად მუშაობს.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL,
                entry_date  TEXT NOT NULL,
                hours       REAL NOT NULL,
                note        TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

    connection.close()
