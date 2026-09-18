"""
clients.py — კლიენტებთან დაკავშირებული ყველა ოპერაცია.

აქ არის ოთხივე ძირითადი მოქმედება, რომელსაც ინგლისურად CRUD ჰქვია:
  Create — დამატება
  Read   — წაკითხვა
  Update — რედაქტირება
  Delete — წაშლა
"""

from src.database import get_connection
from src.models import Client


def add_client(name, contact=None):
    """
    ამატებს ახალ კლიენტს და აბრუნებს მის id-ს.

    ყურადღება მიაქციე კითხვის ნიშნებს SQL-ში: VALUES (?, ?)
    მნიშვნელობებს ცალკე გადავცემთ, ტექსტში ჩაკერების ნაცვლად.
    ეს იცავს SQL injection-ისგან — თუ სახელში SQL ბრძანება ჩაიწერა,
    sqlite3 მას ჩვეულებრივ ტექსტად აღიქვამს და არ შეასრულებს.
    """
    connection = get_connection()

    with connection:
        cursor = connection.execute(
            "INSERT INTO clients (name, contact) VALUES (?, ?)",
            (name, contact),
        )
        # lastrowid არის ახლად დამატებული სტრიქონის id
        new_id = cursor.lastrowid

    connection.close()
    return new_id


def list_clients():
    """აბრუნებს ყველა კლიენტს სიის სახით, სახელის ანბანური თანმიმდევრობით."""
    connection = get_connection()
    rows = connection.execute("SELECT * FROM clients ORDER BY name").fetchall()
    connection.close()

    # სიის შემოკლებული ჩაწერა (list comprehension):
    # ყოველი row-სთვის ვქმნით Client ობიექტს და ვაბრუნებთ ერთ სიად.
    return [Client.from_row(row) for row in rows]


def get_client(client_id):
    """
    აბრუნებს ერთ კლიენტს id-ით. თუ ასეთი არ არსებობს, აბრუნებს None.

    fetchone() აბრუნებს პირველ სტრიქონს ან None-ს, თუ შედეგი ცარიელია.
    """
    connection = get_connection()
    row = connection.execute(
        "SELECT * FROM clients WHERE id = ?", (client_id,)
    ).fetchone()
    connection.close()

    if row is None:
        return None
    return Client.from_row(row)


def update_client(client_id, name, contact=None):
    """
    ცვლის კლიენტის მონაცემებს. აბრუნებს True-ს, თუ ჩანაწერი მართლაც შეიცვალა.

    cursor.rowcount გვეუბნება, რამდენ სტრიქონს შეეხო ბრძანება.
    თუ 0 დაბრუნდა, ასეთი id საერთოდ არ არსებობდა.
    """
    connection = get_connection()

    with connection:
        cursor = connection.execute(
            "UPDATE clients SET name = ?, contact = ? WHERE id = ?",
            (name, contact, client_id),
        )
        changed = cursor.rowcount > 0

    connection.close()
    return changed


def delete_client(client_id):
    """
    შლის კლიენტს. აბრუნებს True-ს, თუ წაშლა მოხდა.

    გაითვალისწინე: ბაზაში ჩაწერილი გვაქვს ON DELETE CASCADE,
    ამიტომ კლიენტთან ერთად წაიშლება მისი პროექტებიც და იმ პროექტების
    დროის ჩანაწერებიც. ამიტომ პროგრამა ამას წაშლამდე გვაფრთხილებს.
    """
    connection = get_connection()

    with connection:
        cursor = connection.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        deleted = cursor.rowcount > 0

    connection.close()
    return deleted
