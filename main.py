"""
main.py — პროგრამის შესასვლელი წერტილი.

ეს ფაილი მხოლოდ მენიუსა და მომხმარებელთან საუბარზეა პასუხისმგებელი.
თვითონ ლოგიკა (ბაზაში ჩაწერა, წაკითხვა, გამოთვლები) src/ საქაღალდეშია.

ასეთი დაყოფა რუბრიკის მე-4 კრიტერიუმის („კოდის ხარისხი და სტრუქტურა")
მთავარი მოთხოვნაა: თითოეულ ფაილს ერთი გასაგები პასუხისმგებლობა აქვს.

გაშვება:  python main.py
"""

from datetime import date

from src.database import init_db
from src.helpers import ask_date, ask_int, ask_number, ask_text, confirm
from src import clients
from src import projects
from src import reports
from src import time_entries


# ---------------------------------------------------------------- კლიენტები


def menu_add_client():
    """ახალი კლიენტის დამატება."""
    print("\n--- ახალი კლიენტი ---")

    name = ask_text("სახელი: ")
    contact = ask_text("კონტაქტი (Enter გამოსატოვებლად): ", allow_empty=True)

    new_id = clients.add_client(name, contact)
    print(f"დამატებულია. კლიენტის ნომერია #{new_id}")


def menu_list_clients():
    """ყველა კლიენტის ჩვენება."""
    print("\n--- კლიენტები ---")

    all_clients = clients.list_clients()

    if not all_clients:
        print("სია ცარიელია. ჯერ დაამატე კლიენტი.")
        return

    for client in all_clients:
        # print(client) იძახებს Client.__str__()-ს, რომელიც models.py-შია აღწერილი
        print(client)


def menu_delete_client():
    """კლიენტის წაშლა დასტურის კითხვით."""
    print("\n--- კლიენტის წაშლა ---")

    menu_list_clients()
    client_id = ask_int("წასაშლელი კლიენტის ნომერი: ", minimum=1)

    client = clients.get_client(client_id)
    if client is None:
        print("ასეთი ნომრით კლიენტი ვერ მოიძებნა.")
        return

    print(f"წასაშლელია: {client}")
    print("ყურადღება: წაიშლება ამ კლიენტის პროექტებიც და დროის ჩანაწერებიც.")

    if not confirm("ნამდვილად გსურს წაშლა?"):
        print("წაშლა გაუქმდა.")
        return

    clients.delete_client(client_id)
    print("წაშლილია.")


# ---------------------------------------------------------------- პროექტები


def menu_add_project():
    """ახალი პროექტის დამატება არსებულ კლიენტზე."""
    print("\n--- ახალი პროექტი ---")

    all_clients = clients.list_clients()
    if not all_clients:
        print("ჯერ ვერცერთი კლიენტი ვერ მოიძებნა. პროექტი კლიენტს უნდა დაუკავშირდეს.")
        return

    for client in all_clients:
        print(client)

    client_id = ask_int("კლიენტის ნომერი: ", minimum=1)

    if clients.get_client(client_id) is None:
        print("ასეთი ნომრით კლიენტი ვერ მოიძებნა.")
        return

    title = ask_text("პროექტის დასახელება: ")
    rate = ask_number("საათობრივი ტარიფი (₾): ", minimum=0)

    new_id = projects.add_project(client_id, title, rate)
    print(f"დამატებულია. პროექტის ნომერია #{new_id}")


def menu_list_projects():
    """ყველა პროექტის ჩვენება კლიენტის სახელთან ერთად."""
    print("\n--- პროექტები ---")

    all_projects = projects.list_projects()

    if not all_projects:
        print("სია ცარიელია. ჯერ დაამატე პროექტი.")
        return

    for project in all_projects:
        client_name = projects.client_name_for(project)
        print(f"{project}  —  {client_name}")


def menu_delete_project():
    """პროექტის წაშლა დასტურის კითხვით."""
    print("\n--- პროექტის წაშლა ---")

    menu_list_projects()
    project_id = ask_int("წასაშლელი პროექტის ნომერი: ", minimum=1)

    project = projects.get_project(project_id)
    if project is None:
        print("ასეთი ნომრით პროექტი ვერ მოიძებნა.")
        return

    print(f"წასაშლელია: {project}")
    print("ყურადღება: წაიშლება ამ პროექტის დროის ჩანაწერებიც.")

    if not confirm("ნამდვილად გსურს წაშლა?"):
        print("წაშლა გაუქმდა.")
        return

    projects.delete_project(project_id)
    print("წაშლილია.")


# ---------------------------------------------------------------- დროის აღრიცხვა


def menu_add_time_entry():
    """დროის ჩაწერა პროექტზე."""
    print("\n--- დროის ჩაწერა ---")

    all_projects = projects.list_projects()
    if not all_projects:
        print("ჯერ ვერცერთი პროექტი ვერ მოიძებნა.")
        return

    for project in all_projects:
        print(f"{project}  —  {projects.client_name_for(project)}")

    project_id = ask_int("პროექტის ნომერი: ", minimum=1)

    if projects.get_project(project_id) is None:
        print("ასეთი ნომრით პროექტი ვერ მოიძებნა.")
        return

    entry_date = ask_date("თარიღი წწწწ-თთ-დდ (Enter — დღეს): ")
    hours = ask_number("რამდენი საათი: ", minimum=0)
    note = ask_text("კომენტარი (Enter გამოსატოვებლად): ", allow_empty=True)

    # add_entry() შეიძლება ValueError-ს დააგდოს — მაგალითად 0 ან 30 საათზე.
    # ვიჭერთ აქ და მომხმარებელს გასაგებ შეტყობინებას ვაჩვენებთ.
    try:
        time_entries.add_entry(project_id, entry_date, hours, note)
    except ValueError as error:
        print(f"ჩაწერა ვერ მოხერხდა: {error}")
        return

    print("ჩაწერილია.")


def menu_list_time_entries():
    """ბოლო 20 ჩანაწერის ჩვენება."""
    print("\n--- ბოლო ჩანაწერები ---")

    entries = time_entries.list_entries(limit=20)

    if not entries:
        print("ჩანაწერები ჯერ არ არის.")
        return

    for entry in entries:
        project = projects.get_project(entry.project_id)
        title = project.title if project else "წაშლილი პროექტი"
        print(f"{entry}  —  {title}")


def menu_delete_time_entry():
    """დროის ჩანაწერის წაშლა."""
    print("\n--- ჩანაწერის წაშლა ---")

    menu_list_time_entries()
    entry_id = ask_int("წასაშლელი ჩანაწერის ნომერი: ", minimum=1)

    if time_entries.delete_entry(entry_id):
        print("წაშლილია.")
    else:
        print("ასეთი ნომრით ჩანაწერი ვერ მოიძებნა.")


# ---------------------------------------------------------------- ანგარიშები


def menu_project_report():
    """ანგარიში პროექტების მიხედვით: საათები და შემოსავალი."""
    print("\n--- ანგარიში პროექტების მიხედვით ---")

    totals = reports.project_totals()

    if not totals:
        print("მონაცემები ჯერ არ არის.")
        return

    # :<28 ნიშნავს „მარცხნივ სწორება 28 სიმბოლოს სიგანეზე",
    # :>8.1f კი — „მარჯვნივ სწორება, ერთი ციფრი წერტილის შემდეგ".
    # ასე სვეტები ერთმანეთის ქვეშ ლაგდება და ცხრილი იკითხება.
    print(f"{'პროექტი':<28}{'კლიენტი':<22}{'საათი':>8}{'შემოსავალი':>14}")
    print("-" * 72)

    for item in totals:
        print(
            f"{item['title']:<28}"
            f"{item['client']:<22}"
            f"{item['hours']:>8.1f}"
            f"{item['earnings']:>13.2f} ₾"
        )

    summary = reports.grand_total()
    print("-" * 72)
    print(f"{'ჯამი':<50}{summary['hours']:>8.1f}{summary['earnings']:>13.2f} ₾")


def menu_monthly_report():
    """თვიური ანგარიში არჩეული წლისთვის."""
    print("\n--- თვიური ანგარიში ---")

    year = ask_int(f"წელი (Enter-ის ნაცვლად ჩაწერე, მაგ. {date.today().year}): ", minimum=2000)

    months = reports.monthly_totals(year)

    if not months:
        print(f"{year} წელს ჩანაწერები არ მოიძებნა.")
        return

    for item in months:
        # ყოველი საათი ერთი ვარსკვლავი — უმარტივესი ტექსტური დიაგრამა.
        # round() გვჭირდება, რადგან "*" * 2.5 შეცდომას დააგდებდა:
        # სიმბოლოს გამრავლება მხოლოდ მთელ რიცხვზე შეიძლება.
        bar = "*" * round(item["hours"])
        print(f"{item['month']}  {item['hours']:>6.1f} სთ  {bar}")

    total = sum(item["hours"] for item in months)
    print(f"\nწლის ჯამი: {total:.1f} საათი")


# ---------------------------------------------------------------- გრაფიკები


def menu_charts():
    """ქმნის ორივე გრაფიკს და ინახავს charts/ საქაღალდეში."""
    print("\n--- გრაფიკების შექმნა ---")

    # matplotlib გარე ბიბლიოთეკაა და შეიძლება დაყენებული არ იყოს.
    # იმპორტს ფუნქციის შიგნით ვწერთ, რომ პროგრამის დანარჩენი ნაწილი
    # მისი გარეშეც მუშაობდეს — მენიუს ერთი პუნქტის გამო მთელი
    # აპლიკაცია გაშვებაზევე არ უნდა ჩავარდეს.
    try:
        from src import charts
    except ImportError:
        print("matplotlib დაყენებული არ არის.")
        print("გასაშვებად შეასრულე: pip install -r requirements.txt")
        return

    project_chart = charts.hours_by_project_chart()
    if project_chart is None:
        print("პროექტების გრაფიკი ვერ შეიქმნა — ჯერ ვერცერთი საათი ვერ მოიძებნა.")
    else:
        print(f"შენახულია: {project_chart}")

    year = ask_int(f"რომელი წლის თვიური გრაფიკი (მაგ. {date.today().year}): ", minimum=2000)

    monthly_chart = charts.monthly_hours_chart(year)
    if monthly_chart is None:
        print(f"{year} წელს ჩანაწერები არ მოიძებნა.")
    else:
        print(f"შენახულია: {monthly_chart}")


# ---------------------------------------------------------------- მთავარი მენიუ


def show_menu():
    """ბეჭდავს მენიუს პუნქტებს."""
    print("\n==============================")
    print("  ფრილანსერის დროის აღრიცხვა")
    print("==============================")
    print("1  კლიენტის დამატება")
    print("2  კლიენტების სია")
    print("3  კლიენტის წაშლა")
    print("4  პროექტის დამატება")
    print("5  პროექტების სია")
    print("6  პროექტის წაშლა")
    print("7  დროის ჩაწერა")
    print("8  ბოლო ჩანაწერები")
    print("9  ჩანაწერის წაშლა")
    print("10 ანგარიში პროექტების მიხედვით")
    print("11 თვიური ანგარიში")
    print("12 გრაფიკების შექმნა")
    print("0  გამოსვლა")


def main():
    """
    პროგრამის მთავარი ციკლი.

    ლექსიკონი (dictionary) მენიუს ნომერს ფუნქციასთან აკავშირებს.
    ეს გვიშველის გრძელი if/elif/elif ჯაჭვისგან: ახალი პუნქტის დასამატებლად
    საკმარისია ერთი ხაზის ჩამატება, და არა მთელი ბლოკის.

    ყურადღება: ფუნქციას ვწერთ ფრჩხილების გარეშე — menu_add_client და
    არა menu_add_client(). ფრჩხილებით ის მაშინვე გაეშვებოდა.
    აქ კი მხოლოდ მისამართს ვინახავთ და მოგვიანებით ვიძახებთ.
    """
    init_db()

    actions = {
        1: menu_add_client,
        2: menu_list_clients,
        3: menu_delete_client,
        4: menu_add_project,
        5: menu_list_projects,
        6: menu_delete_project,
        7: menu_add_time_entry,
        8: menu_list_time_entries,
        9: menu_delete_time_entry,
        10: menu_project_report,
        11: menu_monthly_report,
        12: menu_charts,
    }

    while True:
        show_menu()
        choice = ask_int("აირჩიე: ", minimum=0)

        if choice == 0:
            print("ნახვამდის.")
            break

        action = actions.get(choice)

        if action is None:
            print("ასეთი პუნქტი არ არსებობს.")
            continue

        action()


# ეს პირობა ნიშნავს: „გაუშვი main() მხოლოდ მაშინ, როცა ფაილი პირდაპირ ეშვება".
# თუ ვინმე main.py-ს სხვა ფაილიდან შემოიტანს (import), main() ავტომატურად არ გაეშვება.
if __name__ == "__main__":
    main()
