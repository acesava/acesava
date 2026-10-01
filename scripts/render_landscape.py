#!/usr/bin/env python3
"""Render a repository-owned contribution landscape, using only Python's stdlib.

Height is linear in daily contribution count, normalized to the displayed maximum.
Missing/invalid counts are treated as zero. Every supplied day is represented.
"""

from __future__ import annotations

import argparse
import colorsys
from datetime import date
from html import escape
import json
from pathlib import Path


def _count(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def _points(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def _color(hue: float, value: float = 1.0, saturation: float = .60) -> str:
    return "#" + "".join(f"{round(c * 255):02x}" for c in colorsys.hsv_to_rgb(hue % 1, saturation, value))


def _period(days: list[tuple[int, int, str, int]]) -> str:
    dates = []
    for _, _, day, _ in days:
        try:
            dates.append(date.fromisoformat(day))
        except ValueError:
            pass
    if not dates:
        return "DATE RANGE UNAVAILABLE"
    first, last = min(dates), max(dates)
    return f"{first:%d %b %Y} — {last:%d %b %Y}".upper()


def render_landscape(calendar: dict, output_path: Path) -> None:
    """Write a self-contained, accessible SVG for a GitHub contribution calendar."""
    weeks = calendar.get("weeks") or []
    days: list[tuple[int, int, str, int]] = []
    for wi, week in enumerate(weeks):
        if not isinstance(week, dict):
            continue
        for di, day in enumerate(week.get("contributionDays") or []):
            if isinstance(day, dict):
                raw_date = str(day.get("date") or "")
                # GitHub omits days outside the requested range in edge weeks.
                # Keep those dates in their real weekday slots rather than shifting.
                try:
                    weekday = (date.fromisoformat(raw_date).weekday() + 1) % 7
                except ValueError:
                    weekday = di
                days.append((wi, weekday, raw_date, _count(day.get("contributionCount"))))
    total = _count(calendar.get("totalContributions")) if calendar.get("totalContributions") is not None else sum(d[3] for d in days)
    peak = max((d[3] for d in days), default=0)
    period = _period(days)
    week_count = max(1, len(weeks))
    row_count = max(7, max((d[1] + 1 for d in days), default=7))
    vx, vy = (1004 - row_count * 14) / week_count, -100 / week_count
    ux, uy = 14.0, 7.1
    ox, oy = 98.0, 269.0

    def point(w: float, d: float, height: float = 0) -> tuple[float, float]:
        return ox + w * vx + d * ux, oy + w * vy + d * uy - height

    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="430" viewBox="0 0 1200 430" role="img" aria-labelledby="landscape-title landscape-desc">
<title id="landscape-title">GitHub activity — contribution crystal landscape</title>
<desc id="landscape-desc">{escape(period)}. {total:,} contributions. Each crystal represents one day; its height is proportional to that day's contribution count. Maximum daily count: {peak:,}. Empty cells represent zero contributions.</desc>
<defs>
  <linearGradient id="spectrum" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#fb7655"/><stop offset=".2" stop-color="#d8dc6d"/><stop offset=".4" stop-color="#95efb9"/><stop offset=".65" stop-color="#65d5df"/><stop offset=".85" stop-color="#7da0f8"/><stop offset="1" stop-color="#c999ed"/></linearGradient>
  <linearGradient id="depth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#184634"/><stop offset="1" stop-color="#03110d"/></linearGradient>
  <radialGradient id="halo"><stop stop-color="#29715a" stop-opacity=".20"/><stop offset="1" stop-color="#020706" stop-opacity="0"/></radialGradient>
  <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 1H4" stroke="#a9efd1" stroke-opacity=".025"/></pattern>
  <filter id="soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.3"/></filter>
</defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}} .label{{fill:#73a68e;font-size:16px;letter-spacing:1.5px}} .fine{{fill:#4b755f;font-size:13px;letter-spacing:1px}}</style>
<rect width="1200" height="430" fill="#020706"/>
<rect x="17" y="17" width="1166" height="396" rx="3" fill="none" stroke="#335b46"/>
<path d="M17 40V17H40 M1160 17H1183V40 M1183 390V413H1160 M40 413H17V390" fill="none" stroke="#a0d5ad" stroke-width="1.2"/>
<text x="39" y="48" fill="#bde7c5" font-size="22" letter-spacing="3.5">GITHUB ACTIVITY</text>
<text x="39" y="71" class="label">CONTRIBUTION TOPOGRAPHY / ACESAVA</text>
<text x="1158" y="54" fill="#c9f0d1" font-size="38" text-anchor="end" letter-spacing="2">{total:,}</text>
<text x="1158" y="74" class="label" text-anchor="end">CONTRIBUTIONS</text>
<path d="M39 89H1161" stroke="#234332"/>
<ellipse cx="620" cy="256" rx="554" ry="113" fill="url(#halo)"/>
''']

    def poly(vertices: list[tuple[float, float]], fill: str, stroke: str = "none", opacity: float = 1) -> None:
        svg.append(f'<polygon points="{_points(vertices)}" fill="{fill}" stroke="{stroke}" stroke-width=".55" opacity="{opacity:.2f}"/>')

    if days:
        a, b, c, d = point(0, 0), point(week_count, 0), point(week_count, row_count), point(0, row_count)
        lower = lambda p: (p[0], p[1] + 18)
        poly([a, b, c, d], "#06110d", "#316f50")
        poly([d, c, lower(c), lower(d)], "url(#depth)", "#28533a")
        poly([b, c, lower(c), lower(b)], "#091b12", "#28533a")
        svg.append(f'<path d="M{d[0]:.2f},{d[1]+3:.2f} L{c[0]:.2f},{c[1]+3:.2f}" fill="none" stroke="url(#spectrum)" stroke-width="1.4" opacity=".75"/>')
        for depth in (7, 11, 15):
            svg.append(f'<path d="M{d[0]:.2f},{d[1]+depth:.2f} L{c[0]:.2f},{c[1]+depth:.2f}" stroke="url(#spectrum)" stroke-width=".5" opacity=".2"/>')
        # Draw the most distant cells first, allowing nearer crystals to occlude them.
        for wi, di, day, count in sorted(days, key=lambda cell: point(cell[0], cell[1])[1]):
            margin = .15
            base = [point(wi + margin, di + margin), point(wi + 1 - margin, di + margin), point(wi + 1 - margin, di + 1 - margin), point(wi + margin, di + 1 - margin)]
            label = f"{day or 'Undated day'}: {count} contribution{'s' if count != 1 else ''}"
            svg.append(f'<g data-date="{escape(day, quote=True)}" data-count="{count}"><title>{escape(label)}</title>')
            if not count:
                poly(base, "#0a1b12", "#24412e")
            else:
                height = 78 * count / peak
                # Spectrum follows weekdays, so even a short active period spans the palette.
                hue = .04 + .75 * di / max(1, row_count - 1)
                # A faceted crystal has a data-scaled tip and a low shoulder, not a flat bar.
                shoulder_height = height * .58
                shoulders = [(x, y - shoulder_height) for x, y in base]
                tip = point(wi + .5, di + .5, height)
                poly([base[3], base[2], shoulders[2], shoulders[3]], _color(hue, .34), _color(hue, .49))
                poly([base[1], base[2], shoulders[2], shoulders[1]], _color(hue, .23), _color(hue, .42))
                poly([shoulders[0], shoulders[1], tip], _color(hue, .60), _color(hue, .77))
                poly([shoulders[1], shoulders[2], tip], _color(hue, .45), _color(hue, .65))
                poly([shoulders[2], shoulders[3], tip], _color(hue, .80, .38), _color(hue, .90, .34))
                poly([shoulders[3], shoulders[0], tip], _color(hue, .64), _color(hue, .82))
                svg.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r="{.7 + 1.1 * count / peak:.2f}" fill="{_color(hue, .95, .22)}"/>')
                if count >= peak * .65:
                    svg.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r="2.1" fill="{_color(hue)}" opacity=".65" filter="url(#soft-glow)"/>')
            svg.append('</g>')
        svg.append('<text x="58" y="350" class="fine">EARLIER</text><text x="1138" y="246" class="fine" text-anchor="end">RECENT</text>')
    else:
        svg.append('<text x="600" y="234" fill="#8eb398" font-size="15" letter-spacing="3" text-anchor="middle">NO DAILY ACTIVITY DATA</text>')
    svg.append(f'''<path d="M39 365H1161" stroke="#234332"/>
<text x="39" y="394" class="label">HEIGHT = DAILY CONTRIBUTIONS</text>
<text x="1158" y="394" class="label" text-anchor="end">{escape(period)}</text>
<rect x="18" y="18" width="1164" height="394" fill="url(#scanlines)" pointer-events="none"/>
</svg>''')
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("calendar", type=Path, help="Contribution calendar JSON or GitHub GraphQL response")
    parser.add_argument("output", type=Path, help="Output SVG file")
    args = parser.parse_args()
    calendar = json.loads(args.calendar.read_text(encoding="utf-8"))
    if "data" in calendar:
        user = calendar["data"].get("user") or calendar["data"].get("viewer") or {}
        calendar = user.get("contributionsCollection", {}).get("contributionCalendar", {})
    render_landscape(calendar, args.output)


if __name__ == "__main__":
    main()
