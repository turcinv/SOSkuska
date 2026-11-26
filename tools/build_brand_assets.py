"""Rebuild the local SVG/PNG/ICO/ICNS logo. Run from any directory with Pillow.

The mark is a cat peeking over an open book on a lavender-to-charcoal app-icon
square.  All geometry lives in the module-level constants below (512 canvas) and
feeds both the hand-authored SVG and the Pillow renderer, so they stay aligned.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

DESTINATION = Path(__file__).resolve().parents[1] / 'soskuska/assets/brand'
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)
CANVAS = 512
RADIUS = 112
SCALE = 4

GRADIENT_TOP = '#8C78CC'
GRADIENT_BOTTOM = '#3B3350'
CAT = '#2B2A34'
INNER_EAR = '#4A4458'
WHITE = '#FFFFFF'
NOSE = '#F7B6CF'
PAGE_LEFT = '#C9B6F2'
PAGE_RIGHT = '#E6DCFB'
SPINE = '#9884D6'
MOTION = '#E6DCFB'

# Head: ellipse (cx, cy, rx, ry) plus two ear triangles (mirrored around x=256).
HEAD = (256, 262, 142, 116)
EAR_LEFT = ((120, 244), (122, 88), (250, 160))
EAR_RIGHT = ((392, 244), (390, 88), (262, 160))
INNER_LEFT = ((144, 214), (146, 128), (208, 168))
INNER_RIGHT = ((368, 214), (366, 128), (304, 168))

# Happy closed eyes: upward arcs (centre x, centre y, radius), stroke width.
EYES = ((204, 252, 24), (308, 252, 24))
EYE_WIDTH = 12
NOSE_BOX = (256, 284, 11, 7)  # cx, cy, rx, ry
# Whiskers: (x0, y0, x1, y1), three per side, starting inside the cheek.
WHISKERS = ((166, 278, 82, 260), (162, 292, 76, 290), (166, 306, 84, 318),
            (346, 278, 430, 260), (350, 292, 436, 290), (346, 306, 428, 318))
WHISKER_WIDTH = 6

# Book: each page is a bezier top edge, straight spine edge, bezier bottom edge.
# Points: top-start, ctrl, ctrl, top-end, bottom-end, ctrl, ctrl, bottom-start.
LEFT = ((88, 326), (150, 312), (210, 322), (252, 346),
        (252, 452), (210, 430), (150, 420), (88, 432))
RIGHT = ((260, 346), (302, 322), (362, 312), (424, 326),
         (424, 432), (362, 420), (302, 430), (260, 452))
SPINE_LINE = (256, 346, 256, 452)
SPINE_WIDTH = 8

# Motion strokes: three short radial dashes top-right (x0, y0, x1, y1).
MOTION_STROKES = tuple(
    (round(256 + r0*math.cos(math.radians(a))), round(262 - r0*math.sin(math.radians(a))),
     round(256 + r1*math.cos(math.radians(a))), round(262 - r1*math.sin(math.radians(a))))
    for a, r0, r1 in ((12, 205, 235), (30, 205, 235), (48, 215, 245)))
MOTION_WIDTH = 14


def pair(p):
    return f'{p[0]} {p[1]}'


def page_path(points):
    a, b, c, d, e, f, g, h = points
    return f'M{pair(a)} C{pair(b)} {pair(c)} {pair(d)} L{pair(e)} C{pair(f)} {pair(g)} {pair(h)} Z'


def poly_path(points):
    return 'M' + ' L'.join(pair(p) for p in points) + ' Z'


def curve(a, b, c, d):
    for i in range(65):
        t = i / 64
        yield tuple((1-t)**3*a[j] + 3*(1-t)**2*t*b[j] + 3*(1-t)*t*t*c[j] + t**3*d[j] for j in (0, 1))


def svg_markup():
    cx, cy, rx, ry = HEAD
    nx, ny, nrx, nry = NOSE_BOX
    eyes = '\n'.join(
        f'    <path d="M{x-r} {y} A{r} {r} 0 0 1 {x+r} {y}"/>' for x, y, r in EYES)
    whiskers = '\n'.join(f'    <path d="M{a} {b} L{c} {d}"/>' for a, b, c, d in WHISKERS)
    motion = '\n'.join(f'    <path d="M{a} {b} L{c} {d}"/>' for a, b, c, d in MOTION_STROKES)
    sx0, sy0, sx1, sy1 = SPINE_LINE
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}" role="img" aria-labelledby="title">
  <title id="title">SOSkúška — cat reading a book</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GRADIENT_TOP}"/>
      <stop offset="1" stop-color="{GRADIENT_BOTTOM}"/>
    </linearGradient>
  </defs>
  <rect width="{CANVAS}" height="{CANVAS}" rx="{RADIUS}" fill="url(#bg)"/>
  <g fill="none" stroke="{MOTION}" stroke-width="{MOTION_WIDTH}" stroke-linecap="round">
{motion}
  </g>
  <path d="{poly_path(EAR_LEFT)}" fill="{CAT}" stroke="{CAT}" stroke-width="16" stroke-linejoin="round"/>
  <path d="{poly_path(EAR_RIGHT)}" fill="{CAT}" stroke="{CAT}" stroke-width="16" stroke-linejoin="round"/>
  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{CAT}"/>
  <path d="{poly_path(INNER_LEFT)}" fill="{INNER_EAR}" stroke="{INNER_EAR}" stroke-width="8" stroke-linejoin="round"/>
  <path d="{poly_path(INNER_RIGHT)}" fill="{INNER_EAR}" stroke="{INNER_EAR}" stroke-width="8" stroke-linejoin="round"/>
  <g fill="none" stroke="{WHITE}" stroke-width="{EYE_WIDTH}" stroke-linecap="round">
{eyes}
  </g>
  <ellipse cx="{nx}" cy="{ny}" rx="{nrx}" ry="{nry}" fill="{NOSE}"/>
  <g fill="none" stroke="{WHITE}" stroke-width="{WHISKER_WIDTH}" stroke-linecap="round" opacity="0.9">
{whiskers}
  </g>
  <path d="{page_path(LEFT)}" fill="{PAGE_LEFT}"/>
  <path d="{page_path(RIGHT)}" fill="{PAGE_RIGHT}"/>
  <path d="M{sx0} {sy0} L{sx1} {sy1}" stroke="{SPINE}" stroke-width="{SPINE_WIDTH}" stroke-linecap="round"/>
</svg>
'''


def _stroke(draw, points, width, fill):
    """Polyline with round caps and joints, in supersampled pixel coordinates."""
    pts = [(x*SCALE, y*SCALE) for x, y in points]
    r = width*SCALE/2
    draw.line(pts, fill=fill, width=round(width*SCALE))
    for x, y in pts:
        draw.ellipse((x-r, y-r, x+r, y+r), fill=fill)


def _poly(draw, points, fill, grow=0):
    """Filled polygon; ``grow`` mimics a round-joined stroke of that half-width."""
    pts = [(x*SCALE, y*SCALE) for x, y in points]
    draw.polygon(pts, fill=fill)
    if grow:
        _stroke(draw, list(points) + [points[0]], grow*2, fill)


def render():
    big = CANVAS * SCALE
    # Gradient filled through a rounded-square mask so the corners stay transparent.
    column = Image.new('RGB', (1, big))
    top = tuple(int(GRADIENT_TOP[i:i+2], 16) for i in (1, 3, 5))
    bottom = tuple(int(GRADIENT_BOTTOM[i:i+2], 16) for i in (1, 3, 5))
    column.putdata([tuple(round(top[k] + (bottom[k]-top[k]) * y/(big-1)) for k in range(3))
                    for y in range(big)])
    gradient = column.resize((big, big), Image.Resampling.NEAREST)
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, big-1, big-1), radius=RADIUS*SCALE, fill=255)
    canvas = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    canvas.paste(gradient, (0, 0), mask)
    draw = ImageDraw.Draw(canvas)

    for x0, y0, x1, y1 in MOTION_STROKES:
        _stroke(draw, ((x0, y0), (x1, y1)), MOTION_WIDTH, MOTION)
    _poly(draw, EAR_LEFT, CAT, grow=8)
    _poly(draw, EAR_RIGHT, CAT, grow=8)
    cx, cy, rx, ry = HEAD
    draw.ellipse(((cx-rx)*SCALE, (cy-ry)*SCALE, (cx+rx)*SCALE, (cy+ry)*SCALE), fill=CAT)
    _poly(draw, INNER_LEFT, INNER_EAR, grow=4)
    _poly(draw, INNER_RIGHT, INNER_EAR, grow=4)
    for x, y, r in EYES:
        arc = [(x + r*math.cos(math.radians(a)), y + r*math.sin(math.radians(a)))
               for a in range(180, 361, 6)]
        _stroke(draw, arc, EYE_WIDTH, WHITE)
    nx, ny, nrx, nry = NOSE_BOX
    draw.ellipse(((nx-nrx)*SCALE, (ny-nry)*SCALE, (nx+nrx)*SCALE, (ny+nry)*SCALE), fill=NOSE)
    whisker = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(whisker)
    for x0, y0, x1, y1 in WHISKERS:
        _stroke(wdraw, ((x0, y0), (x1, y1)), WHISKER_WIDTH, WHITE + 'E6')
    canvas.alpha_composite(whisker)
    draw = ImageDraw.Draw(canvas)
    for points, fill in ((LEFT, PAGE_LEFT), (RIGHT, PAGE_RIGHT)):
        a, b, c, d, e, f, g, h = points
        polygon = list(curve(a, b, c, d)) + list(curve(e, f, g, h))
        draw.polygon([(x*SCALE, y*SCALE) for x, y in polygon], fill=fill)
    x0, y0, x1, y1 = SPINE_LINE
    _stroke(draw, ((x0, y0), (x1, y1)), SPINE_WIDTH, SPINE)
    return canvas


def build(destination=DESTINATION):
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'logo.svg').write_text(svg_markup(), encoding='utf-8')
    canvas = render()
    for size in SIZES:
        canvas.resize((size, size), Image.Resampling.LANCZOS).save(destination / f'logo-{size}.png')
    canvas.resize((256, 256), Image.Resampling.LANCZOS).save(
        destination / 'soskuska.ico', sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    canvas.resize((1024, 1024), Image.Resampling.LANCZOS).save(destination / 'soskuska.icns')


if __name__ == '__main__':
    build()
