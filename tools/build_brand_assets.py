"""Rebuild the local SVG/PNG/ICO/ICNS logo. Run from any directory with Pillow."""
from pathlib import Path

from PIL import Image, ImageDraw

DESTINATION = Path(__file__).resolve().parents[1] / 'soskuska/assets/brand'
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)
VIOLET = '#7043C1'
LEFT = ((112, 148), (166, 132), (205, 148), (244, 174),
        (244, 366), (202, 338), (162, 324), (112, 338))
RIGHT = ((268, 174), (307, 148), (346, 132), (400, 148),
         (400, 338), (350, 324), (310, 338), (268, 366))
CHECK = ((300, 252), (327, 280), (375, 218))


def page_path(points):
    a, b, c, d, e, f, g, h = points
    def pair(p):
        return f'{p[0]} {p[1]}'
    return f'M{pair(a)} C{pair(b)} {pair(c)} {pair(d)} L{pair(e)} C{pair(f)} {pair(g)} {pair(h)} Z'


def curve(a, b, c, d):
    for i in range(65):
        t = i / 64
        yield tuple((1-t)**3*a[j] + 3*(1-t)**2*t*b[j] + 3*(1-t)*t*t*c[j] + t**3*d[j] for j in (0, 1))


def build(destination=DESTINATION):
    destination.mkdir(parents=True, exist_ok=True)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-labelledby="title">
  <title id="title">SOSkúška — open book and check mark</title>
  <rect width="512" height="512" rx="112" fill="{VIOLET}"/>
  <path d="{page_path(LEFT)}" fill="#FFFFFF"/>
  <path d="{page_path(RIGHT)}" fill="#EFE7FF"/>
  <path d="M300 252 L327 280 L375 218" fill="none" stroke="{VIOLET}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''
    (destination / 'logo.svg').write_text(svg, encoding='utf-8')
    # Render the same geometry without a browser, fonts or an SVG dependency.
    scale = 4
    canvas = Image.new('RGBA', (512*scale, 512*scale))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((0, 0, 512*scale-1, 512*scale-1), radius=112*scale, fill=VIOLET)
    for points, fill in ((LEFT, '#FFFFFF'), (RIGHT, '#EFE7FF')):
        a, b, c, d, e, f, g, h = points
        polygon = list(curve(a, b, c, d)) + list(curve(e, f, g, h))
        draw.polygon([(round(x*scale), round(y*scale)) for x, y in polygon], fill=fill)
    check = [(x*scale, y*scale) for x, y in CHECK]
    draw.line(check, fill=VIOLET, width=20*scale, joint='curve')
    for x, y in check:
        draw.ellipse((x-10*scale, y-10*scale, x+10*scale, y+10*scale), fill=VIOLET)
    for size in SIZES:
        canvas.resize((size, size), Image.Resampling.LANCZOS).save(destination / f'logo-{size}.png')
    canvas.resize((256, 256), Image.Resampling.LANCZOS).save(
        destination / 'soskuska.ico', sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    canvas.resize((1024, 1024), Image.Resampling.LANCZOS).save(destination / 'soskuska.icns')


if __name__ == '__main__':
    build()
