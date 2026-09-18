"""
time_entries.py — დროის ჩანაწერებთან მუშაობა.

ერთი ჩანაწერი ნიშნავს: „კონკრეტულ დღეს, კონკრეტულ პროექტზე, ამდენი საათი ვიმუშავე".
სწორედ ამ ჩანაწერებზე დგას მთელი აპლიკაცია — ანგარიშებიც და გრაფიკებიც აქედან იღებს მონაცემებს.
"""

from src.database import get_connection
from src.models import TimeEntry

# ერთ დღეში 24 საათზე მეტის ჩაწერა აშკარა შეცდომაა.
# ასეთ ზღვარს სანიტი ჩეკი ჰქვია — ის უაზრო მონაცემებს ბაზაში არ უშვებს.
MAX_HOURS_PER_ENTRY = 24


def add_entry(project_id, entry_date, hours, note=None):
    """
    ამატებს დროის ჩანაწერს.

    აგდებს ValueError-ს, თუ საათების რაოდენობა უაზროა.
    ყურადღება: შეცდომას აქ ვაგდებთ, მაგრამ არ ვიჭერთ — დაჭერა
    main.py-ის საქმეა, რადგან მხოლოდ იქ ვიცით, როგორ ვაცნობოთ მომხმარებელს.
    ლოგიკის ფაილი ეკრანზე არაფერს ბეჭდავს.
    """
    if hours <= 0:
        raise ValueError("საათების რაოდენობა ნულზე მეტი უნდა იყოს.")

    if hours > MAX_HOURS_PER_ENTRY:
        raise ValueError(f"ერთ ჩანაწერში {MAX_HOURS_PER_ENTRY} საათზე მეტი ვერ იქნება.")

    connection = get_connection()

    with connection:
        cursor = connection.execute(
            """INSERT INTO time_entries (project_id, entry_date, hours, note)
               VALUES (?, ?, ?, ?)""",
            (project_id, entry_date, hours, note),
        )
        new_id = cursor.lastrowid

    connection.close()
    return new_id


def list_entries(project_id=None, limit=None):
    """
    აბრუნებს დროის ჩანაწერებს, ახლიდან ძველისკენ დალაგებულს.

    limit გვჭირდება იმისთვის, რომ ეკრანზე ასობით ხაზი არ დავბეჭდოთ —
    ჩვეულებრივ ბოლო 20 ჩანაწერიც საკმარისია.
    """
    connection = get_connection()

    # SQL-ს ნაწილ-ნაწილ ვაწყობთ, პარამეტრებს კი ცალკე სიაში ვაგროვებთ.
    # ასე ვინარჩუნებთ დაცვას SQL injection-ისგან.
    query = "SELECT * FROM time_entries"
    params = []

    if project_id is not None:
        query += " WHERE project_id = ?"
        params.append(project_id)

    query += " ORDER BY entry_date DESC, id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    rows = connection.execute(query, params).fetchall()
    connection.close()

    return [TimeEntry.from_row(row) for row in rows]


def delete_entry(entry_id):
    """შლის ერთ ჩანაწერს. აბრუნებს True-ს, თუ წაშლა მოხდა."""
    connection = get_connection()

    with connection:
        cursor = connection.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
        deleted = cursor.rowcount > 0

    connection.close()
    return deleted


def total_hours_for_project(project_id):
    """
    აბრუნებს პროექტზე დახარჯულ ჯამურ საათებს.

    SUM() არის SQL-ის ფუნქცია, რომელიც ჯამს ითვლის.
    თუ ჩანაწერები საერთოდ არ არის, SUM() აბრუნებს NULL-ს (Python-ში None).
    COALESCE(SUM(hours), 0) ნიშნავს: „თუ NULL დაბრუნდა, მაგივრად 0 გამოიყენე".
    ამის გარეშე გამოთვლებში None მოხვდებოდა და პროგრამა შეცდომით გაჩერდებოდა.
    """
    connection = get_connection()
    row = connection.execute(
        "SELECT COALESCE(SUM(hours), 0) AS total FROM time_entries WHERE project_id = ?",
        (project_id,),
    ).fetchone()
    connection.close()

    return row["total"]
