#!/usr/bin/env python3
"""Build A4 PDF of business-card-sized QR cards for Karşıyaka Girne Anaokulu."""
import csv, io, os, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

BASE_URL = "https://oguzcagala.github.io/kga2026/?v="
MAPPING_CSV = sys.argv[1] if len(sys.argv) > 1 else "/Users/oguzcagala/Desktop/QR/mapping.csv"
OUT_PDF = sys.argv[2] if len(sys.argv) > 2 else "/Users/oguzcagala/Desktop/QR/karts.pdf"

# Register Arial for Turkish glyph coverage
pdfmetrics.registerFont(TTFont("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))

# Layout
PAGE_W, PAGE_H = A4              # 210 x 297 mm
CARD_W = 85 * mm                 # business-card size
CARD_H = 55 * mm
COLS, ROWS = 2, 5                # 10 cards/page → 4 pages
GUTTER_X = 4 * mm
GUTTER_Y = 4 * mm

GRID_W = COLS * CARD_W + (COLS - 1) * GUTTER_X
GRID_H = ROWS * CARD_H + (ROWS - 1) * GUTTER_Y
MARGIN_X = (PAGE_W - GRID_W) / 2
MARGIN_Y = (PAGE_H - GRID_H) / 2

PINK = HexColor("#d4577a")
DARK = HexColor("#5a2a3b")
SOFT = HexColor("#f9d6e0")

def make_qr_png(url):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return ImageReader(bio)

def draw_card(c, x, y, qr_img, seq):
    # Cut-line border (dashed, light)
    c.saveState()
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.4)
    c.setDash(2, 2)
    c.rect(x, y, CARD_W, CARD_H)
    c.restoreState()

    # School name top
    c.setFillColor(PINK)
    c.setFont("Arial-Bold", 8)
    c.drawCentredString(x + CARD_W/2, y + CARD_H - 6*mm, "KARŞIYAKA GİRNE ANAOKULU")

    # "Canım Anneme ♥" subtitle
    c.setFillColor(DARK)
    c.setFont("Arial-Bold", 10)
    c.drawCentredString(x + CARD_W/2, y + CARD_H - 11*mm, "Canım Anneme  ♥")

    # QR (square, centered horizontally)
    qr_size = 26 * mm
    qr_x = x + (CARD_W - qr_size) / 2
    qr_y = y + 12*mm
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size)

    # "Çocuğumuz: ____" line at bottom-left
    c.setFillColor(DARK)
    c.setFont("Arial", 8)
    label_y = y + 6*mm
    c.drawString(x + 5*mm, label_y, "Çocuğumuz:")
    # underline for handwritten name
    c.setStrokeColor(DARK)
    c.setLineWidth(0.5)
    c.setDash()
    c.line(x + 22*mm, label_y - 1, x + CARD_W - 5*mm, label_y - 1)

    # Sequence number tiny in corner (helps match to mapping CSV)
    c.setFillColor(HexColor("#b08090"))
    c.setFont("Arial", 6)
    c.drawRightString(x + CARD_W - 3*mm, y + CARD_H - 4*mm, f"#{seq:02d}")

    # Tagline below QR
    c.setFillColor(PINK)
    c.setFont("Arial", 7)
    c.drawCentredString(x + CARD_W/2, y + 10*mm, "Anneler Günün Kutlu Olsun")

def main():
    rows = list(csv.DictReader(open(MAPPING_CSV)))
    c = canvas.Canvas(OUT_PDF, pagesize=A4)

    per_page = COLS * ROWS
    for i, row in enumerate(rows):
        if i > 0 and i % per_page == 0:
            c.showPage()

        slot = i % per_page
        col = slot % COLS
        # rows go top-to-bottom; PDF y grows up
        row_idx = slot // COLS
        x = MARGIN_X + col * (CARD_W + GUTTER_X)
        y = PAGE_H - MARGIN_Y - (row_idx + 1) * CARD_H - row_idx * GUTTER_Y

        url = BASE_URL + row["uuid"]
        qr_img = make_qr_png(url)
        draw_card(c, x, y, qr_img, int(row["seq"]))

    c.save()
    print(f"OK: {OUT_PDF}  ({len(rows)} cards, {(len(rows)+per_page-1)//per_page} pages)")

if __name__ == "__main__":
    main()
