from pathlib import Path
import textwrap

from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "pdfs"
OUT = ROOT / "output" / "pdf"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PDF_ROOT = ROOT / "itinerary.pdf"
PDF_OUTPUT = OUT / "itinerary.pdf"

ASSETS = ROOT / "assets"
HERO_WIDE = ASSETS / "hero-wide.jpg"
HERO_PORTRAIT = ASSETS / "hero-portrait.jpg"
DOCTORS = ASSETS / "doctors-hana-ruth.jpg"

W, H = letter
M = 42

INK = colors.HexColor("#102033")
DEEP = colors.HexColor("#071625")
BLUE = colors.HexColor("#0b77bd")
AQUA = colors.HexColor("#42c4e8")
FOAM = colors.HexColor("#eff9fb")
PAPER = colors.HexColor("#fff9ef")
SUN = colors.HexColor("#f7c85c")
CORAL = colors.HexColor("#ef7c68")
GREEN = colors.HexColor("#2e8b57")
MUTED = colors.HexColor("#64748b")
LINE = colors.Color(0.07, 0.12, 0.18, alpha=0.13)

MAP_URL = "https://skabone.github.io/Boat-Day/"
ITINERARY_URL = "https://skabone.github.io/Boat-Day/itinerary.html"
PDF_URL = "https://skabone.github.io/Boat-Day/itinerary.pdf"


def crop_image(src, name, size):
    target = TMP / name
    with Image.open(src) as img:
        img = img.convert("RGB")
        ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.42)).save(target, quality=88)
    return target


def rounded(c, x, y, w, h, fill, stroke=LINE, radius=8, width=1):
    c.saveState()
    c.setLineWidth(width)
    c.setStrokeColor(stroke)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.restoreState()


def fit_words(c, text, max_width, font="Helvetica", size=10):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_text(c, text, x, y, max_width, font="Helvetica", size=10, leading=13, color=INK):
    c.saveState()
    c.setFillColor(color)
    c.setFont(font, size)
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            y -= leading
            continue
        for line in fit_words(c, paragraph, max_width, font, size):
            c.drawString(x, y, line)
            y -= leading
    c.restoreState()
    return y


def draw_title(c, text, x, y, max_width, size=30, color=DEEP):
    c.saveState()
    c.setFillColor(color)
    c.setFont("Times-Bold", size)
    for line in fit_words(c, text, max_width, "Times-Bold", size):
        c.drawString(x, y, line)
        y -= size * 1.04
    c.restoreState()
    return y


def draw_label(c, text, x, y, color=BLUE):
    c.saveState()
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x, y, text.upper())
    c.restoreState()


def draw_chip(c, text, x, y, fill=FOAM, color=BLUE):
    width = c.stringWidth(text, "Helvetica-Bold", 8.5) + 18
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(colors.Color(0, 0, 0, alpha=0))
    c.roundRect(x, y - 7, width, 19, 9, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x + 9, y - 1, text)
    c.restoreState()
    return x + width + 7


def draw_qr(c, url, x, y, size):
    qr = QrCodeWidget(url)
    bounds = qr.getBounds()
    qr_w = bounds[2] - bounds[0]
    qr_h = bounds[3] - bounds[1]
    drawing = Drawing(size, size, transform=[size / qr_w, 0, 0, size / qr_h, 0, 0])
    drawing.add(qr)
    renderPDF.draw(drawing, c, x, y)


def draw_link_card(c, title, url, x, y, w, h, fill=colors.white):
    rounded(c, x, y, w, h, fill)
    qr_size = h - 28
    draw_qr(c, url, x + 14, y + 14, qr_size)
    tx = x + qr_size + 28
    draw_label(c, title, tx, y + h - 25)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(INK)
    c.drawString(tx, y + h - 43, "Scan or tap the public link")
    draw_text(c, url, tx, y + h - 61, w - qr_size - 42, "Helvetica", 8.2, 10.5, MUTED)


def draw_list(c, items, x, y, max_width, size=10.2, leading=13.5, color=INK):
    for item in items:
        c.saveState()
        c.setStrokeColor(BLUE)
        c.setLineWidth(1.5)
        c.roundRect(x, y - 3, 9, 9, 2, fill=0, stroke=1)
        c.restoreState()
        y = draw_text(c, item, x + 17, y, max_width - 17, "Helvetica", size, leading, color)
        y -= 4
    return y


def footer(c, page):
    c.saveState()
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.Color(0.1, 0.14, 0.2, alpha=0.55))
    c.drawString(M, 24, "Anchors Aweigh for Drs. Hana & Ruth")
    c.drawRightString(W - M, 24, f"Page {page}")
    c.restoreState()


def draw_cover(c):
    cover = crop_image(HERO_WIDE, "cover.jpg", (1600, 1060))
    c.drawImage(ImageReader(cover), 0, 0, W, H, mask="auto")
    c.saveState()
    c.setFillColor(colors.Color(0.02, 0.08, 0.14, alpha=0.66))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.restoreState()

    x = M
    y = H - 86
    draw_label(c, "Thursday, May 28, 2026 - Lake Washington", x, y, AQUA)
    y -= 22
    y = draw_title(c, "Anchors Aweigh: A Lake Washington Sendoff for Drs. Hana & Ruth", x, y, W - 2 * M, 34, colors.white)
    y -= 6
    draw_text(c, "Captain Mintay's one-link package for the live route, itinerary, packing list, weather snapshot, photo moments, and printable plan.", x, y, W - 2 * M, "Helvetica", 12.5, 16, colors.Color(1, 1, 1, alpha=0.84))

    stat_y = 238
    stat_w = (W - 2 * M - 18) / 3
    stats = [("Boating Captain", "Mintay"), ("Doctors", "Hana and Ruth"), ("Main Window", "10:45 AM - 8:30 PM")]
    for idx, (label, value) in enumerate(stats):
        sx = M + idx * (stat_w + 9)
        rounded(c, sx, stat_y, stat_w, 72, colors.Color(0.02, 0.08, 0.14, alpha=0.62), colors.Color(1, 1, 1, alpha=0.2))
        draw_label(c, label, sx + 12, stat_y + 45, AQUA)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(sx + 12, stat_y + 22, value)

    draw_link_card(c, "Live map", MAP_URL, M, 86, 252, 104, colors.Color(1, 1, 1, alpha=0.92))
    draw_link_card(c, "Itinerary", ITINERARY_URL, W - M - 252, 86, 252, 104, colors.Color(1, 1, 1, alpha=0.92))


def draw_page_two(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - 64
    draw_label(c, "The celebration", M, y)
    y -= 30
    y = draw_title(c, "Today's Doctors", M, y, 310, 31)
    y -= 4
    draw_text(c, "Hana and Ruth are the reason the boat is leaving the dock with this much ceremony. The assignment is simple: celebrate them well, keep the day easy, and get the group photos before anyone gets lake-hair too serious.", M, y, 292, "Helvetica", 11.2, 15, MUTED)

    doc_crop = crop_image(DOCTORS, "doctors_pdf.jpg", (680, 760))
    c.drawImage(ImageReader(doc_crop), 362, H - 388, 206, 244, mask="auto")
    rounded(c, 362, H - 430, 206, 42, colors.white)
    draw_text(c, "The guests of honor. Keep this energy on the boat.", 374, H - 407, 182, "Helvetica-Bold", 9.5, 12, INK)

    rounded(c, M, 278, W - 2 * M, 126, colors.white)
    draw_title(c, "Captain's Welcome", M + 18, 372, 230, 24)
    draw_text(c, "Welcome aboard. Today is for sunshine, lake air, ridiculous photos, responsible drinks, and giving Drs. Hana and Ruth a sendoff that feels like Seattle showed up personally.", M + 18, 340, W - 2 * M - 36, "Helvetica", 11, 14, MUTED)
    x = M + 18
    for chip in ["Captain: Mintay", "Doctors: Hana + Ruth", "Dress code: Boat cute"]:
        x = draw_chip(c, chip, x, 297)

    rounded(c, M, 112, 250, 120, colors.white)
    draw_title(c, "Toast Moment", M + 16, 198, 210, 21)
    draw_text(c, "Near Leschi, pause for a quick toast: one favorite memory, one future wish, and one official doctor-behavior compliment.", M + 16, 169, 216, "Helvetica", 10.2, 13.5, MUTED)

    rounded(c, W - M - 250, 112, 250, 120, colors.white)
    draw_title(c, "Tiny Lake Hint", W - M - 234, 198, 210, 21)
    draw_text(c, "During the Leschi window, a small ripple may appear in the plan. No spoilers. Stay reachable and look alive.", W - M - 234, 169, 216, "Helvetica", 10.2, 13.5, MUTED)
    footer(c, 2)


def draw_itinerary_page(c):
    c.setFillColor(FOAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - 58
    draw_label(c, "Timing follows the live route map", M, y)
    y -= 30
    draw_title(c, "Boat Day Itinerary", M, y, W - 2 * M, 31)

    items = [
        ("10:45 AM", "Depart Fishermen's Terminal", "Cast off from Ballard and head east through Salmon Bay, Fremont Cut, Lake Union, Portage Bay, and the Montlake Cut."),
        ("10:45 AM - 1:45 PM", "Outbound scenic ride", "Relaxed water-only route toward Lake Washington and Leschi, with slow/no-wake areas baked into timing."),
        ("1:45 PM", "Dock near BluWater Bistro / Leschi", "Main mid-day stop. Keep bags tidy, phones close, and the group coordinated around the dock area."),
        ("1:50 - 3:00 PM", "Starbucks walk and meeting window", "Quick walk across Lakeside Ave for the meeting, then back to the dock. This is the only land segment."),
        ("2:30 - 3:30 PM", "Stevie's lake-window", "Keep this flexible and coy. A small water-side cameo may line up near Leschi, so keep one eye on the wake and one eye on the group chat."),
        ("3:30 - 7:00 PM", "Lake Washington celebration hangout", "Main party block: cruise, snack, take photos, toast the doctors, and float only if conditions and captain are comfortable."),
        ("7:30 - 8:30 PM", "Inbound run to Fishermen's Terminal", "Return via Union Bay, Montlake Cut, Lake Union, Fremont Cut, Ship Canal, and Salmon Bay."),
        ("8:30 PM", "Boat returned", "Unload personal items, collect trash, thank the captain, and leave the boat clean."),
    ]
    y = H - 142
    for time, title, body in items:
        h = 64
        rounded(c, M, y - h + 10, W - 2 * M, h, colors.white)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(M + 14, y - 15, time)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 12.3)
        c.drawString(M + 132, y - 12, title)
        draw_text(c, body, M + 132, y - 29, W - 2 * M - 148, "Helvetica", 9.4, 11.7, MUTED)
        y -= 72

    footer(c, 3)


def draw_weather_page(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - 60
    draw_label(c, "Last checked May 27, 2026, evening PDT", M, y)
    y -= 30
    draw_title(c, "Weather Snapshot", M, y, 330, 31)

    rounded(c, M, 482, 180, 190, BLUE, colors.Color(0, 0, 0, alpha=0))
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(M + 90, 628, "THURSDAY")
    c.setFont("Helvetica-Bold", 58)
    c.drawCentredString(M + 90, 562, "78")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(M + 90, 532, "SUNNY HIGH")

    draw_title(c, "Warm, bright, hoodie-at-night friendly.", 250, 646, 300, 22)
    draw_text(c, "NWS forecast for Downtown Seattle calls for sunny conditions with a high near 78 and calm wind becoming northwest around 6 mph in the afternoon. The broader Seattle forecast says highs in the mid 70s to lower 80s, with light wind becoming northwest around 10 mph. Thursday night brings more clouds and a small late-night rain chance after the boat is back.", 250, 596, 300, "Helvetica", 10.5, 13.8, MUTED)

    draw_link_card(c, "NWS Seattle forecast", "https://forecast.weather.gov/MapClick.php?lat=47.6062095&lon=-122.3320708", M, 330, W - 2 * M, 94)
    draw_link_card(c, "NWS Seattle zone forecast", "https://marine.weather.gov/MapClick.php?zoneid=WAZ315", M, 220, W - 2 * M, 94)
    draw_link_card(c, "Printable PDF", PDF_URL, M, 110, W - 2 * M, 94)
    footer(c, 4)


def draw_packing_page(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - 60
    draw_label(c, "Built for 8 to 12 people", M, y)
    y -= 30
    draw_title(c, "What To Bring", M, y, W - 2 * M, 31)
    draw_text(c, "Party-core but practical. Keep snacks light because Leschi has food and restock options during the meeting window.", M, H - 120, W - 2 * M, "Helvetica", 10.8, 14, MUTED)

    col_w = (W - 2 * M - 24) / 3
    sections = [
        ("Drinks + Ice", ["4-6 bags ice", "2-3 cases seltzers", "1-2 bottles tequila", "Mixers, limes, sparkling water", "Red Solo cups and a marker", "Plenty of water bottles", "Electrolytes or Liquid I.V."]),
        ("Easy Food", ["Chips, fruit, crackers, popcorn", "Wraps, sliders, or sandwiches", "Paper towels and napkins", "Trash bags", "Cooler space for drinks first", "Light restock plan around Leschi"]),
        ("Boat Comfort", ["Sunscreen and extra sunscreen", "Sunglasses, hats, towel", "Swimsuit or splash-safe clothes", "Light hoodie for the ride back", "Phone charger or battery pack", "Speaker and downloaded playlist", "Dry bag or zipper bags for phones"]),
    ]
    for idx, (title, items) in enumerate(sections):
        x = M + idx * (col_w + 12)
        rounded(c, x, 296, col_w, 342, colors.white)
        draw_title(c, title, x + 14, 604, col_w - 28, 18)
        draw_list(c, items, x + 14, 572, col_w - 28, 9.2, 12.2, INK)

    rounded(c, M, 92, W - 2 * M, 154, colors.white)
    draw_title(c, "Leschi Food + Restock", M + 16, 212, 300, 22)
    draw_text(c, "Nearby options while the boat is waiting near BluWater. Check hours, availability, and status before relying on any single stop.", M + 16, 181, W - 2 * M - 32, "Helvetica", 10.2, 13, MUTED)
    restock = "BluWater Bistro | Leschi Market | Pablo y Pablo status check | Daniel's Broiler | Starbucks Leschi"
    draw_text(c, restock, M + 16, 136, W - 2 * M - 32, "Helvetica-Bold", 10.2, 13, INK)
    footer(c, 5)


def draw_fun_page(c):
    c.setFillColor(DEEP)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    y = H - 60
    draw_label(c, "Tiny prompts, big memories", M, y, AQUA)
    y -= 30
    draw_title(c, "Fun Assignments", M, y, W - 2 * M, 31, colors.white)

    col_w = (W - 2 * M - 24) / 3
    sections = [
        ("Photo Checklist", ["Doctors in gowns", "Captain + doctors", "Dock arrival", "Lake Washington group photo", "Sunset return photo", "Cheers photo with Seattle/Lake Washington behind it"]),
        ("Boat Day Awards", ["Best boat-day fit", "MVP snack bringer", "Playlist captain", "Most likely to become a lake person"]),
        ("Safety Reminders", ["Boat operator stays sober", "Use cans or plastic, not glass", "Drink water throughout the day", "Keep walking areas clear", "Respect slow/no-wake zones and docks"]),
    ]
    for idx, (title, items) in enumerate(sections):
        x = M + idx * (col_w + 12)
        rounded(c, x, 348, col_w, 292, colors.Color(1, 1, 1, alpha=0.08), colors.Color(1, 1, 1, alpha=0.18))
        draw_title(c, title, x + 14, 606, col_w - 28, 18, colors.white)
        draw_list(c, items, x + 14, 574, col_w - 28, 9.1, 12.2, colors.Color(1, 1, 1, alpha=0.82))

    rounded(c, M, 96, W - 2 * M, 192, colors.white)
    draw_title(c, "Group Text Copy", M + 16, 254, 260, 22)
    body = "Anchors Aweigh: A Lake Washington Sendoff for Drs. Hana & Ruth\n\nBoat day is Thursday, May 28. Captain Mintay has the live route map, itinerary, packing list, weather snapshot, Leschi restock links, and PDF here:\n" + ITINERARY_URL + "\n\nBring sunscreen, sunglasses, a light hoodie, water, electrolytes, red Solo cups, ice, seltzers, tequila/mixers, and light snacks. Keep phones charged for photos and tiny lake surprises."
    draw_text(c, body, M + 16, 222, W - 2 * M - 32, "Helvetica", 9.5, 12.2, MUTED)
    footer(c, 6)


def build():
    c = canvas.Canvas(str(PDF_ROOT), pagesize=letter)
    c.setTitle("Anchors Aweigh - A Lake Washington Sendoff for Drs. Hana & Ruth")
    draw_cover(c)
    c.showPage()
    draw_page_two(c)
    c.showPage()
    draw_itinerary_page(c)
    c.showPage()
    draw_weather_page(c)
    c.showPage()
    draw_packing_page(c)
    c.showPage()
    draw_fun_page(c)
    c.save()

    PDF_OUTPUT.write_bytes(PDF_ROOT.read_bytes())
    reader = PdfReader(str(PDF_ROOT))
    print(f"Wrote {PDF_ROOT} ({len(reader.pages)} pages)")
    print(f"Copied {PDF_OUTPUT}")


if __name__ == "__main__":
    build()
