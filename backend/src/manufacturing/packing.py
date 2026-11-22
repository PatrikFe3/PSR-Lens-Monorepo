"""
Shelf packing of part footprints onto printer beds.
"""

import math
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Item:
    key: str
    w: float
    d: float


@dataclass(frozen=True)
class Placed:
    key: str
    plate: int
    x: float
    y: float
    rotated: bool
    w: float
    d: float


class PartTooLarge(ValueError):
    pass


def usable_rect(bed) -> tuple[float, float, float, float]:
    if bed.shape == 'circle':
        half = (bed.width / 2 - bed.margin) / math.sqrt(2)
        c = bed.width / 2
        x0, y0, x1, y1 = c - half, c - half, c + half, c + half
    else:
        x0, y0, x1, y1 = bed.margin, bed.margin, bed.width - bed.margin, bed.depth - bed.margin

    for ex0, ey0, ex1, ey1 in bed.exclusions:
        if ex0 <= x0 and ex1 >= x1 and ey0 <= y0:      # strip along the front edge
            y0 = max(y0, ey1)
        elif ex0 <= x0 and ex1 >= x1 and ey1 >= y1:    # strip along the back edge
            y1 = min(y1, ey0)
        elif ey0 <= y0 and ey1 >= y1 and ex0 <= x0:    # strip along the left edge
            x0 = max(x0, ex1)
        elif ey0 <= y0 and ey1 >= y1 and ex1 >= x1:    # strip along the right edge
            x1 = min(x1, ex0)
        else:
            raise ValueError(f'Exclusion {(ex0, ey0, ex1, ey1)} must span a full bed edge.')

    if x1 <= x0 or y1 <= y0:
        raise ValueError('Bed margins and exclusions leave no usable area.')
    return x0, y0, x1, y1


def _orient(item: Item, W: float, D: float):
    options = [(item.w, item.d, False), (item.d, item.w, True)]
    fitting = [o for o in options if o[0] <= W and o[1] <= D]
    if not fitting:
        raise PartTooLarge(item.key)
    return min(fitting, key=lambda o: o[1])  # shallowest shelf first


@dataclass
class _Shelf:
    height: float
    items: list = field(default_factory=list)
    used: float = 0.0


def _pack(items, W, D, gap) -> list[list[_Shelf]]:
    oriented = sorted(((it, *_orient(it, W, D)) for it in items), key=lambda t: (-t[2], -t[1], t[0].key))
    plates: list[list[_Shelf]] = []
    for item, w, d, rot in oriented:
        entry = (item, w, d, rot)
        for shelves in plates:
            shelf = next((s for s in shelves if d <= s.height and s.used + gap + w <= W), None)
            if shelf:
                shelf.items.append(entry)
                shelf.used += gap + w
                break
            depth = sum(s.height for s in shelves) + gap * len(shelves)
            if depth + d <= D:
                shelves.append(_Shelf(d, [entry], w))
                break
        else:  # no existing plate had room (or there were no plates yet)
            plates.append([_Shelf(d, [entry], w)])

    return plates


def _distribute(total, sizes, gap, mode) -> list[float]:
    free, n = total - sum(sizes), len(sizes)
    if mode == 'compact':
        lead, step = max(0.0, (free - gap * (n - 1)) / 2), gap
    elif free / (n + 1) >= gap:          # spread evenly, margins included
        lead = step = free / (n + 1)
    elif n > 1:                          # not enough room for margins: justify
        lead, step = 0.0, free / (n - 1)
    else:
        lead, step = free / 2, 0.0
    offsets, pos = [], lead
    for size in sizes:
        offsets.append(pos)
        pos += size + step
    return offsets


def layout(items: list[Item], printer, mode: Literal['spread', 'compact'] = 'spread') -> list[Placed]:
    x0, y0, x1, y1 = usable_rect(printer.bed)
    W, D, gap = x1 - x0, y1 - y0, printer.part_spacing
    placed = []
    for index, shelves in enumerate(_pack(items, W, D, gap)):
        ys = _distribute(D, [s.height for s in shelves], gap, mode)
        for shelf, y in zip(shelves, ys):
            xs = _distribute(W, [e[1] for e in shelf.items], gap, mode)
            for (item, w, d, rot), x in zip(shelf.items, xs):
                placed.append(Placed(item.key, index, x0 + x, y0 + y + (shelf.height - d) / 2, rot, w, d))
    return placed