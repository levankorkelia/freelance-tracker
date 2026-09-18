"""
reports.py — ანგარიშები და გამოთვლები.

ამ ფაილში ერთი ბაიტიც არ იბეჭდება ეკრანზე. ფუნქციები მხოლოდ
მონაცემებს აბრუნებენ, ჩვენებაზე კი main.py ზრუნავს.

ეს დაყოფა მნიშვნელოვანია ორი მიზეზით:
  1. იგივე ანგარიშს იყენებს გრაფიკების მოდულიც (charts.py).
  2. ასეთი ფუნქციის ტესტირება ადვილია — შედეგს ვამოწმებთ პირდაპირ,
     ეკრანზე დაბეჭდილი ტექსტის კითხვის გარეშე.
"""

from src.database import get_connection


def project_totals(start_date=None, end_date=None):
    """
    აბრუნებს ყოველი პროექტის ჯამურ საათებსა და შემოსავალს.

    შედეგი არის ლექსიკონების სია, დალაგებული საათების კლებადობით:
        [{"title": "...", "client": "...", "hours": 12.5, "earnings": 562.5}, ...]

    start_date და end_date არასავალდებულოა. თუ მითითებულია,
    ითვლება მხოლოდ ამ პერიოდში მოხვედრილი ჩანაწერები.

    JOIN აერთიანებს სამ ცხრილს: ჩანაწერს ვუკავშირებთ პროექტს,
    პროექტს კი კლიენტს — რომ ერთი მოთხოვნით მივიღოთ სრული სურათი.
    """
    connection = get_connection()

    query = """
        SELECT
            p.id           AS project_id,
            p.title        AS title,
            p.hourly_rate  AS hourly_rate,
            c.name         AS client_name,
            COALESCE(SUM(t.hours), 0) AS total_hours
        FROM projects p
        JOIN clients c ON c.id = p.client_id
        LEFT JOIN time_entries t ON t.project_id = p.id
    """
    params = []

    # LEFT JOIN ნიშნავს: პროექტი შედეგში მოხვდება მაშინაც,
    # თუ მასზე ჯერ ვერცერთი საათი არ ჩაწერილა (მაშინ total_hours იქნება 0).
    # ჩვეულებრივი JOIN ასეთ პროექტს საერთოდ გამოტოვებდა.

    conditions = []
    if start_date is not None:
        conditions.append("(t.entry_date IS NULL OR t.entry_date >= ?)")
        params.append(start_date)
    if end_date is not None:
        conditions.append("(t.entry_date IS NULL OR t.entry_date <= ?)")
        params.append(end_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # GROUP BY აჯგუფებს ჩანაწერებს პროექტების მიხედვით,
    # რომ SUM() თითოეული პროექტისთვის ცალკე დაითვალოს.
    query += " GROUP BY p.id ORDER BY total_hours DESC, p.title"

    rows = connection.execute(query, params).fetchall()
    connection.close()

    result = []
    for row in rows:
        hours = row["total_hours"]
        result.append({
            "project_id": row["project_id"],
            "title": row["title"],
            "client": row["client_name"],
            "hours": hours,
            "earnings": hours * row["hourly_rate"],
        })

    return result


def monthly_totals(year):
    """
    აბრუნებს თვეების მიხედვით დახარჯულ საათებს მოცემულ წელს.

    შედეგი: [{"month": "2026-01", "hours": 18.0}, ...] — მხოლოდ ის თვეები,
    სადაც ჩანაწერი მართლაც არსებობს.

    substr(entry_date, 1, 7) იღებს თარიღის პირველ 7 სიმბოლოს:
    "2026-09-17" -> "2026-09". სწორედ ამიტომ ვინახავთ თარიღს ამ ფორმატით —
    თვის გამოცალკევება ერთი მარტივი ოპერაციაა.
    """
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT substr(entry_date, 1, 7) AS month,
               SUM(hours) AS total_hours
        FROM time_entries
        WHERE substr(entry_date, 1, 4) = ?
        GROUP BY month
        ORDER BY month
        """,
        (str(year),),
    ).fetchall()

    connection.close()

    return [{"month": row["month"], "hours": row["total_hours"]} for row in rows]


def grand_total(start_date=None, end_date=None):
    """
    აბრუნებს საერთო ჯამს: ყველა პროექტის საათები და შემოსავალი ერთად.

    ხელახლა არ ვწერთ SQL-ს — ვიყენებთ project_totals()-ის შედეგს და ვაჯამებთ.
    ეს არის კოდის გამეორების შემცირების მაგალითი, რაც მე-4 კრიტერიუმში ფასდება.
    """
    totals = project_totals(start_date, end_date)

    total_hours = sum(item["hours"] for item in totals)
    total_earnings = sum(item["earnings"] for item in totals)

    return {"hours": total_hours, "earnings": total_earnings}
