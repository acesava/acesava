#!/usr/bin/env python3
"""Render a contribution archive as precise, faceted annual landscapes.

Only supplied dates receive contribution metadata. Unlisted dates are gaps, not
zeroes. Heights use a shared linear scale across every annual plate.
"""

from __future__ import annotations

import argparse
import calendar
import colorsys
from datetime import date, timedelta
from html import escape
import json
from pathlib import Path


def _points(vertices: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in vertices)


def _color(hue: float, value: float = 1.0, saturation: float = .60) -> str:
    return "#" + "".join(f"{round(c * 255):02x}" for c in colorsys.hsv_to_rgb(hue % 1, saturation, value))


def _anniversary(start: date, year: int) -> date:
    return date(year, start.month, min(start.day, calendar.monthrange(year, start.month)[1]))


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
    """Write the supplied archive as a standalone responsive-profile SVG asset."""
    start, end, days = _validated_days(dataset)
    total = sum(days.values())
    peak = max(days.values(), default=0)
    periods: list[tuple[date, date]] = []
    period_start = start
    while period_start <= end:
        period_end = min(end, _anniversary(start, period_start.year + 1) - timedelta(days=1))
        periods.append((period_start, period_end))
        period_start = period_end + timedelta(days=1)

    width = 600 if mobile else 1200
    columns = 1 if mobile else 2
    margin, gap = (20, 18) if mobile else (28, 20)
    panel_width = (width - margin * 2 - gap * (columns - 1)) / columns
    panel_height = 262 if mobile else 262
    header_height = 203 if mobile else 170
    rows = (len(periods) + columns - 1) // columns
    footer_height = 115 if mobile else 98
    height = header_height + rows * (panel_height + gap) + footer_height
    title = str(dataset.get("title") or "Combined Account Contribution topography")
    desc = (
        f"{title}. {start:%d %B %Y} to {end:%d %B %Y}. "
        f"{total:,} supplied contributions across {len(days):,} listed dates. "
        f"{len(periods)} annual plates, each read from June at left to May at right. "
        f"Crystal height is linear in the daily count on a common scale, from 0 to {peak}. "
        "Unlisted dates remain empty grid gaps; they are not confirmed zero. "
        "This is the profile owner's supplied contribution archive."
    )
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="archive-title archive-desc">
<title id="archive-title">{escape(title)}</title>
<desc id="archive-desc">{escape(desc)}</desc>
<defs>
  <linearGradient id="spectrum"><stop stop-color="#f8a290"/><stop offset=".18" stop-color="#e4d67e"/><stop offset=".36" stop-color="#96e5ad"/><stop offset=".57" stop-color="#78d6dc"/><stop offset=".79" stop-color="#919de7"/><stop offset="1" stop-color="#d6a3df"/></linearGradient>
  <linearGradient id="plate" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#081915"/><stop offset="1" stop-color="#030c0a"/></linearGradient>
  <linearGradient id="depth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#12372d"/><stop offset="1" stop-color="#020908"/></linearGradient>
  <radialGradient id="field-halo"><stop stop-color="#23735a" stop-opacity=".18"/><stop offset="1" stop-color="#020807" stop-opacity="0"/></radialGradient>
  <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 1H4" stroke="#bcf3d7" stroke-opacity=".025"/></pattern>
  <filter id="peak-glow" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="1.8"/></filter>
</defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}} .muted{{fill:#82ac99}} .micro{{fill:#82ac99;font-size:12px;letter-spacing:1.1px}} polygon{{stroke-width:.4}}</style>
<rect width="{width}" height="{height}" fill="#020807"/>
<rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="#466e5c"/>
<rect x="7" y="7" width="{width-14}" height="{height-14}" fill="none" stroke="#152f27"/>
<path d="M7 31V7H31 M{width-31} 7H{width-7}V31 M{width-7} {height-31}V{height-7}H{width-31} M31 {height-7}H7V{height-31}" fill="none" stroke="#acd9c0" stroke-width="1.2"/>
''']

    def text(x: float, y: float, value: object, size: int = 14, color: str = "#b9e4cd", attributes: str = "") -> None:
        svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}" {attributes}>{escape(str(value))}</text>')

    def polygon(vertices: list[tuple[float, float]], fill: str, stroke: str = "none", opacity: float = 1, line_width: float = .4) -> None:
        extras = (f' stroke-width="{line_width:g}"' if line_width != .4 else "") + (f' opacity="{opacity:.2f}"' if opacity != 1 else "")
        svg.append(f'<polygon points="{_points(vertices)}" fill="{fill}" stroke="{stroke}"{extras}/>')

    text(margin + 10, 35, "05 / CONTRIBUTION ARCHIVE", 13, "#86ac98", 'letter-spacing="2"')
    text(margin + 10, 73, "COMBINED ACCOUNT", 32 if mobile else 34, "#c0efd3", 'letter-spacing="1.1"')
    text(margin + 10, 107, "CONTRIBUTION TOPOGRAPHY", 24 if mobile else 28, "#b1d7c5", 'letter-spacing=".5"')
    if mobile:
        text(margin + 10, 154, f"{total:,}", 38, "#d6f4df", 'letter-spacing="1"')
        text(margin + 140, 149, "CONTRIBUTIONS", 16, "#8ebaa3", 'letter-spacing="1"')
        text(width - margin - 10, 176, f"{start:%Y}–{end:%Y}", 14, "#91aeaa", 'text-anchor="end"')
        text(margin + 10, 176, f"{len(days):,} LISTED DATES · {len(periods):02} ANNUAL PLATES", 14, "#91aeaa")
    else:
        text(width - margin - 10, 76, f"{total:,}", 54, "#d6f4df", 'text-anchor="end" letter-spacing="2"')
        text(width - margin - 10, 103, "CONTRIBUTIONS", 16, "#8ebaa3", 'text-anchor="end" letter-spacing="2"')
        text(margin + 10, 138, f"{start:%d %b %Y} — {end:%d %b %Y}".upper(), 14, "#91aeaa", 'letter-spacing="1"')
        text(width - margin - 10, 138, f"{len(days):,} LISTED DATES · {len(periods):02} ANNUAL PLATES", 14, "#91aeaa", 'text-anchor="end" letter-spacing="1"')
    svg.append(f'<path d="M{margin+10} {header_height-15}H{width-margin-10}" stroke="url(#spectrum)" opacity=".68"/>')

    for index, (first, last) in enumerate(periods):
        left = margin + (index % columns) * (panel_width + gap)
        top = header_height + (index // columns) * (panel_height + gap)
        count_map = {day: count for day, count in days.items() if first <= day <= last}
        annual_total = sum(count_map.values())
        week_start = first - timedelta(days=(first.weekday() + 1) % 7)
        week_count = ((last - week_start).days + 7) // 7
        ux, uy = 9.5, 5.0
        vx, vy = (panel_width - 56 - 7 * ux) / week_count, -52 / week_count
        origin_x, origin_y = left + 26, top + 179

        def point(week: float, weekday: float, value_height: float = 0) -> tuple[float, float]:
            return origin_x + week * vx + weekday * ux, origin_y + week * vy + weekday * uy - value_height

        svg.append(f'<g aria-label="{first:%B %Y} to {last:%B %Y}: {annual_total:,} contributions" data-period-start="{first}" data-period-end="{last}" data-total="{annual_total}">')
        svg.append(f'<rect x="{left:g}" y="{top:g}" width="{panel_width:g}" height="{panel_height}" rx="2" fill="url(#plate)" stroke="#2b4f41"/>')
        svg.append(f'<path d="M{left+1:g} {top+27:g}V{top+1:g}H{left+27:g} M{left+panel_width-27:g} {top+panel_height-1:g}H{left+panel_width-1:g}V{top+panel_height-27:g}" fill="none" stroke="#81b397"/>')
        text(left + 16, top + 28, f"{first:%Y}—{last:%y}", 24, "#bfdecf", 'letter-spacing="1"')
        text(left + 16, top + 47, f"{first:%b %Y} — {last:%b %Y}".upper(), 14 if mobile else 12, "#84aa98", 'letter-spacing="1"')
        text(left + panel_width - 16, top + 30, f"{annual_total:,}", 29, "#d1ead8", 'text-anchor="end"')
        text(left + panel_width - 16, top + 48, "CONTRIBUTIONS", 13 if mobile else 12, "#84aa98", 'text-anchor="end" letter-spacing="1.5"')
        svg.append(f'<path d="M{left+16:g} {top+59:g}H{left+panel_width-16:g}" stroke="#1e3e32"/>')
        svg.append(f'<ellipse cx="{left+panel_width/2:g}" cy="{top+159:g}" rx="{panel_width*.48:g}" ry="73" fill="url(#field-halo)"/>')
        a, b, c, d = point(0, 0), point(week_count, 0), point(week_count, 7), point(0, 7)
        lower = lambda p: (p[0], p[1] + 12)
        polygon([a, b, c, d], "#04100d", "#355b49", line_width=.65)
        polygon([d, c, lower(c), lower(d)], "url(#depth)", "#28513e", line_width=.55)
        polygon([b, c, lower(c), lower(b)], "#081a14", "#315740", line_width=.55)
        for week in range(week_count + 1):
            p, q = point(week, 0), point(week, 7)
            svg.append(f'<path d="M{p[0]:.2f},{p[1]:.2f}L{q[0]:.2f},{q[1]:.2f}" stroke="#173d2d" stroke-width=".35"/>')
        for weekday in range(8):
            p, q = point(0, weekday), point(week_count, weekday)
            svg.append(f'<path d="M{p[0]:.2f},{p[1]:.2f}L{q[0]:.2f},{q[1]:.2f}" stroke="#244f3c" stroke-width=".35"/>')
        for depth, opacity in ((1, .8), (4, .3), (8, .18)):
            svg.append(f'<path d="M{d[0]:.2f},{d[1]+depth:.2f}L{c[0]:.2f},{c[1]+depth:.2f}" stroke="url(#spectrum)" stroke-width=".8" opacity="{opacity}"/>')

        cells = []
        for day, count in count_map.items():
            offset = (day - week_start).days
            cells.append((offset // 7, offset % 7, day, count))
        for wi, di, day, count in sorted(cells, key=lambda cell: point(cell[0], cell[1])[1]):
            inset = .10
            base = [point(wi + inset, di + inset), point(wi + 1 - inset, di + inset), point(wi + 1 - inset, di + 1 - inset), point(wi + inset, di + 1 - inset)]
            svg.append(f'<g data-date="{day}" data-count="{count}"><title>{day}: {count} contribution{"s" if count != 1 else ""}</title>')
            if count == 0:
                polygon(base, "#163827", "#517960", line_width=.35)
            else:
                # Every year shares the same height scale. Hue follows the month-axis.
                crystal_height = 49 * count / peak
                hue = .025 + .765 * (wi + .5) / week_count
                shoulder_height = crystal_height * .60
                shoulders = [(x, y - shoulder_height) for x, y in base]
                tip = point(wi + .5, di + .5, crystal_height)
                polygon([base[3], base[2], shoulders[2], shoulders[3]], _color(hue, .36, .55), _color(hue, .52, .5))
                polygon([base[1], base[2], shoulders[2], shoulders[1]], _color(hue, .22, .48), _color(hue, .36, .5))
                polygon([shoulders[0], shoulders[1], tip], _color(hue, .69, .39), _color(hue, .75, .32))
                polygon([shoulders[1], shoulders[2], tip], _color(hue, .47, .56), _color(hue, .62, .40))
                polygon([shoulders[2], shoulders[3], tip], _color(hue, .87, .24), _color(hue, .97, .19))
                polygon([shoulders[3], shoulders[0], tip], _color(hue, .63, .40), _color(hue, .76, .33))
                svg.append(f'<path d="M{tip[0]:.2f},{tip[1]:.2f}L{shoulders[3][0]:.2f},{shoulders[3][1]:.2f}" stroke="{_color(hue, .98, .14)}" stroke-width=".55" opacity=".9"/>')
                if count == peak:
                    svg.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r="1.7" fill="{_color(hue, 1, .18)}" opacity=".7" filter="url(#peak-glow)"/>')
                    svg.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r=".68" fill="#f1f8e5"/>')
            svg.append('</g>')

        # Month ticks are aligned to actual dates, including the partial first week.
        for month_offset in range(12):
            month_index = first.month - 1 + month_offset
            month_date = date(first.year + month_index // 12, month_index % 12 + 1, 1)
            if not first <= month_date <= last:
                continue
            w = (month_date - week_start).days / 7
            tick = point(w, 7)
            svg.append(f'<path d="M{tick[0]:.2f},{tick[1]+12:.2f}v3" stroke="#658670" stroke-width=".7"/>')
            if month_offset in (0, 3, 6, 9, 11):
                label = point(w, 7, -25)
                text(label[0], label[1], f"{month_date:%b}".upper(), 10, "#89a696", 'letter-spacing=".7"')
        text(left + 16, top + panel_height - 10, f"{len(count_map):,} LISTED DATES", 13 if mobile else 12, "#799e8c", 'letter-spacing="1"')
        text(left + panel_width - 16, top + panel_height - 10, f"PLATE {index+1:02} / {len(periods):02}", 13 if mobile else 12, "#799e8c", 'text-anchor="end" letter-spacing="1"')
        svg.append('</g>')

    footer_y = header_height + rows * (panel_height + gap)
    svg.append(f'<path d="M{margin+10} {footer_y+1}H{width-margin-10}" stroke="#305443"/>')
    text(margin + 10, footer_y + 28, "HEIGHT = DAILY CONTRIBUTIONS", 18 if mobile else 16, "#abcbb7", 'letter-spacing=".6"')
    text(margin + 10, footer_y + 51, "UNLISTED DATES = GAPS", 17 if mobile else 13, "#8cac99", 'letter-spacing="1"')
    if mobile:
        text(margin + 10, footer_y + 78, f"SHARED HEIGHT SCALE  0—{peak} / DAY", 16, "#8cac99", 'letter-spacing=".6"')
    else:
        text(width - margin - 10, footer_y + 28, f"SHARED HEIGHT SCALE  0—{peak} / DAY", 13, "#a1c4b0", 'text-anchor="end" letter-spacing="1"')
        text(width - margin - 10, footer_y + 51, "SUPPLIED ACCOUNT ARCHIVE", 12, "#8cac99", 'text-anchor="end" letter-spacing="1"')
    svg.append(f'<rect x="8" y="8" width="{width-16}" height="{height-16}" fill="url(#scanlines)" pointer-events="none"/>\n</svg>')
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Normalized contribution archive JSON")
    parser.add_argument("output", type=Path, help="Output SVG file")
    parser.add_argument("--mobile", action="store_true", help="Stack annual plates for narrow screens")
    args = parser.parse_args()
    render_landscape(json.loads(args.dataset.read_text(encoding="utf-8")), args.output, mobile=args.mobile)


if __name__ == "__main__":
    main()
