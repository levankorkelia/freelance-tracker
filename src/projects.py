"""
projects.py — პროექტებთან დაკავშირებული ოპერაციები.

სტრუქტურა იგივეა, რაც clients.py-ში. განსხვავება ისაა, რომ
პროექტი ყოველთვის კონკრეტულ კლიენტს ეკუთვნის (client_id).
"""

from src.database import get_connection
from src.models import Project

# პროექტის დასაშვები სტატუსები.
# ერთ ადგილას ჩაწერილი სია გვიცავს შეცდომებისგან — თუ ვინმემ
# შემთხვევით "aktive" ჩაწეროს, ვალიდაცია ამას დაიჭერს.
VALID_STATUSES = ("active", "paused", "done")


def add_project(client_id, title, hourly_rate=0, status="active"):
    """ამატებს ახალ პროექტს და აბრუნებს მის id-ს."""
    connection = get_connection()

    with connection:
        cursor = connection.execute(
            """INSERT INTO projects (client_id, title, hourly_rate, status)
               VALUES (?, ?, ?, ?)""",
            (client_id, title, hourly_rate, status),
        )
        new_id = cursor.lastrowid

    connection.close()
    return new_id


def list_projects(client_id=None):
    """
    აბრუნებს პროექტებს.

    თუ client_id მითითებულია, აბრუნებს მხოლოდ ამ კლიენტის პროექტებს.
    თუ არა — ყველას. ერთი ფუნქცია ორ საჭიროებას ფარავს,
    ნაცვლად იმისა, რომ თითქმის იდენტური კოდი ორჯერ დავწეროთ.
    """
    connection = get_connection()

    if client_id is None:
        rows = connection.execute("SELECT * FROM projects ORDER BY id").fetchall()
    else:
        rows = connection.execute(
            "SELECT * FROM projects WHERE client_id = ? ORDER BY id", (client_id,)
        ).fetchall()

    connection.close()
    return [Project.from_row(row) for row in rows]


def get_project(project_id):
    """აბრუნებს ერთ პროექტს id-ით, ან None-ს თუ ვერ მოიძებნა."""
    connection = get_connection()
    row = connection.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    connection.close()

    if row is None:
        return None
    return Project.from_row(row)


def update_project(project_id, title, hourly_rate, status):
    """ცვლის პროექტის მონაცემებს. აბრუნებს True-ს, თუ ჩანაწერი შეიცვალა."""
    connection = get_connection()

    with connection:
        cursor = connection.execute(
            """UPDATE projects
               SET title = ?, hourly_rate = ?, status = ?
               WHERE id = ?""",
            (title, hourly_rate, status, project_id),
        )
        changed = cursor.rowcount > 0

    connection.close()
    return changed


def delete_project(project_id):
    """შლის პროექტს მისი დროის ჩანაწერებთან ერთად. აბრუნებს True-ს წარმატებისას."""
    connection = get_connection()

    with connection:
        cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        deleted = cursor.rowcount > 0

    connection.close()
    return deleted


def client_name_for(project):
    """
    დამხმარე ფუნქცია: აბრუნებს პროექტის კლიენტის სახელს.

    სიაში პროექტის ჩვენებისას გვინდა დავწეროთ კლიენტის სახელი და არა client_id=3.
    """
    connection = get_connection()
    row = connection.execute(
        "SELECT name FROM clients WHERE id = ?", (project.client_id,)
    ).fetchone()
    connection.close()

    if row is None:
        return "უცნობი"
    return row["name"]
