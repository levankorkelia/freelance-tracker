"""
models.py — პროექტის კლასები (OOP ნაწილი).

კლასი არის „ფორმა", რომლითაც აღვწერთ, როგორ გამოიყურება ერთი ობიექტი.
მაგალითად, ერთ კლიენტს აქვს id, სახელი და საკონტაქტო ინფორმაცია.

ბაზიდან წამოღებული სტრიქონი (row) არის უბრალო მონაცემები.
ამ კლასების დანიშნულებაა, ის მონაცემები გადააქციონ ობიექტად,
რომელსაც საკუთარი მეთოდები (ფუნქციები) აქვს.
"""


class Client:
    """ერთი კლიენტი."""

    def __init__(self, id, name, contact=None):
        # __init__ არის კონსტრუქტორი — ეშვება ობიექტის შექმნისას.
        # self ნიშნავს „თვითონ ეს ობიექტი".
        self.id = id
        self.name = name
        self.contact = contact

    @classmethod
    def from_row(cls, row):
        """
        ქმნის Client ობიექტს ბაზის სტრიქონიდან.

        @classmethod ნიშნავს, რომ ეს მეთოდი მთელ კლასს ეკუთვნის და არა ცალკეულ ობიექტს.
        ვიძახებთ ასე: Client.from_row(row)
        """
        return cls(id=row["id"], name=row["name"], contact=row["contact"])

    def __str__(self):
        """
        __str__ განსაზღვრავს, როგორ გამოჩნდება ობიექტი print()-ისას.
        ამის გარეშე print(client) დაბეჭდავდა რაღაც მსგავსს: <src.models.Client object at 0x...>
        """
        contact = self.contact or "—"
        return f"#{self.id}  {self.name}  ({contact})"


class Project:
    """ერთი პროექტი. ეკუთვნის კონკრეტულ კლიენტს."""

    def __init__(self, id, client_id, title, hourly_rate=0, status="active"):
        self.id = id
        self.client_id = client_id
        self.title = title
        self.hourly_rate = hourly_rate
        self.status = status

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            client_id=row["client_id"],
            title=row["title"],
            hourly_rate=row["hourly_rate"],
            status=row["status"],
        )

    def earnings(self, total_hours):
        """
        ითვლის შემოსავალს მოცემული საათების რაოდენობისთვის.

        ეს არის მაგალითი იმისა, თუ რატომ გვჭირდება კლასი:
        გამოთვლა ცხოვრობს იმ ობიექტთან ერთად, რომელსაც ის ეხება.
        """
        return total_hours * self.hourly_rate

    def __str__(self):
        return f"#{self.id}  {self.title}  ({self.hourly_rate} ₾/სთ, {self.status})"


class TimeEntry:
    """დროის ერთი ჩანაწერი — რამდენი საათი ვიმუშავე კონკრეტულ დღეს."""

    def __init__(self, id, project_id, entry_date, hours, note=None):
        self.id = id
        self.project_id = project_id
        self.entry_date = entry_date
        self.hours = hours
        self.note = note

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            project_id=row["project_id"],
            entry_date=row["entry_date"],
            hours=row["hours"],
            note=row["note"],
        )

    def __str__(self):
        note = self.note or ""
        return f"#{self.id}  {self.entry_date}  {self.hours} სთ  {note}"
