#!/usr/bin/env python3
"""Generate the minimal profile and extend its archived contributions through today."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from html import escape
import json
import os
from pathlib import Path
import urllib.request

from render_landscape import render_landscape, _validated_days

ROOT = Path(__file__).resolve().parents[1]
INK = "#030908"
MINT = "#b7f6cf"
DIM = "#6d9a91"
BLUE = "#91bfff"
RAINBOW = ["#ff7968", "#ffc56c", "#e1ed88", "#98e3b2", "#78d9dc", "#91bfff", "#b2a4ed"]


def api(path: str, payload=None):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "acesava-profile"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request("https://api.github.com/" + path, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
    if isinstance(result, dict) and result.get("errors"):
        raise RuntimeError("GitHub did not return complete public profile metadata")
    return result


def text(x, y, value, size=22, color=MINT, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'


def svg(title, height, body, width=1200):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}">
<title>{escape(title)}</title>
<defs>
 <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 0H4" stroke="#c8ffdb" opacity=".025"/></pattern>
 <filter id="glow"><feGaussianBlur stdDeviation="1.3"/></filter>
</defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.blink{{animation:blink 2.2s steps(1) infinite}}.sweep{{animation:sweep 12s linear infinite}}@keyframes blink{{0%,65%{{opacity:1}}66%,100%{{opacity:.2}}}}@keyframes sweep{{from{{transform:translateX(0)}}to{{transform:translateX(262px)}}}}@media(prefers-reduced-motion:reduce){{.blink,.sweep{{animation:none}}}}</style>
<rect width="{width}" height="{height}" fill="{INK}"/>
<rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="#56867a"/>
<rect x="7" y="7" width="{width-14}" height="{height-14}" fill="none" stroke="#1d3930"/>
{body}
<rect width="{width}" height="{height}" fill="url(#scan)" pointer-events="none"/>
</svg>'''


def spectrum(x, y, width=300):
    return ''.join(f'<path d="M{x} {y+i*3}h{width}" stroke="{c}" opacity=".85"/>' for i,c in enumerate(RAINBOW))


def intro(profile):
    name = (profile.get("name") or "acesava").strip()
    location = (profile.get("location") or "").strip()
    body = text(32, 77, name.upper(), 42)
    body += '<rect class="blink" x="182" y="49" width="20" height="31" fill="#b7f6cf"/>'
    body += text(32, 120, "@acesava", 22, BLUE)
    body += '<path d="M450 28V132" stroke="#32534a"/>'
    body += text(487, 65, "LOCATION", 17, DIM) + text(487, 103, location, 23)
    body += spectrum(950, 72, 210)
    return svg("Ace S — acesava. San Francisco, CA.", 160, body)


def intro_mobile(profile):
    body = text(25, 65, (profile.get("name") or "acesava").strip().upper(), 42)
    body += '<rect class="blink" x="180" y="34" width="20" height="32" fill="#b7f6cf"/>'
    body += text(25, 107, "@acesava", 23, BLUE)
    body += spectrum(359, 48, 213)
    body += text(25, 149, (profile.get("location") or "").strip(), 22)
    return svg("Ace S — acesava. San Francisco, CA.", 178, body, 600)


def calendar_days(result):
    """Read a GraphQL response without silently replacing unavailable data."""
    if result.get("errors"):
        raise ValueError("GitHub contribution query returned errors")
    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    rows = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    if sum(row["contributionCount"] for row in rows) != calendar["totalContributions"]:
        raise ValueError("GitHub calendar total does not reconcile to its daily counts")
    return rows


def fetch_recent(start, end):
    """GitHub permits at most one year per contribution-calendar query."""
    query = """query($from: DateTime!, $to: DateTime!) {
      user(login: "acesava") {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }"""
    rows = []
    cursor = start
    while cursor <= end:
        last = min(end, cursor + timedelta(days=364))
        result = api("graphql", {"query": query, "variables": {
            "from": cursor.isoformat() + "T00:00:00Z",
            "to": last.isoformat() + "T23:59:59Z",
        }})
        rows.extend(calendar_days(result))
        cursor = last + timedelta(days=1)
    return rows


def combine_archive(archive, recent_rows, today):
    """Preserve the archive, then append disjoint, complete current-account days."""
    start, cutoff, archived_days = _validated_days(archive)
    if today <= cutoff:
        raise ValueError("The refresh date must follow the supplied archive coverage")
    recent = {}
    for row in recent_rows:
        day = date.fromisoformat(row["date"])
        count = row["contributionCount"]
        if not cutoff < day <= today:
            raise ValueError(f"Current-account date {day} overlaps the archive or is outside the refresh range")
        if day in recent:
            raise ValueError(f"Duplicate current-account date: {day}")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"Invalid current-account contribution count: {count!r}")
        recent[day] = count
    expected = {cutoff + timedelta(days=i) for i in range(1, (today-cutoff).days+1)}
    if set(recent) != expected:
        raise ValueError("Current-account calendar is incomplete; keeping the existing display")
    combined = archived_days | recent
    return {
        "title": "Combined Account Contribution topography",
        "startDate": start.isoformat(),
        "endDate": today.isoformat(),
        "totalContributions": sum(combined.values()),
        "sources": [
            {"type": "user-supplied", "path": "data/contributions.json",
             "startDate": start.isoformat(), "endDate": cutoff.isoformat(),
             "totalContributions": sum(archived_days.values())},
            {"type": "github", "account": "acesava",
             "startDate": (cutoff+timedelta(days=1)).isoformat(),
             "endDate": today.isoformat(), "totalContributions": sum(recent.values())},
        ],
        "note": "The supplied archive is preserved through its stated end date. Subsequent days come from the acesava GitHub calendar. Missing archive dates are unlisted, not confirmed zero. The current date and month may be partial.",
        "days": [{"date": day.isoformat(), "contributionCount": count}
                 for day, count in sorted(combined.items())],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path,
                        help="Offline profile.json and recent-contributions.json GraphQL response")
    parser.add_argument("--as-of", type=date.fromisoformat,
                        default=datetime.now(ZoneInfo("America/Los_Angeles")).date(),
                        help="Final displayed date; defaults to today in America/Los_Angeles")
    args = parser.parse_args()
    archive = json.loads((ROOT/"data"/"contributions.json").read_text())
    _, cutoff, _ = _validated_days(archive)
    if args.input_dir:
        profile = json.loads((args.input_dir/"profile.json").read_text())
        recent = calendar_days(json.loads((args.input_dir/"recent-contributions.json").read_text()))
    else:
        profile = api("users/acesava")
        recent = fetch_recent(cutoff+timedelta(days=1), args.as_of)
    dataset = combine_archive(archive, recent, args.as_of)
    assets = ROOT/"assets"
    assets.mkdir(exist_ok=True)
    render_landscape(dataset, assets/"contributions.svg")
    render_landscape(dataset, assets/"contributions-mobile.svg", mobile=True)
    (assets/"operator.svg").write_text(intro(profile))
    (assets/"operator-mobile.svg").write_text(intro_mobile(profile))
    (ROOT/"data"/"combined-contributions.json").write_text(json.dumps(dataset, indent=2)+"\n")
    print(f"Rendered {dataset['totalContributions']:,} combined contributions through {args.as_of}: "
          f"{archive['totalContributions']:,} archived + {dataset['sources'][1]['totalContributions']:,} current-account contributions.")


if __name__ == "__main__":
    main()
