from PIL import Image, ImageDraw, ImageFont
def write_image(message , font_name="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",font_size=50):
    WIDTH, HEIGHT = 640, 480
    image = Image.new("RGB", (WIDTH, HEIGHT), color="white")
    draw = ImageDraw.Draw(image)
    from PIL import ImageFont
    font = ImageFont.truetype(font_name, font_size)
    draw.text((10, 10), message, fill=(0, 0, 0) ,font=font)
    image.save("text_image.png")

