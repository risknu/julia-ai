from __future__ import annotations

from PIL import ImageFont, Image, ImageDraw

from io import BytesIO
import requests

def demotivator_render(image_url: str = None, text: str = None) -> BytesIO:
    template = Image.open('resources/template.jpg')
    response = requests.get(image_url)

    mem = Image.open(BytesIO(response.content)).convert('RGBA')

    width, height = 610, 569

    resized_mem = mem.resize((width, height), Image.ANTIALIAS)

    text_position, text_color = (0, 0), (266,0,0)
    strip_width, strip_height = 700, 1300
    font_width = 60
    if len(text) >= 25:
        font_width = 50

    background = Image.new('RGB', (strip_width, strip_height))
    draw = ImageDraw.Draw(template)
    if '\n' in text:  
        split_offers = text.split('\n')
        for i in range(2):
            if i == 1:
                strip_height += 110
                font_width -= 20
            font = ImageFont.truetype("resources/fonts/demotivator.ttf", font_width) 
            text_width, text_height = draw.textsize(split_offers[i], font)
            position = ((strip_width-text_width)/2,(strip_height-text_height)/2)
            draw.text(position, split_offers[i], font=font)
    else:
        font = ImageFont.truetype("resources/fonts/demotivator.ttf", font_width)
        text_width, text_height = draw.textsize(text, font)
        strip_height = 1330
        position = ((strip_width-text_width)/2,(strip_height-text_height)/2)
        draw.text(position, text, font=font)

    template.paste(resized_mem, (54, 32),  resized_mem)

    image_bytesio = BytesIO()
    template.save(image_bytesio, format='PNG')
    image_bytesio.seek(0)
    return image_bytesio
