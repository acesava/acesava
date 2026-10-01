#!/usr/bin/env python3
"""Render one continuous monthly contribution landscape.

Monthly heights sum the listed daily records. Missing records are never invented
as zeroes; every supplied date is preserved as metadata within its month.
"""

from __future__ import annotations

import argparse
import colorsys
from datetime import date
from html import escape
import json
from pathlib import Path


def _points(vertices: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in vertices)


def _color(hue: float, value: float = 1.0, saturation: float = .60) -> str:
    return "#" + "".join(f"{round(c * 255):02x}" for c in colorsys.hsv_to_rgb(hue % 1, saturation, value))


def _validated_days(dataset: dict) -> tuple[date, date, dict[date, int]]:
    start = date.fromisoformat(dataset["startDate"])
    end = date.fromisoformat(dataset["endDate"])
    if start > end:
        raise ValueError("Contribution startDate must not follow endDate")
    days: dict[date, int] = {}
    for row in dataset["days"]:
        day = date.fromisoformat(row["date"])
        count = row["contributionCount"]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"Invalid contribution count on {day}: {count!r}")
        if not start <= day <= end:
            raise ValueError(f"Contribution date {day} is outside the stated archive range")
        if day in days:
            raise ValueError(f"Duplicate contribution date: {day}")
        days[day] = count
    if not days:
        raise ValueError("Contribution archive contains no daily records")
    total = dataset["totalContributions"]
    if isinstance(total, bool) or not isinstance(total, int) or total != sum(days.values()):
        raise ValueError("totalContributions must equal the sum of supplied daily counts")
    return start, end, days


def render_landscape(dataset: dict, output_path: Path, mobile: bool = False) -> None:
    """Write a self-contained crystal panorama, one height-scaled gem per month."""
    start, end, days = _validated_days(dataset)
    total = sum(days.values())
    months: list[date] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        months.append(cursor)
        cursor = date(cursor.year + (cursor.month == 12), cursor.month % 12 + 1, 1)
    by_month = {month: [] for month in months}
    for day, count in sorted(days.items()):
        by_month[date(day.year, day.month, 1)].append((day, count))
    month_totals = {month: sum(count for _, count in records) for month, records in by_month.items()}
    peak = max(month_totals.values(), default=0)
    width, height = (600, 480) if mobile else (1200, 530)
    margin = 28 if mobile else 40
    title = str(dataset.get("title") or "Combined Account Contribution topography")
    desc = (
        f"{title}. {start:%d %B %Y} to {end:%d %B %Y}. "
        f"{total:,} contributions from {len(days):,} listed dates. "
        "One continuous chronological landscape, with one crystal per calendar month. "
        "Height is linear in the sum of that month's listed daily contributions. "
        f"The tallest month contains {peak:,} listed contributions. "
        "Months without listed records remain gaps, not confirmed zeroes. "
        "The final month is partial when the end date is before month end."
    )
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="landscape-title landscape-desc">
<title id="landscape-title">{escape(title)}</title>
<desc id="landscape-desc">{escape(desc)}</desc>
<defs>
  <linearGradient id="spectrum"><stop stop-color="#f4aa85"/><stop offset=".2" stop-color="#e1dd8b"/><stop offset=".4" stop-color="#91e4b0"/><stop offset=".61" stop-color="#81d1e2"/><stop offset=".8" stop-color="#92aceb"/><stop offset="1" stop-color="#d7a5e4"/></linearGradient>
  <linearGradient id="depth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#163e31"/><stop offset="1" stop-color="#020908"/></linearGradient>
  <radialGradient id="halo"><stop stop-color="#24765a" stop-opacity=".2"/><stop offset="1" stop-color="#020807" stop-opacity="0"/></radialGradient>
  <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 1H4" stroke="#bcf3d7" stroke-opacity=".025"/></pattern>
  <filter id="peak-glow" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="2"/></filter>
</defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}} polygon{{stroke-width:.45}}</style>
<rect width="{width}" height="{height}" fill="#020807"/>
<rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="#476d5c"/>
<rect x="7" y="7" width="{width-14}" height="{height-14}" fill="none" stroke="#18372c"/>
<path d="M7 31V7H31 M{width-31} 7H{width-7}V31 M{width-7} {height-31}V{height-7}H{width-31} M31 {height-7}H7V{height-31}" fill="none" stroke="#a4d4ba" stroke-width="1.2"/>
''']

    def text(x: float, y: float, value: object, size: int, color: str = "#b8dfc9", attributes: str = "") -> None:
        svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}" {attributes}>{escape(str(value))}</text>')

    def polygon(vertices: list[tuple[float, float]], fill: str, stroke: str = "none", opacity: float = 1) -> None:
        extra = f' opacity="{opacity:g}"' if opacity != 1 else ""
        svg.append(f'<polygon points="{_points(vertices)}" fill="{fill}" stroke="{stroke}"{extra}/>')

    text(margin, 53 if mobile else 62, "COMBINED ACCOUNT", 29 if mobile else 34, "#c0ead0", 'letter-spacing="1.2"')
    text(margin, 87 if mobile else 99, "CONTRIBUTION TOPOGRAPHY", 23 if mobile else 28, "#accfbd", 'letter-spacing=".5"')
    if mobile:
        text(margin, 137, f"{total:,}", 36, "#d8f1df", 'letter-spacing="1"')
        text(margin + 145, 132, "CONTRIBUTIONS", 15, "#90b7a0", 'letter-spacing="1"')
    else:
        text(width - margin, 68, f"{total:,}", 50, "#d8f1df", 'text-anchor="end" letter-spacing="2"')
        text(width - margin, 98, "CONTRIBUTIONS", 15, "#90b7a0", 'text-anchor="end" letter-spacing="1.8"')
    header_rule = 155 if mobile else 122
    svg.append(f'<path d="M{margin} {header_rule}H{width-margin}" stroke="#284c3b"/>')

    # One time axis spans the complete archive; the shallow second dimension is
    # decorative perspective only, not another aggregation or another period.
    ox, oy = (38.0, 342.0) if mobile else (72.0, 376.0)
    ux, uy = (12.0, 30.0) if mobile else (20.0, 46.0)
    vx = (width - 2 * ox - ux) / len(months)
    vy = (-32.0 if mobile else -64.0) / len(months)
    max_height = 118.0 if mobile else 180.0

    def point(month: float, depth: float, value_height: float = 0) -> tuple[float, float]:
        return ox + month * vx + depth * ux, oy + month * vy + depth * uy - value_height

    a, b, c, d = point(0, 0), point(len(months), 0), point(len(months), 1), point(0, 1)
    lower = lambda p: (p[0], p[1] + (9 if mobile else 14))
    svg.append(f'<ellipse cx="{width/2:g}" cy="{oy-32:g}" rx="{width*.46:g}" ry="{90 if mobile else 150}" fill="url(#halo)"/>')
    polygon([a, b, c, d], "#04120e", "#3f6953")
    polygon([d, c, lower(c), lower(d)], "url(#depth)", "#32573f")
    polygon([b, c, lower(c), lower(b)], "#0b2118", "#36593f")
    for mi in range(len(months) + 1):
        p, q = point(mi, 0), point(mi, 1)
        svg.append(f'<path d="M{p[0]:.2f},{p[1]:.2f}L{q[0]:.2f},{q[1]:.2f}" stroke="#285039" stroke-width=".4"/>')
    for depth in (.25, .5, .75):
        p, q = point(0, depth), point(len(months), depth)
        svg.append(f'<path d="M{p[0]:.2f},{p[1]:.2f}L{q[0]:.2f},{q[1]:.2f}" stroke="#204a36" stroke-width=".35"/>')
    for depth, opacity in ((1, .7), (5, .3), (9, .15)):
        svg.append(f'<path d="M{d[0]:.2f},{d[1]+depth:.2f}L{c[0]:.2f},{c[1]+depth:.2f}" stroke="url(#spectrum)" stroke-width=".8" opacity="{opacity}"/>')

    # Draw the far (latest) end first so nearer crystals occlude it correctly.
    for mi in reversed(range(len(months))):
        month = months[mi]
        records = by_month[month]
        month_total = month_totals[month]
        month_key = month.strftime("%Y-%m")
        label = f"{month:%B %Y}: {month_total:,} listed contributions across {len(records)} listed dates" if records else f"{month:%B %Y}: no listed records"
        total_attribute = f' data-total="{month_total}"' if records else ""
        svg.append(f'<g data-month="{month_key}"{total_attribute} data-listed-dates="{len(records)}"><title>{escape(label)}</title>')
        for day, count in records:
            svg.append(f'<g data-date="{day}" data-count="{count}"><title>{day}: {count} contribution{"s" if count != 1 else ""}</title></g>')
        if records:
            base = [point(mi + .1, .35), point(mi + .9, .35), point(mi + .9, .65), point(mi + .1, .65)]
            if month_total == 0:
                polygon(base, "#183d2b", "#547b5f")
            else:
                crystal_height = max_height * month_total / peak
                shoulder_height = crystal_height * .66
                shoulders = [(x, y - shoulder_height) for x, y in base]
                tip = point(mi + .50, .49, crystal_height)
                hue = .045 + .745 * (mi + .5) / len(months)
                polygon([base[3], base[2], shoulders[2], shoulders[3]], _color(hue, .34, .56), _color(hue, .54, .46))
                polygon([base[1], base[2], shoulders[2], shoulders[1]], _color(hue, .22, .5), _color(hue, .39, .4))
                polygon([shoulders[0], shoulders[1], tip], _color(hue, .65, .37), _color(hue, .82, .30))
                polygon([shoulders[1], shoulders[2], tip], _color(hue, .48, .54), _color(hue, .64, .42))
                polygon([shoulders[2], shoulders[3], tip], _color(hue, .86, .22), _color(hue, .98, .17))
                polygon([shoulders[3], shoulders[0], tip], _color(hue, .66, .35), _color(hue, .85, .25))
                svg.append(f'<path d="M{tip[0]:.2f},{tip[1]:.2f}L{shoulders[3][0]:.2f},{shoulders[3][1]:.2f}" stroke="{_color(hue, .98, .14)}" stroke-width=".7"/>')
                if month_total >= peak * .75:
                    svg.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r="2.1" fill="{_color(hue, 1, .17)}" opacity=".55" filter="url(#peak-glow)"/>')
                    svg.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r=".9" fill="#eff7e3"/>')
        svg.append('</g>')

    year_markers = [(0, start.year)] + [(i, m.year) for i, m in enumerate(months) if m.month == 1 and i]
    for mi, year in year_markers:
        if mobile and year != start.year and year != end.year and year % 2:
            continue
        p = point(mi, 1)
        svg.append(f'<path d="M{p[0]:.2f},{p[1]+14:.2f}v5" stroke="#668f75"/>')
        text(p[0], p[1] + (34 if mobile else 37), year, 15 if mobile else 17, "#9bbcaa", 'letter-spacing=".5"')

    footer_line = 410 if mobile else 474
    svg.append(f'<path d="M{margin} {footer_line}H{width-margin}" stroke="#284c3b"/>')
    text(margin, footer_line + 26, "LISTED CONTRIBUTIONS BY MONTH", 15 if mobile else 17, "#abccb8", 'letter-spacing=".5"')
    date_label = f"{start:%b %Y} — {end:%d %b %Y}".upper()
    if mobile:
        text(margin, footer_line + 49, date_label, 14, "#8ba995", 'letter-spacing=".7"')
    else:
        text(width - margin, footer_line + 26, date_label, 15, "#8ba995", 'text-anchor="end" letter-spacing=".7"')
    svg.append(f'<rect x="8" y="8" width="{width-16}" height="{height-16}" fill="url(#scanlines)" pointer-events="none"/>\n</svg>')
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Normalized contribution archive JSON")
    parser.add_argument("output", type=Path, help="Output SVG file")
    parser.add_argument("--mobile", action="store_true", help="Use the narrow-screen panorama layout")
    args = parser.parse_args()
    render_landscape(json.loads(args.dataset.read_text(encoding="utf-8")), args.output, mobile=args.mobile)


if __name__ == "__main__":
    main()
