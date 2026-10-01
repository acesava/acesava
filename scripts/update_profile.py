#!/usr/bin/env python3
"""Generate the profile's instrument displays from public GitHub data."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import textwrap
import urllib.request

from render_landscape import render_landscape

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
        raise RuntimeError("GitHub did not return a complete contribution calendar")
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
    body += text(487, 128, "PUBLIC REPOSITORIES", 17, DIM) + text(787, 129, f'{len(repos):02}', 26, BLUE)
    body += text(1003, 44, "DISPLAY / 01", 15, DIM)
    body += spectrum(950, 80, 210)
    body += text(950, 140, updated[:10] + " UTC", 15, DIM)
    return svg("Ace S — acesava. Public GitHub profile information.", 178, body)


def monitor(index, title_lines, subtitle, tag, variant):
    # The compact diagrams are decorative; project claims stay in readable text.
    body = text(28, 37, f"0{index+1} / PUBLIC PROJECT", 16, DIM)
    body += '<rect x="28" y="56" width="265" height="130" fill="#071210" stroke="#497766"/>'
    for i in range(1,8):
        body += f'<path d="M{28+i*33} 56V186" stroke="#29453b" stroke-width=".7"/>'
    for i in range(1,4):
        body += f'<path d="M28 {56+i*32}H293" stroke="#29453b" stroke-width=".7"/>'
    if variant == "map":
        for off in [0,13,26,39]:
            body += f'<path d="M{42+off} 175L{67+off} 146L{80+off} 121L{102+off} 104L{110+off} 75L{136+off} 65" fill="none" stroke="#78d9dc" opacity="{.9-off/65}"/>'
        for x,y in [(135,100),(179,142),(227,91),(94,155),(240,160)]:
            body += f'<circle cx="{x}" cy="{y}" r="4" fill="#e1ed88"/>'
        body += text(221, 176, "LA", 15, BLUE)
    elif variant == "signal":
        for offset,c in [(0,BLUE),(19,MINT)]:
            pts = ' '.join(f'{35+i*4},{119+offset+math.sin(i*.18)*19+math.cos(i*.39)*8}' for i in range(63))
            body += f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2"/>'
        body += text(44,79,"LA / SF",15,DIM)
    else:
        for i,c in enumerate(RAINBOW):
            body += f'<path d="M{48+i*28} {161-i*8}v{-30-i*3}l14 -8v{30+i*3}Z" fill="{c}" fill-opacity=".55" stroke="{c}"/>'
    body += '<path class="sweep" d="M29 59v124" stroke="#b7f6cf" opacity=".33"/>'
    for i,line in enumerate(title_lines):
        body += text(330,84+i*37,line,32)
    body += text(330,158,subtitle,20,DIM)
    body += text(330,194,tag,15,BLUE)
    body += text(1130,119,"↗",34,MINT)
    return svg(' — '.join(title_lines) + '. ' + subtitle,218,body)


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
    body += text(360,136,f'{len(repos):02} PUBLIC REPOS',18)
    body += text(360,184,updated[:10]+" UTC",16,DIM)
    return svg("Ace S — acesava. Public GitHub profile information.",210,body,600)


def monitor_mobile(index,title_lines,subtitle,tag,variant):
    body = text(24,37,f"0{index+1} / PUBLIC PROJECT",17,DIM)
    body += '<rect x="24" y="60" width="128" height="110" fill="#071210" stroke="#497766"/>'
    body += spectrum(38,105,100)
    body += text(182,93,title_lines[0],24)
    if len(title_lines)>1:
        body += text(182,126,title_lines[1],24)
    body += text(549,163,"↗",27)
    for i,line in enumerate(textwrap.wrap(subtitle,width=45)):
        body += text(24,212+i*29,line,20,DIM)
    return svg(' — '.join(title_lines)+'. '+subtitle,282,body,600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",type=Path,help="Use previously fetched profile.json, repos.json, contributions.json")
    args = parser.parse_args()
    if args.input_dir:
        profile,repos,result = [json.loads((args.input_dir/f'{name}.json').read_text()) for name in ("profile","repos","contributions")]
    else:
        profile = api("users/acesava")
        repos = api("users/acesava/repos?per_page=100&type=owner")
        result = api("graphql",{"query":'query { user(login:"acesava") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount color } } } } } }'})
    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    if not calendar.get("weeks"):
        raise RuntimeError("Refusing to replace the display with an empty calendar")
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
    print(f"Rendered profile from {len(repos)} public repositories and {calendar['totalContributions']} GitHub contributions.")


if __name__ == "__main__":
    main()
