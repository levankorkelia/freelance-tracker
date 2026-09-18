"""
helpers.py — დამხმარე ფუნქციები მომხმარებლისგან მონაცემების მისაღებად.

რატომ ცალკე ფაილი? იმიტომ, რომ „მომხმარებელს ვკითხოთ რიცხვი და დავრწმუნდეთ,
რომ ის მართლაც რიცხვია" ერთი და იგივე ამოცანაა მენიუს ყველა ადგილას.
ერთხელ ვწერთ და ყველგან ვიყენებთ — კოდის გამეორება მცირდება.
"""


def ask_text(prompt, allow_empty=False):
    """
    ითხოვს ტექსტს მომხმარებლისგან.

    while True ქმნის უსასრულო ციკლს: კითხვას ვიმეორებთ მანამ,
    სანამ სწორ პასუხს არ მივიღებთ. return ციკლიდან გამოგვიყვანს.

    .strip() შლის დასაწყისსა და ბოლოში მოხვედრილ ზედმეტ ჰარეებს.
    """
    while True:
        value = input(prompt).strip()

        if value:
            return value

        if allow_empty:
            # ცარიელი პასუხი დაშვებულია — ვაბრუნებთ None-ს და არა ცარიელ ტექსტს,
            # რომ ბაზაში „არაფერი" და „ცარიელი სტრიქონი" არ აგვერიოს.
            return None

        print("ეს ველი სავალდებულოა. სცადე თავიდან.")


def ask_number(prompt, minimum=0):
    """
    ითხოვს ათწილად რიცხვს (მაგალითად, 2.5 საათს ან 45.50 ლარს).

    float("abc") შეცდომას აგდებს — ValueError.
    try/except სწორედ ამიტომ გვჭირდება: შეცდომას ვიჭერთ და
    პროგრამის გაჩერების ნაცვლად თავაზიანად ვთხოვთ თავიდან შეყვანას.
    """
    while True:
        raw = input(prompt).strip()

        # მძიმე წერტილად ვაქციოთ — ბევრი ადამიანი 2,5-ს წერს 2.5-ის ნაცვლად.
        raw = raw.replace(",", ".")

        try:
            value = float(raw)
        except ValueError:
            print("გთხოვ, შეიყვანე რიცხვი (მაგალითად: 2.5).")
            continue

        if value < minimum:
            print(f"რიცხვი არ უნდა იყოს {minimum}-ზე ნაკლები.")
            continue

        return value


def ask_int(prompt, minimum=None):
    """ითხოვს მთელ რიცხვს — მაგალითად, ჩანაწერის id-ს ან მენიუს პუნქტის ნომერს."""
    while True:
        raw = input(prompt).strip()

        try:
            value = int(raw)
        except ValueError:
            print("გთხოვ, შეიყვანე მთელი რიცხვი.")
            continue

        if minimum is not None and value < minimum:
            print(f"რიცხვი არ უნდა იყოს {minimum}-ზე ნაკლები.")
            continue

        return value


def ask_date(prompt, allow_today=True):
    """
    ითხოვს თარიღს ფორმატით წწწწ-თთ-დდ (მაგალითად: 2026-09-17).

    თუ მომხმარებელი უბრალოდ Enter-ს დააჭერს, ვიღებთ დღევანდელ თარიღს —
    ყოველდღიური ჩაწერისას ეს ყველაზე ხშირად საჭირო მნიშვნელობაა.

    datetime.strptime() ცდილობს ტექსტის თარიღად გარდაქმნას.
    თუ ფორმატი არასწორია ან თარიღი არ არსებობს (მაგალითად 2026-02-30),
    ის აგდებს ValueError-ს, რომელსაც ვიჭერთ.
    """
    from datetime import date, datetime

    while True:
        raw = input(prompt).strip()

        if not raw and allow_today:
            # date.today() აბრუნებს დღევანდელ თარიღს,
            # isoformat() კი გადააქცევს ტექსტად: "2026-09-17"
            return date.today().isoformat()

        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            print("თარიღის ფორმატი უნდა იყოს წწწწ-თთ-დდ, მაგალითად 2026-09-17.")
            continue

        return parsed.date().isoformat()


def confirm(prompt):
    """
    დასტურის კითხვა. აბრუნებს True-ს მხოლოდ მაშინ, თუ პასუხი ნამდვილად „კი"-ა.

    ნაგულისხმევი პასუხი უარყოფითია: შემთხვევითი Enter წაშლას არ გამოიწვევს.
    """
    answer = input(f"{prompt} (კი/არა): ").strip().lower()
    return answer in ("კი", "k", "y", "yes")
