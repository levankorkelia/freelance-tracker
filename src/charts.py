"""
charts.py — გრაფიკების შექმნა matplotlib-ით.

აქ არის ორი გრაფიკი და თითოეული სხვადასხვა კითხვას პასუხობს:

  1. ჰორიზონტალური სვეტები — „რომელ პროექტს რამდენი საათი მოვახმარე?"
     როცა ვადარებთ სიდიდეებს კატეგორიების მიხედვით, სვეტი საუკეთესო ფორმაა.
     ჰორიზონტალურს ვირჩევთ იმიტომ, რომ პროექტების სახელები გრძელია და
     ვერტიკალურ სვეტებზე ისინი ერთმანეთს გადაეფარებოდა.

  2. ხაზი — „როგორ იცვლებოდა დატვირთვა თვეების მიხედვით?"
     როცა ვაჩვენებთ ცვლილებას დროში, ხაზი უკეთესია, ვიდრე სვეტები:
     თვალი ტენდენციას მაშინვე ხედავს.

ფუნქციები მონაცემებს თვითონ არ ითვლიან — ამას reports.py აკეთებს.
აქ მხოლოდ ხატვაა. ისევ იგივე პრინციპი: ერთი ფაილი, ერთი პასუხისმგებლობა.
"""

from pathlib import Path

import matplotlib

# ეს ორი ხაზი ხატვამდე უნდა იყოს.
# "Agg" არის matplotlib-ის რეჟიმი, რომელიც ფაილში ხატავს ფანჯრის გახსნის გარეშე.
# თუ გრაფიკის ფანჯარაში ჩვენებაც გინდა, ეს ხაზი დააკომენტარე.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src import reports

# გრაფიკების შესანახი საქაღალდე — პროექტის ძირში.
BASE_DIR = Path(__file__).parent.parent
CHARTS_DIR = BASE_DIR / "charts"

# ერთი ფერი მთელი გრაფიკისთვის.
# როცა ერთი რიგი მონაცემია, ფერადი სვეტები ზედმეტია: ფერი უნდა
# რაღაცას ნიშნავდეს, თორემ ყურადღებას ტყუილად იტაცებს.
MAIN_COLOR = "#3b6ea5"
GRID_COLOR = "#dddddd"
TEXT_COLOR = "#333333"


def _prepare_output(filename):
    """
    ამზადებს ფაილის სრულ მისამართს და ქმნის charts/ საქაღალდეს, თუ ის არ არსებობს.

    სახელის დასაწყისში ქვედა ტირე (_) მიღებული შეთანხმებაა და ნიშნავს:
    ეს ფუნქცია მხოლოდ ამ ფაილის შიგნით გამოსაყენებელია, გარედან არა.
    """
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    return CHARTS_DIR / filename


def hours_by_project_chart(filename="hours_by_project.png"):
    """
    ხატავს ჰორიზონტალურ სვეტოვან დიაგრამას: რომელ პროექტს რამდენი საათი მოვახმარე.

    აბრუნებს შენახული ფაილის მისამართს, ან None-ს, თუ მონაცემები არ არის.
    """
    totals = reports.project_totals()

    # ვტოვებთ მხოლოდ იმ პროექტებს, სადაც საათები მართლაც ჩაწერილია.
    # ნულოვანი სვეტი გრაფიკზე ადგილს იკავებს და არაფერს გვეუბნება.
    totals = [item for item in totals if item["hours"] > 0]

    if not totals:
        return None

    # project_totals() ჩამოსულია კლებადობით. ჰორიზონტალურ გრაფიკზე
    # პირველი ელემენტი ქვემოთ ხატება, ამიტომ სიას ვაბრუნებთ,
    # რომ ყველაზე დიდი სვეტი ზემოთ აღმოჩნდეს.
    totals = list(reversed(totals))

    titles = [item["title"] for item in totals]
    hours = [item["hours"] for item in totals]

    # figsize არის ზომა დიუმებში. სიმაღლეს პროექტების რაოდენობაზე ვამოკიდებთ,
    # რომ ხუთი პროექტიც და თხუთმეტიც თანაბრად კარგად გამოიყურებოდეს.
    height = max(3, 0.6 * len(totals) + 1.5)
    figure, axes = plt.subplots(figsize=(9, height))

    axes.barh(titles, hours, color=MAIN_COLOR, height=0.6)

    axes.set_title("საათები პროექტების მიხედვით", fontsize=13, color=TEXT_COLOR, pad=15)
    axes.set_xlabel("საათი", fontsize=10, color=TEXT_COLOR)

    # ბადე მხოლოდ ერთი ღერძის გასწვრივ და ღია ფერით.
    # ბადე დამხმარეა და არა მთავარი — ის მონაცემებს არ უნდა ეჯიბრებოდეს.
    axes.grid(axis="x", color=GRID_COLOR, linewidth=0.8)
    axes.set_axisbelow(True)

    # ვშლით ჩარჩოს ზედა და მარჯვენა ხაზებს — ისინი არაფერს გვეუბნება.
    axes.spines["top"].set_visible(False)
    axes.spines["right"].set_visible(False)

    # ციფრს პირდაპირ სვეტის ბოლოში ვწერთ, რომ მკითხველს ღერძზე
    # თვალის გადატანა არ დასჭირდეს.
    for index, value in enumerate(hours):
        axes.text(value, index, f"  {value:.1f}", va="center", fontsize=9, color=TEXT_COLOR)

    # tight_layout() ასწორებს მინდვრებს, რომ გრძელი სახელები არ მოიჭრას.
    figure.tight_layout()

    output_path = _prepare_output(filename)
    figure.savefig(output_path, dpi=150)

    # ფანჯრის დახურვა აუცილებელია: ამის გარეშე ყოველი გამოძახება
    # მეხსიერებაში ახალ გრაფიკს ტოვებდა.
    plt.close(figure)

    return output_path


def monthly_hours_chart(year, filename=None):
    """
    ხატავს ხაზოვან გრაფიკს: როგორ იცვლებოდა საათები თვეების მიხედვით.

    აბრუნებს შენახული ფაილის მისამართს, ან None-ს, თუ ამ წელს ჩანაწერები არ არის.
    """
    months = reports.monthly_totals(year)

    if not months:
        return None

    if filename is None:
        filename = f"monthly_{year}.png"

    labels = [item["month"] for item in months]
    hours = [item["hours"] for item in months]

    figure, axes = plt.subplots(figsize=(9, 4.5))

    # marker="o" ხატავს წერტილს ყოველ გაზომვაზე.
    # ეს მნიშვნელოვანია: ხაზი უწყვეტია, მაგრამ მონაცემები დისკრეტულია —
    # წერტილები აჩვენებს, სად გვაქვს ნამდვილი გაზომვა და სად უბრალოდ შემაერთებელი ხაზი.
    axes.plot(labels, hours, color=MAIN_COLOR, linewidth=2, marker="o", markersize=6)

    axes.set_title(f"დატვირთვა თვეების მიხედვით — {year}", fontsize=13, color=TEXT_COLOR, pad=15)
    axes.set_ylabel("საათი", fontsize=10, color=TEXT_COLOR)

    axes.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    axes.set_axisbelow(True)

    axes.spines["top"].set_visible(False)
    axes.spines["right"].set_visible(False)

    # ღერძი ნულიდან იწყება. ეს პრინციპული საკითხია:
    # თუ სვეტოვან ან ხაზოვან გრაფიკს ნულზე მაღლა დავაწყებთ,
    # მცირე სხვაობა ვიზუალურად რამდენჯერმე გაიზრდება და მკითხველს შევაცდენთ.
    axes.set_ylim(bottom=0)

    figure.tight_layout()

    output_path = _prepare_output(filename)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    return output_path
