"""
ტესტები დამხმარე ფუნქციებისთვის.

ეს ფუნქციები მომხმარებელს input()-ით ეკითხებიან. ტესტში კლავიატურა არ გვაქვს,
ამიტომ monkeypatch-ით input()-ს დროებით ჩვენს ფუნქციას ვუცვლით —
ის თითო პასუხს წინასწარ მომზადებული სიიდან აბრუნებს.

ასე ვამოწმებთ ყველაზე მნიშვნელოვანს: რომ არასწორ პასუხზე პროგრამა
არ ჩავარდება, არამედ თავიდან იკითხავს.
"""

from src.helpers import ask_date, ask_int, ask_number, confirm


def feed_inputs(monkeypatch, answers):
    """
    აიძულებს input()-ს, თანმიმდევრობით დააბრუნოს answers სიის ელემენტები.

    iter() სიას აქცევს იტერატორად, next() კი ყოველ გამოძახებაზე
    შემდეგ ელემენტს იღებს — ზუსტად ისე, როგორც მომხმარებელი წერდა
    პასუხებს ერთმანეთის მიყოლებით.
    """
    answers_iterator = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers_iterator))


def test_ask_number_accepts_comma_as_decimal(monkeypatch):
    """„2,5" და „2.5" ერთსა და იმავე რიცხვად უნდა წაიკითხოს."""
    feed_inputs(monkeypatch, ["2,5"])

    assert ask_number("საათი: ") == 2.5


def test_ask_number_repeats_after_invalid_input(monkeypatch):
    """
    ასოებზე პროგრამა არ უნდა ჩავარდეს — უნდა იკითხოს თავიდან.

    პირველი პასუხი არასწორია, მეორე სწორი. ველოდებით მეორეს.
    """
    feed_inputs(monkeypatch, ["abc", "4"])

    assert ask_number("საათი: ") == 4


def test_ask_number_rejects_below_minimum(monkeypatch):
    """მინიმუმზე ნაკლები რიცხვი არ უნდა გაიაროს."""
    feed_inputs(monkeypatch, ["-3", "1.5"])

    assert ask_number("საათი: ", minimum=0) == 1.5


def test_ask_int_repeats_after_invalid_input(monkeypatch):
    """ათწილადი მაშინ, როცა მთელი გვჭირდება, თავიდან კითხვას იწვევს."""
    feed_inputs(monkeypatch, ["2.5", "7"])

    assert ask_int("ნომერი: ") == 7


def test_ask_date_rejects_nonexistent_date(monkeypatch):
    """
    30 თებერვალი არ არსებობს — ასეთი თარიღი არ უნდა გაიაროს.

    სწორედ ამას იჭერს datetime.strptime(). უბრალო ფორმატის შემოწმება
    (ციფრები და ტირეები) ამ შეცდომას ვერ დაიჭერდა.
    """
    feed_inputs(monkeypatch, ["2026-02-30", "2026-02-28"])

    assert ask_date("თარიღი: ") == "2026-02-28"


def test_ask_date_rejects_wrong_format(monkeypatch):
    """ფორმატი 17/09/2026 არ არის მისაღები."""
    feed_inputs(monkeypatch, ["17/09/2026", "2026-09-17"])

    assert ask_date("თარიღი: ") == "2026-09-17"


def test_confirm_requires_explicit_yes(monkeypatch):
    """
    დასტური მხოლოდ მკაფიო „კი"-ზე უნდა დაბრუნდეს.

    ეს მნიშვნელოვანია: წაშლა შეუქცევადია, ამიტომ ცარიელი Enter
    ან გაუგებარი პასუხი უარად უნდა ჩაითვალოს.
    """
    feed_inputs(monkeypatch, ["კი"])
    assert confirm("წავშალო?") is True

    feed_inputs(monkeypatch, [""])
    assert confirm("წავშალო?") is False

    feed_inputs(monkeypatch, ["მერე"])
    assert confirm("წავშალო?") is False
