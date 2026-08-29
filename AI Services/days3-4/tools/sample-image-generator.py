from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_PATH = Path(__file__).parent.parent / "generated" / "sample-ticket.png"

# The known-good text. Textract should return these lines nearly verbatim --
# that is the whole point of controlling the input.
TICKET_LINES = [
    "SUPPORT TICKET #4471",
    "",
    "Customer: Northwind Trading Co.",
    "Opened:   2026-08-24  09:14 UTC",
    "Product:  Checkout Service",
    "",
    "Description:",
    "Payments fail at the confirmation step for all",
    "customers using saved cards. Started after the",
    "Tuesday release. We are losing orders hourly.",
    "",
    "Contact: ops@northwind-trading.example",
]


def _load_font(size: int) -> ImageFont.ImageFont:
    """Get a legible font, whatever this machine happens to have."""
    for candidate in ("DejaVuSansMono.ttf", "consola.ttf", "cour.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    # Pillow >= 10.1 can scale the built-in font; older versions cannot.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def generate(output_path: Path = OUTPUT_PATH) -> Path:
    width, height = 900, 620
    margin, line_height = 50, 40

    # Black on white at high contrast. OCR accuracy is far more sensitive to
    # contrast and resolution than to anything else, so this is the setting
    # that decides whether the demo looks impressive or broken.
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    title_font = _load_font(30)
    body_font = _load_font(24)

    y = margin
    for index, line in enumerate(TICKET_LINES):
        draw.text((margin, y), line, fill="black", font=title_font if index == 0 else body_font)
        y += line_height

    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="black", width=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


if __name__ == "__main__":
    path = generate()
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
    print("Upload this file to POST /api/v1/documents/analyze in Postman.")