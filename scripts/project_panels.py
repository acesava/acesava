"""Detailed, decorative CRT instrument illustrations for the project index.

These are designed illustrations, not charts of restaurant or project measurements.
The two public entry points preserve the original profile generator signatures.
"""
from __future__ import annotations

from html import escape
import math
import textwrap

INK = "#030908"
MINT = "#d0f8df"
DIM = "#8aada1"
BLUE = "#a6caff"
RAINBOW = ("#ff9488", "#f8c889", "#e0ed9d", "#a3e7bd", "#8bdfdf", "#a6caff", "#c4b1f3")


def _text(x, y, value, size=20, color=MINT, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'


def _path(d, color="#719d8d", width=1, opacity=1, extra=""):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}" {extra}/>'


def _poly(points, color, opacity=1, width=1):
    coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'


def _grid():
    s = '<rect x="9" y="9" width="342" height="176" fill="url(#screen)"/>'
    for x in range(18, 352, 12):
        s += _path(f'M{x} 12V181', "#386253", .5, .34)
    for y in range(17, 182, 12):
        s += _path(f'M12 {y}H348', "#386253", .5, .34)
    return s


def _map():
    """An engraved street atlas and contour field; intentionally schematic."""
    s = _grid()
    # Topographic bands meet a tilted street lattice, like an old map terminal.
    for i in range(11):
        d = f'M{13+i*8} 180C{28+i*6} 141 {11+i*8} 126 {42+i*7} 102S{74+i*7} 50 {97+i*7} 13'
        s += _path(d, RAINBOW[3+i%3], .7, .25+i*.035)
    for i in range(12):
        x = 105+i*16
        s += _path(f'M{x} 18L{x-63} 178', "#6a9e85", .7, .62)
    for i in range(10):
        y = 23+i*15
        s += _path(f'M87 {y}L344 {y+38}', "#5e947d", .7, .62)
    # Wide boulevards and freeway-style curves have separate casing and light.
    routes = [
        'M67 171C107 155 115 133 141 120S207 106 230 87S288 68 335 36',
        'M100 16L119 51L174 92L199 123L280 171',
        'M55 139L132 141L175 135L224 145L339 124',
    ]
    for d in routes:
        s += _path(d, "#06120f", 5)
        s += _path(d, "#b7dcc1", 1.5, .85)
    s += _path('M48 17C54 54 78 52 72 83S94 120 73 157S59 170 57 180', BLUE, 1.7, .8)
    # Schematized district blocks, not real restaurant locations.
    for x, y, w, h in [(133,53,22,16),(210,44,16,19),(226,102,29,17),(280,79,28,15),(179,148,20,16),(105,106,16,20)]:
        s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#8fe0b5" opacity=".09" stroke="#a3e7bd" stroke-width=".7"/>'
    for j, (x, y) in enumerate([(137,117),(182,96),(228,89),(277,69),(227,143)]):
        s += f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="{RAINBOW[j+1]}" opacity=".38"/>'
        s += f'<circle cx="{x}" cy="{y}" r="3" fill="{RAINBOW[j+1]}"/>'
        s += _path(f'M{x-12} {y}h5m14 0h5M{x} {y-12}v5m0 14v5', RAINBOW[j+1], .65, .65)
    s += '<rect x="245" y="146" width="93" height="28" fill="#071410" stroke="#5f8d7b" stroke-width=".7"/>'
    s += _text(254,165,'LOS ANGELES',11,'#c5e9cb')
    return s


def _scope(cx, cy, r, label, tint, phase):
    s = f'<circle cx="{cx}" cy="{cy}" r="{r+4}" fill="#071611" stroke="#598573" stroke-width=".6"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#scope)" stroke="{tint}" stroke-width=".8" opacity=".9"/>'
    for j in range(1,6):
        s += f'<circle cx="{cx}" cy="{cy}" r="{r*j/6:.2f}" fill="none" stroke="{tint}" stroke-width=".6" opacity=".24"/>'
    for a in range(0,360,15):
        rad = math.radians(a)
        a0, a1 = (r-5 if a%45==0 else r-3), r
        s += _path(f'M{cx+math.cos(rad)*a0:.2f} {cy+math.sin(rad)*a0:.2f}L{cx+math.cos(rad)*a1:.2f} {cy+math.sin(rad)*a1:.2f}', tint,.8,.75)
    s += _path(f'M{cx-r} {cy}H{cx+r}M{cx} {cy-r}V{cy+r}', tint,.7,.35)
    for j in range(6):
        pts=[]
        for k in range(65):
            a=k*math.tau/64
            radius=13+j*4+math.sin(a*3+phase+j*.3)*4+math.cos(a*5+phase)*2
            pts.append((cx+math.cos(a)*radius,cy+math.sin(a)*radius*.82))
        s += _poly(pts,tint,.25+j*.09,.7)
    for k in range(4):
        a=phase+k*1.43
        x,y=cx+math.cos(a)*r*.59,cy+math.sin(a)*r*.59
        s+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.8" fill="#e0ed9d"/>'
    s += _text(cx,cy+r+20,label,12,tint,'text-anchor="middle" letter-spacing="2"')
    return s


def _signal():
    """Two atlas scopes with interlaced routes and an illustrative signal strip."""
    s = _grid()
    for i,c in enumerate(RAINBOW):
        s += _path(f'M125 {68+i*6}C166 {28+i*12} 197 {143-i*11} 237 {70+i*6}',c,.9,.65)
    s += _scope(77,82,53,'LOS ANGELES',RAINBOW[3],.35)
    s += _scope(283,82,53,'SAN FRANCISCO',RAINBOW[5],2)
    s += '<rect x="143" y="133" width="76" height="25" fill="#08130f" stroke="#4d7969" stroke-width=".7"/>'
    s += _text(181,149,'MENU ATLAS',9,'#c8dbba','text-anchor="middle" letter-spacing=".6"')
    for j, c in enumerate([RAINBOW[2],RAINBOW[4]]):
        pts=[(16+i*2,170+j*6+math.sin(i*.14+j)*2.4+math.cos(i*.43+j)*1.6) for i in range(165)]
        s+=_poly(pts,c,.72,.85)
    return s


def _prism():
    """A many-faceted crystal above a spectral wireframe reference plane."""
    s = _grid()
    # Perspective floor references the rainbow plane in the main artwork.
    for i,c in enumerate(RAINBOW):
        for j in range(3):
            y=128+i*6+j*1.55
            d=(y-128)*1.25
            s += _path(f'M{78-d:.2f} {y:.2f}H{282+d:.2f}',c,.9,.72)
    for j in range(17):
        s += _path(f'M{78+j*12.75:.2f} 128L{23+j*19.55:.2f} 177',"#bad7d1",.65,.33)
    # An asymmetric crystal, rendered face by face with subtle inner facets.
    p={'top':(181,21),'a':(124,54),'b':(157,45),'c':(216,51),'d':(241,77),'e':(199,100),'f':(157,96),'g':(108,81),'tip':(182,145),'core':(177,75)}
    faces=[('top a b',5),('top b c',4),('top c d',6),('a g b',3),('b g f',4),('b f core',5),('b core c',3),('c core e',6),('c e d',5),('d e tip',6),('e core tip',5),('core f tip',4),('f g tip',3)]
    for j,(names,ci) in enumerate(faces):
        coords=' '.join(f'{p[n][0]},{p[n][1]}' for n in names.split())
        s+=f'<polygon points="{coords}" fill="{RAINBOW[ci]}" fill-opacity="{.12+(j%4)*.09}" stroke="{RAINBOW[ci]}" stroke-width=".85" stroke-opacity=".88"/>'
    s += _path('M181 21L177 75L182 145M108 81L241 77M124 54L199 100M157 45L157 96', '#d9f7ee',.55,.58)
    for x,y in [(181,21),(124,54),(241,77),(182,145),(177,75)]:
        s+=f'<circle cx="{x}" cy="{y}" r="1.4" fill="#edfff4"/>'
        s+=_path(f'M{x-4} {y}h8M{x} {y-4}v8','#e2eaf7',.65,.75)
    s += _path('M84 57H55V118H112M260 46H307V106H251', '#8eaba7',.65,.6)
    for x,y,label in [(47,50,'RGB'),(294,124,'SVG')]:
        s+=_text(x,y,label,10,BLUE,'letter-spacing="1.5"')
    for i,c in enumerate(RAINBOW):
        s+=f'<rect x="{23+i*7}" y="25" width="4" height="12" fill="{c}" opacity=".65"/>'
    return s


_DIAGRAMS = {'map': _map, 'signal': _signal, 'prism': _prism}
_LABELS = {'map': 'URBAN FIELD / SCHEMATIC', 'signal': 'NEIGHBORHOOD ATLAS / STUDY', 'prism': 'CHROMATIC DISPLAY / STUDY'}


def _instrument(variant,x,y,width,height):
    body=_DIAGRAMS.get(variant,_prism)()
    body+='<rect x="6" y="6" width="348" height="182" rx="2" fill="none" stroke="#91b5a2" stroke-width="1"/>'
    body+='<rect x="3" y="3" width="354" height="188" rx="3" fill="none" stroke="#25453b" stroke-width="1"/>'
    # Four warm phosphor corners evoke the photograph's instrument bezels.
    body+=_path('M6 27V6H27M333 6H354V27M354 167V188H333M27 188H6V167','#d5ecc8',1,.8)
    return f'<svg x="{x}" y="{y}" width="{width}" height="{height}" viewBox="0 0 360 194">{body}</svg>'


def _svg(title,width,height,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title,quote=True)}">
<title>{escape(title)}</title><desc>Decorative instrument illustration. The diagram is not measured project data.</desc>
<defs>
 <linearGradient id="screen" x2="0" y2="1"><stop stop-color="#0b1b16"/><stop offset="1" stop-color="#030b08"/></linearGradient>
 <radialGradient id="scope"><stop stop-color="#244d38"/><stop offset=".66" stop-color="#102c21"/><stop offset="1" stop-color="#05110d"/></radialGradient>
 <linearGradient id="edge"><stop stop-color="#416c5c"/><stop offset=".5" stop-color="#92b69b"/><stop offset="1" stop-color="#3c6054"/></linearGradient>
 <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 .5H4" stroke="#d1ffe3" stroke-opacity=".025"/></pattern>
</defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}text{{text-rendering:geometricPrecision}}</style>
<rect width="{width}" height="{height}" fill="{INK}"/>
<rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="url(#edge)"/>
<rect x="7" y="7" width="{width-14}" height="{height-14}" fill="none" stroke="#1c3b30"/>
{body}<rect x="8" y="8" width="{width-16}" height="{height-16}" fill="url(#scan)" pointer-events="none"/>
</svg>'''


def _arrow(x,y):
    return _path(f'M{x} {y+17}L{x+18} {y-1}M{x+3} {y-1}H{x+18}V{y+14}',MINT,1.7)


def monitor(index,title_lines,subtitle,tag,variant):
    body=_text(27,34,f'{index+1:02} / PUBLIC PROJECT',16,DIM,'letter-spacing="1.3"')
    body+=_instrument(variant,23,48,363,196)
    body+=_text(29,263,_LABELS.get(variant,_LABELS['prism']),11,DIM,'letter-spacing=".8"')
    body+=_path('M403 26V258','#385e4c',.8)
    for i,line in enumerate(title_lines):
        body+=_text(430,90+i*40,line,34,MINT,'letter-spacing=".5"')
    if len(title_lines)==1:
        for i,c in enumerate(RAINBOW):
            body+=_path(f'M{431+i*42} 117h32',c,2,.8)
    for i,line in enumerate(textwrap.wrap(subtitle,width=57)):
        body+=_text(431,179+i*29,line,21,'#a6c2b7')
    body+=_path('M431 226H1166','#294d3d',.8)
    body+=_text(431,255,tag,16,BLUE,'letter-spacing=".6"')
    body+=_arrow(1139,61)
    return _svg(' — '.join(title_lines)+'. '+subtitle,1200,282,body)


def monitor_mobile(index,title_lines,subtitle,tag,variant):
    body=_text(25,37,f'{index+1:02} / PUBLIC PROJECT',17,DIM,'letter-spacing="1"')
    body+=_instrument(variant,21,60,286,154)
    mobile_lines=[wrapped for line in title_lines for wrapped in textwrap.wrap(line,width=17)]
    for i,line in enumerate(mobile_lines):
        body+=_text(328,87+i*30,line,23,MINT)
    body+=_text(29,239,_LABELS.get(variant,_LABELS['prism']),12,DIM,'letter-spacing=".5"')
    body+=_path('M25 253H575','#325844',.8)
    for i,line in enumerate(textwrap.wrap(subtitle,width=42)):
        body+=_text(26,287+i*30,line,21,'#b0cbbd')
    body+=_text(26,362,tag,15,BLUE)
    body+=_arrow(553,26)
    return _svg(' — '.join(title_lines)+'. '+subtitle,600,386,body)
