#!/usr/bin/env python3
"""Generate profile instruments from public metadata and the supplied contribution archive."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import urllib.request

from render_landscape import render_landscape
from project_panels import monitor, monitor_mobile

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


def intro(profile, repos, updated):
    name = (profile.get("name") or "acesava").strip()
    location = (profile.get("location") or "").strip()
    body = text(32, 43, "01 / OPERATOR", 18, DIM)
    body += text(32, 100, name.upper(), 42)
    body += '<rect class="blink" x="182" y="72" width="20" height="31" fill="#b7f6cf"/>'
    body += text(32, 140, "@acesava", 22, BLUE)
    body += '<path d="M450 28V154" stroke="#32534a"/>'
    body += text(487, 57, "LOCATION", 17, DIM) + text(487, 89, location, 23)
    body += text(1003, 44, "DISPLAY / 01", 15, DIM)
    body += spectrum(950, 80, 210)
    body += text(950, 140, updated[:10] + " UTC", 15, DIM)
    return svg("Ace S — acesava. Public GitHub profile information.", 178, body)


def footer():
    body = text(30,38,"END OF TRANSMISSION",16,DIM)
    body += spectrum(420,20,370)
    body += text(956,38,"ACESAVA / ARCHIVE",16,MINT)
    return svg("End of transmission — acesava",60,body)


def intro_mobile(profile, repos, updated):
    body = text(25,38,"01 / OPERATOR",17,DIM)
    body += text(25,96,(profile.get("name") or "acesava").strip().upper(),42)
    body += '<rect class="blink" x="180" y="65" width="20" height="32" fill="#b7f6cf"/>'
    body += text(25,136,"@acesava",23,BLUE)
    body += spectrum(359,69,213)
    body += text(25,184,(profile.get("location") or "").strip(),22)
    body += text(360,184,updated[:10]+" UTC",16,DIM)
    return svg("Ace S — acesava. Public GitHub profile information.",210,body,600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",type=Path,help="Use previously fetched public profile.json and repos.json")
    args = parser.parse_args()
    if args.input_dir:
        profile,repos = [json.loads((args.input_dir/f'{name}.json').read_text()) for name in ("profile","repos")]
    else:
        profile = api("users/acesava")
        repos = api("users/acesava/repos?per_page=100&type=owner")
    calendar = json.loads((ROOT/"data"/"contributions.json").read_text())
    if not calendar.get("days"):
        raise RuntimeError("Refusing to replace the supplied contribution archive with empty data")
    repos = [r for r in repos if not r.get("private",False)]
    updated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    assets = ROOT/"assets"
    assets.mkdir(exist_ok=True)
    (assets/"operator.svg").write_text(intro(profile,repos,updated))
    (assets/"operator-mobile.svg").write_text(intro_mobile(profile,repos,updated))
    projects = [
        ("project-restaurants.svg",1,["LOS ANGELES","RESTAURANT STUDY"],"Korean restaurants + KBBQ. Public data, reproducible estimates.","PERMITS / OPEN MAPS / PYTHON","map"),
        ("project-noodles.svg",2,["BLACK BEAN NOODLES","ACROSS NEIGHBORHOODS"],"Jjajangmyeon + zhajiangmian across Los Angeles and San Francisco.","MENUS / NEIGHBORHOODS / RESEARCH","signal"),
        ("project-display.svg",3,["THE DISPLAY ENGINE"],"The artwork, source, and generated instruments behind this profile.","SVG / PYTHON / GITHUB ACTIONS","prism"),
    ]
    names = {r["name"] for r in repos}
    required = {"la-korean-restaurants","jjajangmyeon-restaurants","acesava"}
    if not required <= names:
        raise RuntimeError("A featured public repository is missing; review the index before updating")
    for file,index,title,subtitle,tag,variant in projects:
        (assets/file).write_text(monitor(index,title,subtitle,tag,variant))
        (assets/file.replace('.svg','-mobile.svg')).write_text(monitor_mobile(index,title,subtitle,tag,variant))
    (assets/"footer.svg").write_text(footer())
    render_landscape(calendar,assets/"contributions.svg")
    render_landscape(calendar,assets/"contributions-mobile.svg",mobile=True)
    print(f"Rendered profile from {len(repos)} public repositories and {calendar['totalContributions']} supplied contributions.")


if __name__ == "__main__":
    main()
