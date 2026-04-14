import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def generate_preview(original_file, text="PREVIEW", font_path=None):
    base = Image.open(original_file).convert("RGBA")
    width, height = base.size

    watermark_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_size = max(20, int(width * 0.8))
    h_spacing = int(width * 0.08)
    v_spacing = int(height * 0.08)

    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # tile watermark
    for x in range(0, width, text_width + h_spacing):
        for y in range(0, height, text_height + v_spacing):
            draw.text((x, y), text, fill=(255, 255, 255, 180), font=font)

    # rotate
    rotated = watermark_layer.rotate(35, expand=1)

    # crop center
    rw, rh = rotated.size
    left = (rw - width) // 2
    top = (rh - height) // 2
    rotated_cropped = rotated.crop((left, top, left + width, top + height))

    # merge
    final = Image.alpha_composite(base, rotated_cropped).convert("RGB")

    # save to memory
    buffer = BytesIO()
    final.save(buffer, format="JPEG")
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f"preview_{original_file.name}")