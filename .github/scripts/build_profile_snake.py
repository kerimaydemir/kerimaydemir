from pathlib import Path
import sys

OUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
OUT_DIR.mkdir(parents=True, exist_ok=True)

WEEKS = 53
DAYS = 7
CELL = 12
STEP = 16
X0 = 2
Y0 = 2

active = set()
for col in range(10, 16):
    for row in [2, 3, 4, 5, 6]:
        active.add((col, row))
for col in range(20, 25):
    for row in [1, 2, 3, 5, 6]:
        active.add((col, row))
for col in range(34, 39):
    for row in [0, 1, 2, 3, 4]:
        active.add((col, row))
for col in range(45, 52):
    for row in [1, 2, 3, 4, 5]:
        active.add((col, row))

active_order = sorted(active, key=lambda pos: (pos[0], pos[1]))[:75]
active = set(active_order)

route = []
seen = set()
travel_cols = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    16, 17, 18, 19,
    25, 26, 27, 28, 29, 30, 31, 32, 33,
    39, 40, 41, 42, 43, 44, 52,
}

for col in range(WEEKS):
    rows = range(DAYS) if col % 2 == 0 else range(DAYS - 1, -1, -1)
    for row in rows:
        if (col, row) in active:
            route.append((col, row))
            seen.add((col, row))
        elif col in travel_cols and row in ([0, 3, 6] if col % 2 == 0 else [6, 3, 0]):
            route.append((col, row))

for cell in active_order:
    if cell not in seen:
        route.append(cell)


def xy(cell):
    col, row = cell
    return X0 + col * STEP, Y0 + row * STEP


def pct(index, total):
    return round(index / max(1, total - 1) * 100, 2)


route_xy = [xy(cell) for cell in route]
first = route_xy[0]
hit_index = {}
for index, cell in enumerate(route):
    if cell in active and cell not in hit_index:
        hit_index[cell] = index

levels = ["c1", "c2", "c3", "c4"]


def route_keyframes(name, delay_steps, visible_after_pct):
    items = []
    total = len(route_xy) + delay_steps
    for index in range(total):
        progress = pct(index, total - 1)
        if index < delay_steps:
            x = first[0] - STEP * (delay_steps - index)
            y = first[1]
            opacity = 0 if progress < visible_after_pct else 1
        else:
            x, y = route_xy[index - delay_steps]
            opacity = 1
        items.append(f"{progress}%{{transform:translate({x}px,{y}px);opacity:{opacity}}}")
    return f"@keyframes {name}" + "{" + "".join(items) + "}"


def cell_keyframes(name, level, hit_at):
    progress = pct(hit_at, len(route_xy) - 1)
    before = max(0, round(progress - 0.08, 2))
    after = min(100, round(progress + 0.08, 2))
    return (
        f"@keyframes {name}"
        + "{"
        + f"0%,{before}%{{fill:var(--{level})}}{after}%,100%{{fill:var(--ce)}}"
        + "}"
    )


styles = [
    ":root{--cb:#1b1f230a;--cs:#7c3aed;--ce:#161b22;--c1:#01311f;--c2:#034525;--c3:#0f6d31;--c4:#00c647}",
    ".c{shape-rendering:geometricPrecision;fill:var(--ce);stroke-width:1px;stroke:var(--cb);width:12px;height:12px}",
    ".s{shape-rendering:geometricPrecision;fill:var(--cs);animation:move 28000ms linear infinite}",
]

cell_classes = {}
for index, cell in enumerate(active_order):
    level = levels[(cell[0] + cell[1]) % len(levels)]
    class_name = f"e{index}"
    cell_classes[cell] = class_name
    styles.append(cell_keyframes(class_name, level, hit_index[cell]))
    styles.append(f".c.{class_name}" + "{" + f"fill:var(--{level});animation:{class_name} 28000ms linear infinite" + "}")

for index in range(16):
    class_name = f"s{index}"
    visible_after = min(70, index * 3.1)
    styles.append(route_keyframes(class_name, index, visible_after))
    opacity = round(max(0.45, 1 - index * 0.035), 2)
    styles.append(f".s.{class_name}" + "{" + f"animation-name:{class_name};opacity:{opacity}" + "}")

rects = []
for col in range(WEEKS):
    for row in range(DAYS):
        x, y = xy((col, row))
        class_name = cell_classes.get((col, row))
        class_attr = f"c {class_name}" if class_name else "c"
        rects.append(f'<rect class="{class_attr}" x="{x}" y="{y}" rx="2" ry="2"/>')

snake = []
for index in range(16):
    size = max(8.4, 14.8 - index * 0.28)
    offset = round((16 - size) / 2, 1)
    radius = round(size / 3.2, 1)
    snake.append(
        f'<rect class="s s{index}" x="{offset}" y="{offset}" width="{size:.1f}" height="{size:.1f}" rx="{radius}" ry="{radius}"/>'
    )

svg = (
    '<svg viewBox="-16 -32 880 192" width="880" height="192" xmlns="http://www.w3.org/2000/svg">'
    "<desc>Animated contribution snake with amplified cells</desc>"
    "<style>"
    + "".join(styles)
    + "</style>"
    + "".join(rects)
    + "".join(snake)
    + "</svg>"
)

for name in ["github-snake.svg", "github-snake-dark.svg"]:
    (OUT_DIR / name).write_text(svg)
