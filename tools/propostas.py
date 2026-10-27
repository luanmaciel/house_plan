"""Fluxo, três propostas de layout e elétrica do apartamento (obra só no banheiro).

Saídas em out/: fluxo.svg, proposta_A.svg, proposta_B.svg, proposta_C.svg, eletrica.svg,
propostas.html (página) e propostas.pdf (via Edge headless, se disponível).
Uso: python tools/propostas.py
"""
import copy
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plantas as PL  # noqa: E402
import prancheta as P  # noqa: E402

OUT = PL.OUT
R = PL.R
COL = PL.COL
MONO = PL.MONO
px = PL.px
PX = PL.PX
DOORS = {d["room"]: d for d in P.geo["doors"]}


# ---------------------------------------------------------------- propostas
def rel(room, x, y, w, h):
    return dict(x=round(R[room][0] + x, 3), y=round(R[room][1] + y, 3), w=w, h=h, room=room)


def montar(overrides, extras=()):
    items = copy.deepcopy(P.ITEMS)
    by = {it["id"]: it for it in items}
    for k, (room, x, y, w, h) in overrides.items():
        by[k].update(rel(room, x, y, w, h))
    for e in extras:
        items.append(e)
    return items


POLTRONA = dict(id="poltrona", label="poltrona reclinável 0,80x0,85", c="bed", op=0.5, fixed=False, dash=False, night=False,
                **rel("sala_bot", 0.05, 0.95, 0.80, 0.85))

PROPOSTAS = {
    "A": dict(titulo="Proposta A · layout de partida da prancheta", overrides={}, extras=(), resumo=[
        "Sala: sofá de 2,10 na parede da cozinha, rack e TV na parede do banheiro (1,43 m entre eles), mesa de jantar para 6 atravessada na frente, com passagem de 0,61 m para o hall.",
        "Quarto 2: bicama na parede de baixo, mesa de computador no canto da janela.",
        "Cozinha: geladeira no alto da parede oposta à bancada, mesa de café logo abaixo.",
        "Escritório: mesa na cabeceira da cama de solteiro, ambas na parede da esquerda.",
        "Lavanderia: máquina e tanque na parede da direita, um sobre o outro; sobram 1,76 m livres à frente das portas do escritório e do lavabo."]),
    "B": dict(titulo="Proposta B · passagem larga para o hall, TV do lado da cozinha", overrides={
        "sofa": ("sala_bot", 1.83, 1.0, 0.90, 2.10), "rack": ("sala_bot", 0.0, 1.3, 0.40, 1.80),
        "jantar": ("sala_top", 1.2, 0.24, 0.90, 1.60),
        "cadj1": ("sala_top", 0.70, 0.30, 0.45, 0.45), "cadj2": ("sala_top", 0.70, 0.85, 0.45, 0.45), "cadj3": ("sala_top", 0.70, 1.40, 0.45, 0.45),
        "cadj4": ("sala_top", 2.15, 0.30, 0.45, 0.45), "cadj5": ("sala_top", 2.15, 0.85, 0.45, 0.45), "cadj6": ("sala_top", 2.15, 1.40, 0.45, 0.45),
        "bicama": ("q2", 1.75, 0.0, 1.88, 0.88), "aux": ("q2", 1.79, 0.88, 1.80, 0.88),
        "mesa": ("q2", 0.70, 0.0, 1.00, 0.50), "cadeira": ("q2", 1.18, 0.55, 0.45, 0.45),
        "cafe": ("cozinha", 0.0, 0.05, 0.50, 0.80), "cadcafe": ("cozinha", 0.55, 0.20, 0.45, 0.45), "gelad": ("cozinha", 0.0, 1.90, 0.70, 0.70),
        "mesaesc": ("escritorio", 0.0, 0.0, 1.00, 0.45), "camaesc": ("escritorio", 0.775, 0.47, 0.88, 1.88),
    }, extras=(), resumo=[
        "Sala: mesa de jantar em pé (0,90 × 1,60) encostada na entrada, três cadeiras de cada lado; sobra 1,15 m de passagem direta da porta até o hall dos quartos. Sofá na parede do banheiro, TV na parede da cozinha.",
        "Quarto 2: bicama na parede de cima com a cabeceira na janela, mesa entre a porta e a cama (arranjo validado em setembro).",
        "Cozinha: mesa de café junto à porta da entrada (café da manhã perto da luz), geladeira mais para o fundo, perto da lavanderia.",
        "Escritório: cama na parede da direita, mesa deitada na parede de cima; passagem de 0,78 m ao lado da cama."]),
    "C": dict(titulo="Proposta C · sofá menor com poltrona reclinável", overrides={
        "sofa": ("sala_bot", 0.0, 1.9, 0.90, 1.60),
        "jantar": ("sala_top", 1.2, 0.24, 0.90, 1.60),
        "cadj1": ("sala_top", 0.70, 0.30, 0.45, 0.45), "cadj2": ("sala_top", 0.70, 0.85, 0.45, 0.45), "cadj3": ("sala_top", 0.70, 1.40, 0.45, 0.45),
        "cadj4": ("sala_top", 2.15, 0.30, 0.45, 0.45), "cadj5": ("sala_top", 2.15, 0.85, 0.45, 0.45), "cadj6": ("sala_top", 2.15, 1.40, 0.45, 0.45),
        "mesa": ("q2", 0.80, 0.0, 1.00, 0.50), "cadeira": ("q2", 1.18, 0.55, 0.45, 0.45),
        "gelad": ("cozinha", 0.0, 0.05, 0.70, 0.70), "cafe": ("cozinha", 0.0, 1.50, 0.50, 0.80), "cadcafe": ("cozinha", 0.55, 1.65, 0.45, 0.45),
    }, extras=(POLTRONA,), resumo=[
        "Sala: sofá de dois lugares (1,60) mais uma poltrona reclinável na mesma parede da cozinha, os dois de frente para a TV na parede do banheiro. Levantar de uma poltrona com braços é mais fácil aos 60+ do que de um sofá fundo. Jantar em pé como na B.",
        "Quarto 2: bicama na parede de baixo (como na A), mas mesa de computador perto da porta, deixando o canto da janela livre para a luz.",
        "Cozinha: geladeira colada à porta da entrada (compras entram e vão direto para dentro), mesa de café mais para o fundo.",
        "Escritório: igual à A."]),
}


# ---------------------------------------------------------------- validação (mesmas regras da prancheta)
def _r(it):
    return it["x"], it["y"], it["x"] + it["w"], it["y"] + it["h"]


def overlap(a, b):
    return a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"] and a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"]


def in_swing(it, d):
    bx0, bx1 = sorted((d["hx"], d["hx"] + d["sx"] * d["r"])); by0, by1 = sorted((d["hy"], d["hy"] + d["sy"] * d["r"]))
    if not (it["x"] < bx1 and it["x"] + it["w"] > bx0 and it["y"] < by1 and it["y"] + it["h"] > by0):
        return False
    cx = min(max(d["hx"], it["x"]), it["x"] + it["w"]); cy = min(max(d["hy"], it["y"]), it["y"] + it["h"])
    return ((cx - d["hx"]) ** 2 + (cy - d["hy"]) ** 2) ** 0.5 < d["r"]


def grp(it):
    r = it["room"]
    return "sala" if r.startswith("sala") else {"nicho": "banho", "q1alc": "q1"}.get(r, r)


def validar(items):
    by = {it["id"]: it for it in items}
    out = []
    add = lambda ok, t, v=None: out.append((bool(ok), t + (f": {v:.2f} m" if v is not None else "")))
    for it in items:
        if it["fixed"]:
            continue
        for d in P.geo["doors"]:
            if d["room"] == grp(it) and in_swing(it, d):
                add(False, f"{it['label']} está na varredura da porta")
    solid = [i for i in items if not i["dash"] and not i["fixed"] and not i["night"]]
    for i, a in enumerate(solid):
        for b in solid[i + 1:]:
            if {a["id"], b["id"]} & {"box"} and {a["id"], b["id"]} & {"chuveiro", "banco"}:
                continue
            if overlap(a, b):
                add(False, f"{a['label']} sobrepõe {b['label']}")
    q1, q2, st, sb, co, es = R["q1"], R["q2"], R["sala_top"], R["sala_bot"], R["cozinha"], R["escritorio"]
    arm, cama = by["armario"], by["cama"]
    add(cama["x"] - (arm["x"] + arm["w"]) >= 0.65 - 1e-6, "quarto 1: frente do armário até a cama (mín 0,65)", cama["x"] - (arm["x"] + arm["w"]))
    add(q1[0] + q1[2] - (cama["x"] + cama["w"]) >= 0.6 - 1e-6, "quarto 1: passagem do lado da janela (mín 0,60)", q1[0] + q1[2] - (cama["x"] + cama["w"]))
    add(q1[1] + q1[3] - (cama["y"] + cama["h"]) >= 0.6 - 1e-6, "quarto 1: pé da cama (mín 0,60)", q1[1] + q1[3] - (cama["y"] + cama["h"]))
    ae = by["armexist"]; front = 9
    for it in items:
        if it["room"] == "q2" and it["id"] not in ("armexist", "aux") and it["y"] < ae["y"] + ae["h"] and it["y"] + it["h"] > ae["y"] and it["x"] >= ae["x"] + ae["w"] - 1e-6:
            front = min(front, it["x"] - (ae["x"] + ae["w"]))
    add(front >= 0.65 - 1e-6, "quarto 2: frente do armário de correr (mín 0,65)", front)
    mesa = by["mesa"]; free = q2[1] + q2[3] - (mesa["y"] + mesa["h"])
    for it in items:
        if it["room"] == "q2" and it["id"] not in ("mesa", "cadeira", "aux", "armexist") and it["x"] < mesa["x"] + mesa["w"] and it["x"] + it["w"] > mesa["x"] and it["y"] >= mesa["y"] + mesa["h"]:
            free = min(free, it["y"] - (mesa["y"] + mesa["h"]))
    add(free >= 0.75 - 1e-6, "quarto 2: espaço da cadeira à frente da mesa, de dia (mín 0,75)", free)
    sofa, rack = by["sofa"], by["rack"]
    gs = max(rack["x"] - (sofa["x"] + sofa["w"]), sofa["x"] - (rack["x"] + rack["w"]))
    add(gs >= 0.8 - 1e-6, "sala: passagem entre sofá e rack (mín 0,80)", gs)
    top = [i for i in items if i["room"] == "sala_top"]
    add(min(i["x"] for i in top) - st[0] >= 0.6 - 1e-6, "sala: folga entre a boca da entrada e a mesa/cadeiras (mín 0,60)", min(i["x"] for i in top) - st[0])
    add(st[0] + st[2] - max(i["x"] + i["w"] for i in top) >= 0.6 - 1e-6, "sala: passagem da entrada até o hall dos quartos (mín 0,60)", st[0] + st[2] - max(i["x"] + i["w"] for i in top))
    bc = by["bancada"]; gc = co[2] - bc["w"]
    for it in items:
        if it["room"] == "cozinha" and it["id"] not in ("bancada", "piac", "fogao", "cadcafe"):
            gc = min(gc, max(it["x"] - (bc["x"] + bc["w"]), bc["x"] - (it["x"] + it["w"])))
    add(gc >= 0.9 - 1e-6, "cozinha: corredor entre a bancada e geladeira/mesa (mín 0,90)", gc)
    me, ce = by["mesaesc"], by["camaesc"]
    lado = max(ce["x"] - es[0], es[0] + es[2] - (ce["x"] + ce["w"]), ce["y"] - (me["y"] + me["h"]))
    add(lado >= 0.6 - 1e-6, "escritório: passagem livre ao lado da cama (mín 0,60)", lado)
    return out


# ---------------------------------------------------------------- fluxo
ROTAS = [
    ("social", "#5F7355", [(3.95, 0.7), (5.3, 0.85), (7.9, 1.1), (7.9, 2.72), (8.85, 2.72), (8.85, 3.95)]),
    ("q1", "#5F7355", [(8.85, 2.72), (9.75, 2.72)]),
    ("q2", "#5F7355", [(8.85, 3.65), (9.75, 3.65)]),
    ("banho", "#5F7355", [(8.85, 3.95), (8.85, 4.75)]),
    ("varanda", "#A06B3F", [(5.6, 1.5), (5.7, 3.2), (6.2, 5.5), (6.2, 6.5)]),
    ("serviço", "#B93A2B", [(4.04, 1.0), (4.04, 1.7), (3.3, 2.6), (3.3, 4.6), (3.3, 5.6), (2.5, 5.9), (2.15, 5.7)]),
    ("lavabo", "#B93A2B", [(2.5, 5.9), (2.5, 6.9), (2.15, 6.9)]),
]
PINCH = [
    (8.85, 2.35, "hall 0,85 de largura"),
    (7.7, 2.2, "virada para o hall: 1,0 m"),
    (4.04, 1.25, "porta de correr 0,70"),
    (3.3, 5.07, "correr 1,50 p/ lavanderia"),
    (2.15, 5.55, "escritório só pela lavanderia (0,60)"),
    (2.15, 7.1, "lavabo só pela lavanderia (0,60)"),
    (6.2, 5.97, "correr 1,40 p/ varanda"),
    (3.95, 0.3, "entrada 0,83"),
]


def fluxo():
    s = PL.base("Apartamento · mapa de fluxo (rotas diárias e gargalos)")
    for k, nome in PL.NOMES.items():
        if k in ("nicho", "q1alc"):
            continue
        x, y, w, h = R[k]
        s.append(f'<text x="{px(x + 0.08)}" y="{px(y + h - 0.08)}" {MONO} font-size="10" fill="{COL["muted"]}">{nome}</text>')
    for nome, cor, pts in ROTAS:
        d = " ".join(f"{px(x)},{px(y)}" for x, y in pts)
        s.append(f'<polyline points="{d}" fill="none" stroke="{cor}" stroke-width="7" stroke-opacity=".55" stroke-linecap="round" stroke-linejoin="round"/>')
        (x0, y0), (x1, y1) = pts[-2], pts[-1]   # ponta de seta desenhada à mão (marker com context-stroke não sai no PDF)
        import math
        ang = math.atan2(y1 - y0, x1 - x0); X, Y = float(px(x1)), float(px(y1))
        pa = [(X, Y)] + [(X - 12 * math.cos(ang - d_), Y - 12 * math.sin(ang - d_)) for d_ in (0.45, -0.45)]
        s.append(f'<polygon points="{" ".join(f"{a_:.1f},{b_:.1f}" for a_, b_ in pa)}" fill="{cor}" fill-opacity=".8"/>')
    for x, y, t in PINCH:
        s.append(f'<circle cx="{px(x)}" cy="{px(y)}" r="5" fill="{COL["cota"]}"/>')
        s.append(f'<text x="{float(px(x)) + 8:.1f}" y="{float(px(y)) + 4:.1f}" {MONO} font-size="9" fill="{COL["cota"]}">{t}</text>')
    lx = float(px(7.9)); ly = float(px(6.5))
    for i, (t, c) in enumerate((("rota social: entrada → sala → hall → quartos e banheiro", "#5F7355"), ("rota da varanda", "#A06B3F"), ("rota de serviço: entrada → cozinha → lavanderia → escritório e lavabo", "#B93A2B"))):
        s.append(f'<line x1="{lx}" y1="{ly + i * 16}" x2="{lx + 30}" y2="{ly + i * 16}" stroke="{c}" stroke-width="6" stroke-opacity=".55"/>')
        s.append(f'<text x="{lx + 38}" y="{ly + i * 16 + 4}" {MONO} font-size="9" fill="{COL["muted"]}">{t}</text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------------------------------------------------------------- elétrica
# (cômodo, x, y relativos ao canto interno, tipo, circuito)
CIRC = {
    1: ("Iluminação social", "sala, entrada, hall, quartos, escritório", "1,5 mm² · 10 A"),
    2: ("Iluminação serviço", "cozinha, lavanderia, banheiro, lavabo, varanda", "1,5 mm² · 10 A"),
    3: ("Tomadas quartos e escritório", "TUG", "2,5 mm² · 16 A"),
    4: ("Tomadas sala, hall e varanda", "TUG", "2,5 mm² · 16 A"),
    5: ("Tomadas da bancada da cozinha", "TUG, 3 pontos acima da bancada", "2,5 mm² · 20 A"),
    6: ("Tomadas áreas molhadas", "lavanderia, lavabo, banheiro (DR 30 mA)", "2,5 mm² · 20 A"),
    7: ("Geladeira", "TUE, tomada exclusiva", "2,5 mm² · 16 A"),
    8: ("Micro-ondas / forno elétrico", "TUE, na bancada", "2,5 mm² · 20 A"),
    9: ("Máquina de lavar", "TUE, lavanderia", "2,5 mm² · 20 A"),
    10: ("Chuveiro elétrico", "TUE, 5.500 a 7.500 W, DR 30 mA", "6,0 mm² · 40 A (220 V) ou 10 mm² (127 V)"),
    11: ("Ar-condicionado quarto 1", "TUE, ponto alto na parede da janela", "2,5 mm² · 16 A"),
    12: ("Ar-condicionado quarto 2 / sala (reserva)", "TUE, deixar eletroduto e espaço no quadro", "2,5 mm² · 16 A"),
    13: ("Secadora de roupas", "TUE, tomada ao lado da lavadora, a 1,60 m (máquina de cima da torre)", "4,0 mm² · 25 A"),
}
PONTOS = [
    ("cozinha", 2.16, 0.04, "Q", 0), ("cozinha", 2.30, 0.70, "T", 5), ("cozinha", 2.30, 1.60, "T", 5), ("cozinha", 2.30, 3.10, "T", 5),
    ("cozinha", 2.30, 2.50, "E", 8), ("cozinha", 0.04, 1.30, "E", 7), 
    ("cozinha", 1.70, 0.06, "S", 2), ("cozinha", 2.30, 1.10, "X", 2),
    ("lavanderia", 2.32, 1.05, "E", 9), ("lavanderia", 2.32, 1.35, "E", 13), ("lavanderia", 2.32, 1.80, "T", 6), ("lavanderia", 0.55, 0.06, "S", 2),
    ("lavabo", 1.25, 0.04, "T", 6), ("lavabo", 1.57, 0.50, "S", 2),
    ("escritorio", 0.04, 0.70, "T", 3), ("escritorio", 1.61, 1.10, "T", 3), ("escritorio", 0.70, 2.93, "T", 3), ("escritorio", 1.35, 2.90, "S", 1),
    ("banho", 0.35, 0.04, "T", 6), ("banho", 1.40, 0.10, "S", 2), ("banho", 0.15, 1.10, "C", 10), ("banho", 0.83, 1.45, "X", 2),
    ("q1", 0.50, 0.04, "T", 3), ("q1", 3.15, 0.04, "T", 3), ("q1", 1.80, 2.74, "T", 3), ("q1", 3.59, 1.90, "T", 3), ("q1", 3.55, 0.30, "A", 11),
    ("q1", 0.80, 2.72, "S", 1), ("q1", 1.00, 0.06, "s", 1), ("q1", 2.62, 0.06, "s", 1),
    ("q2", 0.90, 0.04, "T", 3), ("q2", 3.45, 0.04, "T", 3), ("q2", 3.59, 1.20, "T", 3), ("q2", 0.90, 2.74, "T", 3), ("q2", 3.55, 2.50, "A", 12),
    ("q2", 0.78, 0.06, "S", 1), ("q2", 3.40, 2.72, "s", 1),
    ("sala_top", 0.20, 0.04, "T", 4), ("sala_top", 1.90, 0.04, "T", 4), ("sala_top", 3.70, 0.60, "T", 4), ("sala_top", 0.06, 1.35, "S", 1),
    ("sala_bot", 0.04, 0.90, "T", 4), ("sala_bot", 2.69, 3.30, "T", 4), ("sala_bot", 2.69, 2.40, "T", 4), ("sala_bot", 0.20, 3.48, "T", 4), 
    ("hall", 0.06, 0.30, "s", 1), 
    ("entrada", 1.44, 0.40, "S", 1),
    ("varanda", 0.10, 0.55, "T", 4), ("varanda", 2.40, 0.06, "S", 2),
]
TIPOS = dict(Q="quadro de distribuição (QDC)", T="tomada 2P+T (TUG), a 0,40 a 1,10 m do piso", E="tomada de uso específico (TUE)",
             L="ponto de luz no teto", l="luz auxiliar (LED de bancada, luz de vigília com sensor)", S="interruptor a 1,00 m",
             s="interruptor paralelo (cabeceira ou segunda porta)", X="exaustor", C="ponto do chuveiro elétrico", A="ponto do ar-condicionado")
CORC = {1: "#2E6F9E", 2: "#2E6F9E", 3: "#4E7A52", 4: "#4E7A52", 5: "#4E7A52", 6: "#4E7A52", 7: "#B93A2B", 8: "#B93A2B", 9: "#B93A2B",
        10: "#B93A2B", 11: "#B93A2B", 12: "#B93A2B", 13: "#B93A2B", 0: "#1c1a17"}


def simbolo(s, X, Y, tipo, circ):
    c = CORC[circ]
    if tipo == "Q":
        s.append(f'<rect x="{X - 4}" y="{Y - 2}" width="18" height="28" fill="#fff" stroke="{c}" stroke-width="2"/>'
                 f'<text x="{X + 5}" y="{Y + 16}" {MONO} font-size="8" font-weight="700" fill="{c}" text-anchor="middle">QDC</text>')
    elif tipo in "TE":
        s.append(f'<circle cx="{X}" cy="{Y}" r="5" fill="{"#fff" if tipo == "T" else c}" stroke="{c}" stroke-width="1.6"/>')
    elif tipo == "L":
        s.append(f'<circle cx="{X}" cy="{Y}" r="6" fill="#fff" stroke="{c}" stroke-width="1.4"/>'
                 f'<path d="M{X - 4},{Y - 4} L{X + 4},{Y + 4} M{X - 4},{Y + 4} L{X + 4},{Y - 4}" stroke="{c}" stroke-width="1.4"/>')
    elif tipo == "l":
        s.append(f'<circle cx="{X}" cy="{Y}" r="4" fill="{c}" fill-opacity=".35" stroke="{c}" stroke-width="1.2"/>')
    elif tipo in "Ss":
        s.append(f'<rect x="{X - 5}" y="{Y - 5}" width="10" height="10" fill="#fff" stroke="{c}" stroke-width="1.4"/>'
                 f'<text x="{X}" y="{Y + 3}" {MONO} font-size="7" fill="{c}" text-anchor="middle">{"S" if tipo == "S" else "Sp"}</text>')
    elif tipo == "X":
        s.append(f'<circle cx="{X}" cy="{Y}" r="6" fill="none" stroke="{c}" stroke-width="1.4"/><text x="{X}" y="{Y + 3}" {MONO} font-size="7" fill="{c}" text-anchor="middle">ex</text>')
    elif tipo == "C":
        s.append(f'<path d="M{X - 6},{Y + 5} L{X},{Y - 6} L{X + 6},{Y + 5} Z" fill="{c}" fill-opacity=".25" stroke="{c}" stroke-width="1.6"/>')
    elif tipo == "A":
        s.append(f'<rect x="{X - 8}" y="{Y - 4}" width="16" height="8" fill="{c}" fill-opacity=".25" stroke="{c}" stroke-width="1.4"/><text x="{X}" y="{Y + 2.5}" {MONO} font-size="6" fill="{c}" text-anchor="middle">AC</text>')
    if circ and tipo not in "Ll":
        s.append(f'<text x="{X + 7}" y="{Y - 5}" {MONO} font-size="7" fill="{c}">{circ}</text>')


def eletrica():
    s = PL.base("Apartamento · proposta de elétrica (quadro na cozinha, junto à porta da entrada)")
    for k, nome in PL.NOMES.items():
        if k in ("nicho", "q1alc"):
            continue
        x, y, w, h = R[k]
        s.append(f'<text x="{px(x + 0.08)}" y="{px(y + h - 0.08)}" {MONO} font-size="10" fill="{COL["muted"]}">{nome}</text>')
    # móveis da proposta A em cinza bem claro, só de referência
    for it in P.ITEMS:
        if it["night"] or it["dash"]:
            continue
        s.append(f'<rect x="{px(it["x"])}" y="{px(it["y"])}" width="{it["w"] * PX:.1f}" height="{it["h"] * PX:.1f}" fill="#000" fill-opacity=".05" stroke="#000" stroke-opacity=".15"/>')
    for room, x, y, tipo, circ in PONTOS:
        rx, ry = R[room][0] + x, R[room][1] + y
        simbolo(s, float(px(rx)), float(px(ry)), tipo, circ)
    lx = float(px(7.9)); ly = float(px(6.45))
    for i, (t, c) in enumerate((("azul: iluminação (circuitos 1 e 2)", "#2E6F9E"), ("verde: tomadas de uso geral (3 a 6)", "#4E7A52"), ("vermelho: uso específico (7 a 12)", "#B93A2B"))):
        s.append(f'<text x="{lx}" y="{ly + i * 14}" {MONO} font-size="9" fill="{c}">{t}</text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------------------------------------------------------------- iluminação
# lux alvo por ambiente (NBR ISO/CIE 8995-1, reforçado onde 60+ pede) e pontos de luz
LUZ = {
    "sala_top":   dict(nome="Sala · jantar", lux=200, k=3000, pts=[(1.87, 1.04, "pendente sobre a mesa, 2 lâmpadas")]),
    "sala_bot":   dict(nome="Sala · estar", lux=200, k=2700, pts=[(1.36, 1.2, "plafon"), (1.36, 2.6, "plafon"), (0.5, 3.35, "abajur ou arandela junto ao sofá (leitura)")]),
    "entrada":    dict(nome="Entrada", lux=150, k=3000, pts=[(0.75, 0.44, "plafon")]),
    "hall":       dict(nome="Hall dos quartos", lux=150, k=3000, pts=[(0.43, 0.88, "plafon"), (0.1, 1.6, "luz de vigília com sensor, 3 W")]),
    "cozinha":    dict(nome="Cozinha", lux=300, k=4000, pts=[(1.18, 1.0, "plafon"), (1.18, 2.7, "plafon"), (1.95, 2.0, "fita LED sob os aéreos, 3 m (500 lx na bancada)")]),
    "lavanderia": dict(nome="Lavanderia", lux=300, k=4000, pts=[(1.18, 1.04, "plafon")]),
    "lavabo":     dict(nome="Lavabo", lux=200, k=3000, pts=[(0.83, 0.49, "plafon"), (0.98, 0.15, "arandela no espelho 4000 K")]),
    "escritorio": dict(nome="Quarto/escritório", lux=300, k=3000, pts=[(0.83, 1.48, "plafon"), (0.25, 0.3, "luminária de mesa 4000 K")]),
    "banho":      dict(nome="Banheiro", lux=300, k=3000, pts=[(0.83, 0.5, "plafon IP44"), (0.5, 1.3, "plafon IP65 no box"), (0.25, 0.1, "arandela no espelho 4000 K")]),
    "q1":         dict(nome="Quarto 1", lux=150, k=2700, pts=[(1.82, 1.39, "plafon"), (0.9, 0.2, "arandela de cabeceira"), (2.75, 0.2, "arandela de cabeceira")]),
    "q2":         dict(nome="Quarto 2", lux=150, k=2700, pts=[(1.82, 1.39, "plafon"), (2.0, 2.6, "arandela de cabeceira"), (3.1, 0.25, "luminária de mesa 4000 K")]),
    "varanda":    dict(nome="Varanda", lux=100, k=2700, pts=[(1.36, 0.55, "plafon IP44")]),
}
# pontos de luz da elétrica saem do mapa de iluminação: plafon/pendente = "L" (circuito 1 social, 2 serviço), auxiliar = "l"
_SERVICO = {"cozinha", "lavanderia", "banho", "lavabo", "varanda"}
for _k, _d in LUZ.items():
    for _x, _y, _t in _d["pts"]:
        PONTOS.append((_k, _x, _y, "L" if _t.startswith(("plafon", "pendente")) else "l", 2 if _k in _SERVICO else 1))

LAMP = [(806, "9 W"), (1100, "12 W"), (1500, "15 W"), (2000, "plafon LED 18 W"), (2400, "plafon LED 24 W"), (3200, "plafon LED 32 W"), (4000, "painel LED 40 W")]   # lúmens → produto


def calc_luz():
    """Lúmens necessários = lux × área ÷ 0,5 (teto claro, luminária difusa); divididos entre os plafons."""
    linhas = []
    for k, d in LUZ.items():
        x, y, w, h = R[k]
        area = w * h
        lm = d["lux"] * area / 0.5
        n = max(1, sum(1 for p in d["pts"] if p[2].startswith(("plafon", "pendente"))))
        por = lm / n
        lamp = next((f"{w_} ({l} lm)" for l, w_ in LAMP if l >= por), "2 × painel LED 40 W")
        linhas.append(dict(k=k, nome=d["nome"], area=area, lux=d["lux"], lm=lm, n=n, lamp=lamp, k_=d["k"], pts=d["pts"]))
    return linhas


def iluminacao():
    s = PL.base("Apartamento · mapa de iluminação (pontos, potência e temperatura de cor)")
    for it in P.ITEMS:
        if it["night"] or it["dash"]:
            continue
        s.append(f'<rect x="{px(it["x"])}" y="{px(it["y"])}" width="{it["w"] * PX:.1f}" height="{it["h"] * PX:.1f}" fill="#000" fill-opacity=".05" stroke="#000" stroke-opacity=".15"/>')
    for l in calc_luz():
        x, y, w, h = R[l["k"]]
        cor = "#D9A441" if l["k_"] <= 2700 else ("#C98A2E" if l["k_"] == 3000 else "#4A90B8")
        s.append(f'<text x="{px(x + 0.08)}" y="{px(y + h - 0.08)}" {MONO} font-size="8" fill="{COL["muted"]}">{l["nome"]} · {l["lux"]} lx · {l["k_"]} K</text>')
        for (ax, ay, t) in l["pts"]:
            X, Y = float(px(x + ax)), float(px(y + ay))
            if t.startswith(("plafon", "pendente")):
                s.append(f'<circle cx="{X}" cy="{Y}" r="14" fill="{cor}" fill-opacity=".25" stroke="{cor}" stroke-width="2"/>'
                         f'<text x="{X}" y="{Y + 3}" {MONO} font-size="7" fill="{COL["ink"]}" text-anchor="middle">{l["lamp"].split(" (")[0]}</text>')
            elif t.startswith("fita"):
                s.append(f'<rect x="{X - 3}" y="{Y - 60}" width="6" height="120" fill="#4A90B8" fill-opacity=".5"/>')
            else:
                c2 = "#4A90B8" if "4000" in t else cor
                s.append(f'<circle cx="{X}" cy="{Y}" r="6" fill="{c2}" fill-opacity=".5" stroke="{c2}" stroke-width="1.5"/>')
    lx = float(px(7.9)); ly = float(px(6.45))
    for i, (t, c) in enumerate((("2700 K: quartos, estar, varanda (relaxar)", "#D9A441"), ("3000 K: jantar, circulação, banheiro, escritório", "#C98A2E"), ("4000 K: cozinha, lavanderia, espelhos, mesas de trabalho", "#4A90B8"))):
        s.append(f'<circle cx="{lx + 6}" cy="{ly + i * 14 - 3}" r="5" fill="{c}" fill-opacity=".5" stroke="{c}"/><text x="{lx + 16}" y="{ly + i * 14}" {MONO} font-size="9" fill="{COL["muted"]}">{t}</text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------------------------------------------------------------- lista de compras da elétrica
def compras():
    qx, qy = R["cozinha"][0] + 2.16, R["cozinha"][1] + 0.04
    cont, metros = {}, {}
    for room, x, y, tipo, circ in PONTOS:
        cont[tipo] = cont.get(tipo, 0) + 1
        if circ:
            d = abs(R[room][0] + x - qx) + abs(R[room][1] + y - qy) + 2 * 2.6   # pelo teto: sobe e desce o pé-direito
            metros[circ] = max(metros.get(circ, 0), d)
    luz = calc_luz()
    n_plafon = sum(l["n"] for l in luz)
    n_aux = sum(len(l["pts"]) - l["n"] for l in luz)
    cabo = {}
    for c, d in metros.items():
        bit = CIRC[c][2].split("·")[0].strip()
        cabo[bit] = cabo.get(bit, 0) + round(d * 1.3 * 3 + 5)   # fase, neutro e terra, 30 % de folga
    n_cx = int((cont.get("T", 0) + cont.get("E", 0) + cont.get("S", 0) + cont.get("s", 0)) * 1.2)
    compras.cont, compras.cabo, compras.n_plafon, compras.n_cx = cont, cabo, n_plafon, n_cx
    linhas = [
        ("Quadro de distribuição de embutir, 24 espaços DIN, com barramento de neutro e terra", "1 un"),
        ("Disjuntor geral bipolar 50 A (confirmar com a carga instalada e a concessionária)", "1 un"),
        ("Disjuntores DIN: 10 A (2), 16 A (5), 20 A (4), 25 A (1, secadora), 40 A bipolar (chuveiro)", "13 un"),
        ("Interruptor DR 30 mA: 40 A para áreas molhadas e 63 A para o chuveiro", "2 un"),
        ("DPS classe II, 20 kA (um por fase e um no neutro)", "2 a 3 un"),
        ("Tomadas 2P+T 10 A padrão NBR 14136, com espelho", f"{cont.get('T', 0)} un"),
        ("Tomadas 2P+T 20 A (geladeira, micro-ondas, lavadora e secadora, lado a lado na torre)", f"{cont.get('E', 0)} un"),
        ("Interruptores simples", f"{cont.get('S', 0)} un"),
        ("Interruptores paralelos (three-way)", f"{cont.get('s', 0)} un"),
        ("Sensores de presença (hall e lavabo)", "2 un"),
        ("Kit do chuveiro: caixa, conector de porcelana e disjuntor dedicado", "1 un"),
        ("Pontos de ar-condicionado: caixa 4×2 alta e eletroduto até a condensadora", f"{cont.get('A', 0)} un"),
        ("Caixas 4×2 de embutir (tomadas e interruptores, com 20 % de sobra)", f"{n_cx} un"),
        ("Caixas octogonais de teto (pontos de luz)", f"{n_plafon + 2} un"),
        ("Plafons e pendente LED de teto, com difusor", f"{n_plafon} un"),
        ("Arandelas, luminárias de mesa, luz de vigília e fita LED (pontos auxiliares)", f"{n_aux} un"),
        ("Lâmpadas LED E27, 9 a 15 W, IRC ≥ 90, nas cores do mapa de iluminação", f"{n_plafon + 5} un"),
        ("Eletroduto corrugado 25 mm (tomadas, chuveiro, ar)", f"{int(sum(v for k, v in cabo.items() if '1,5' not in k) / 3 * 0.6)} m"),
        ("Eletroduto corrugado 20 mm (iluminação)", f"{int(cabo.get('1,5 mm²', 0) / 3 * 0.6)} m"),
    ] + [(f"Cabo flexível {k}: fase, neutro e terra (cores da norma: vermelho ou preto, azul, verde)", f"{v} m") for k, v in sorted(cabo.items())] + [
        ("Fita isolante, conectores, abraçadeiras, gesso e massa para fechar os rasgos", "verba"),
    ]
    return linhas


def tabela_luz():
    tr = "".join(f"<tr><td>{l['nome']}</td><td>{l['area']:.1f} m²</td><td>{l['lux']} lx</td><td>{l['lm']:.0f} lm</td><td>{l['n']} × {l['lamp']}</td><td>{l['k_']} K</td><td>{'; '.join(p[2] for p in l['pts'] if not p[2].startswith(('plafon', 'pendente')))}</td></tr>" for l in calc_luz())
    return f"<table><tr><th>ambiente</th><th>área</th><th>lux alvo</th><th>lúmens</th><th>teto</th><th>cor</th><th>luz auxiliar</th></tr>{tr}</table>"


# ---------------------------------------------------------------- preços (pesquisa web 08/09/2026)
# (item, quantidade, unidade, preço médio unitário R$, faixa, onde)
PRECO_ELETRICA = [
    ("Quadro de embutir 24 DIN com barramentos", 1, "un", 200, "90 a 320", "Leroy Merlin / Magalu"),
    ("Disjuntor geral bipolar 50 A", 1, "un", 45, "32 a 75", "Magalu / Leroy Merlin"),
    ("Disjuntores DIN 10/16/20/25 A", 12, "un", 15, "9 a 25", "Leroy Merlin / Ferreira Costa"),
    ("Disjuntor bipolar 40 A (chuveiro)", 1, "un", 40, "30 a 55", "Leroy Merlin"),
    ("DR 2P 40 A 30 mA + DR 2P 63 A 30 mA", 2, "un", 180, "110 a 260", "Leroy Merlin / Telhanorte"),
    ("DPS classe II 20 kA", 3, "un", 55, "40 a 80", "Leroy Merlin / Telhanorte"),
    ("Tomada 2P+T 10 A com espelho (Tramontina Liz)", None, "un", 18, "12 a 30", "Magalu / Leroy Merlin"),
    ("Tomada 2P+T 20 A com espelho", None, "un", 15, "13 a 20", "Redemac / Kennedy"),
    ("Interruptor simples", None, "un", 13, "11 a 16", "Magalu"),
    ("Interruptor paralelo", None, "un", 20, "15 a 22", "Tramontina / Magalu"),
    ("Sensor de presença de teto 360°", 2, "un", 50, "36 a 62", "Leroy Merlin"),
    ("Kit do ponto do chuveiro (caixa, conector, fita)", 1, "un", 40, "25 a 60", "Leroy Merlin"),
    ("Ponto de ar-condicionado (caixa alta + eletroduto)", 2, "un", 30, "20 a 50", "Leroy Merlin"),
    ("Caixa 4×2 de embutir", None, "un", 4, "2 a 7", "Magalu / Casas Bahia"),
    ("Caixa octogonal 4×4", None, "un", 10, "9 a 12", "Casas São Pedro"),
    ("Eletroduto corrugado 25 mm", None, "m", 2.2, "rolo 50 m: 75 a 160", "Ferreira Costa / Leroy Merlin"),
    ("Eletroduto corrugado 20 mm", None, "m", 1.6, "rolo 50 m: 50 a 120", "Ferreira Costa / Leroy Merlin"),
    ("Cabo flexível 1,5 mm²", None, "m", 1.6, "rolo 100 m: 120 a 210", "Leroy Merlin / Cobrecom"),
    ("Cabo flexível 2,5 mm²", None, "m", 2.7, "rolo 100 m: 260 a 320", "Casas São Pedro"),
    ("Cabo flexível 4,0 mm² (secadora)", None, "m", 4.2, "rolo 100 m: ~420", "estimado pela faixa 2,5 a 6,0"),
    ("Cabo flexível 6,0 mm² (chuveiro)", None, "m", 6.0, "rolo 100 m: 250 a 800", "Leroy Merlin / Tokled"),
    ("Miudezas: fita, conectores, abraçadeiras, gesso", 1, "verba", 300, "200 a 500", ""),
]
PRECO_LUZ = [
    ("Plafon LED sobrepor 18 W 2700 K (estar)", 2, "un", 35, "25 a 50", "Leroy Merlin / Magalu"),
    ("Plafon LED sobrepor 32 W (jantar, cozinha ×2, lavanderia, escritório, quartos ×2)", 7, "un", 120, "90 a 194", "Mercado Livre / Yamamura"),
    ("Plafon LED IP44 (banheiro, varanda)", 2, "un", 80, "60 a 130", "Leroy Merlin / marketplaces"),
    ("Luminária LED IP65 (dentro do box)", 1, "un", 70, "60 a 110", "Magalu / Leroy Merlin"),
    ("Plafon LED 9 W (entrada, hall, lavabo)", 3, "un", 30, "20 a 40", "Leroy Merlin"),
    ("Arandela LED de cabeceira (quartos ×3, sofá)", 4, "un", 110, "80 a 180", "Leroy Merlin / Amazon"),
    ("Arandela de espelho 4000 K 40 cm (banheiro, lavabo)", 2, "un", 130, "100 a 220", "Amazon / Mercado Livre"),
    ("Luminária de mesa LED 4000 K (escritório, quarto 2)", 2, "un", 120, "80 a 180", "Mercado Livre"),
    ("Fita LED 4000 K 5 m 12 V com fonte + 3 perfis de 1 m", 1, "kit", 240, "180 a 340", "Leroy Merlin / Shopee"),
    ("Luz de vigília LED com sensor (hall)", 1, "un", 50, "30 a 80", "Amazon"),
    ("Dimmer rotativo para LED (estar, quartos)", 3, "un", 80, "60 a 150", "Mercado Livre"),
    ("Lâmpadas LED E27 9 a 12 W IRC 90 (reserva e arandelas)", 12, "un", 12, "8 a 20", "Magalu / Amazon"),
]
# móveis: id do item na prancheta → (nome de compra, preço médio, faixa, onde, medidas)
PRECO_MOVEIS = {
    "sofa":     ("Sofá 3 lugares retrátil 2,10 × 0,90", 1900, "1.900 a 2.400", "Casas Bahia / Madeira Madeira", "200 a 210 cm"),
    "sofa160":  ("Sofá 2 lugares 1,60 × 0,90 (linho)", 2200, "1.800 a 3.400", "Leroy Merlin / Madeira Madeira", "160 × 90 cm"),
    "poltrona": ("Poltrona do papai reclinável com braços 0,80", 1400, "740 a 2.000", "Magalu / Amazon", "80 × 94 cm"),
    "rack":     ("Rack para TV 1,80 × 0,40", 750, "600 a 900", "Magalu (Caemmun)", "180 × 39,5 cm"),
    "jantar":   ("Mesa de jantar 6 lugares 1,60 × 0,90", 1260, "1.120 a 1.460", "Magalu / Madeira Madeira", "160 × 90 cm"),
    "cadj":     ("Jogo de 6 cadeiras de jantar estofadas", 1250, "1.000 a 1.900", "Magalu / Madeira Madeira", "45 × 55 cm"),
    "cama":     ("Cama box queen 1,58 × 1,98 com colchão de molas ensacadas", 2500, "2.000 a 3.800", "Magalu / Casas Bahia", "158 × 198 cm"),
    "cabec":    ("Cabeceira queen estofada 1,58", 450, "180 a 800", "Magalu / Casas Bahia", "158 cm"),
    "criado":   ("Par de criados-mudos 0,40 × 0,40 com gaveta", 260, "180 a 350", "Magalu / Mobly", "40 × 40 cm"),
    "bicama":   ("Bicama solteiro 0,88 × 1,88 com auxiliar + 2 colchões D33", 2100, "1.050 a 2.900", "Magalu / Madeira Madeira", "88 × 188 cm"),
    "mesa":     ("Escrivaninha 1,00 × 0,50 (quarto 2)", 250, "180 a 350", "Magalu / Madeira Madeira", "100 × 50 cm"),
    "cadeira":  ("Cadeira de escritório ergonômica com braços", 550, "400 a 1.300", "Magalu / Mercado Livre", ""),
    "cafe":     ("Mesa de café 0,80 × 0,50 com 2 banquetas", 580, "500 a 700", "Madeira Madeira", "80 × 50 cm"),
    "mesaesc":  ("Escrivaninha 1,00 × 0,45 (escritório)", 250, "180 a 350", "Magalu / Madeira Madeira", "100 × 45 cm"),
    "camaesc":  ("Cama box solteiro 0,88 × 1,88 com colchão", 1000, "800 a 1.500", "Magalu / Madeira Madeira", "88 × 188 cm"),
    "mesav":    ("Conjunto de varanda: mesa 0,60 × 0,60 + 2 cadeiras", 500, "300 a 700", "Magalu / Madeira Madeira", "60 × 60 cm"),
}
JA_TEM = ["Lavadora e secadora (torre)", "Geladeira", "Fogão", "Armários dos quartos e bancada da cozinha"]
PRECO_BANHO = [
    ("Box de vidro temperado 8 mm frontal 1,66 com porta de correr, instalado", 1, "un", 1200, "900 a 1.500", "vidraceiro"),
    ("Vaso sanitário caixa acoplada altura conforto 46 cm (Deca/Celite)", 1, "un", 1500, "900 a 2.000", "Telhanorte / Leroy Merlin"),
    ("Cuba semi-encaixe 0,60 × 0,45 com gabinete", 1, "un", 1400, "900 a 2.000", "Leroy Merlin / Telhanorte"),
    ("Torneira monocomando de alavanca", 1, "un", 350, "250 a 700", "Leroy Merlin / Amazon"),
    ("Chuveiro elétrico 7.500 W (Lorenzetti Acqua Duo ou similar)", 1, "un", 350, "250 a 500", "Amazon / Mercado Livre"),
    ("Ducha manual com barra deslizante", 1, "un", 200, "130 a 350", "Leroy Merlin"),
    ("Barra de apoio inox 0,60 (×2) e 0,80 (×1)", 3, "un", 170, "120 a 280", "Obramax / Leroy Merlin"),
    ("Banco articulado de parede para o box (NBR 9050)", 1, "un", 1000, "900 a 1.200", "loja de acessibilidade"),
    ("Ralo linear inox 0,60", 1, "un", 220, "160 a 350", "Leroy Merlin"),
    ("Porcelanato antiderrapante R10 60×60, 3,5 m² + 10 %", 4, "m²", 90, "70 a 120", "Leroy Merlin / Telhanorte"),
    ("Revestimento de parede cerâmico, ~18 m²", 18, "m²", 45, "25 a 60", "Leroy Merlin / Telhanorte"),
    ("Impermeabilização da área molhada (material + aplicação)", 4, "m²", 60, "40 a 90", "prestador"),
    ("Exaustor 150 mm", 1, "un", 250, "180 a 400", "Leroy Merlin / Amazon"),
    ("Espelho 60×80 com LED", 1, "un", 450, "300 a 800", "Leroy Merlin / Amazon"),
    ("Assento sanitário elevado (se o vaso não for de altura conforto)", 0, "un", 200, "120 a 350", "Mercado Livre"),
    ("Mão de obra: pedreiro + encanador + eletricista do banheiro (2 a 3 semanas)", 1, "verba", 6500, "5.000 a 8.000", "estimativa regional"),
    ("Hidráulica extra da versão 1 (vaso no nicho: rasgo, tubo 100 mm, caimento)", 1, "verba", 2000, "1.500 a 3.000", "só se a vistoria liberar"),
]


def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def qtd_compras():
    """Quantidades calculadas em compras(), indexadas pelo começo do nome do item de preço."""
    compras()
    c, cabo = compras.cont, compras.cabo
    m = lambda k: cabo.get(k, 0)
    return {"Tomada 2P+T 10 A": c.get("T", 0), "Tomada 2P+T 20 A": c.get("E", 0), "Interruptor simples": c.get("S", 0),
            "Interruptor paralelo": c.get("s", 0), "Caixa 4×2": compras.n_cx, "Caixa octogonal": compras.n_plafon + 2,
            "Eletroduto corrugado 25": int(sum(v for k, v in cabo.items() if "1,5" not in k) / 3 * 0.6),
            "Eletroduto corrugado 20": int(m("1,5 mm²") / 3 * 0.6),
            "Cabo flexível 1,5": m("1,5 mm²"), "Cabo flexível 2,5": m("2,5 mm²"), "Cabo flexível 4,0": m("4,0 mm²"), "Cabo flexível 6,0": m("6,0 mm²")}


def tabela_preco(linhas, qmap=None):
    total = 0
    tr = ""
    for nome, qtd, un, preco, faixa, onde in linhas:
        if qtd is None:
            qtd = next((v for k, v in (qmap or {}).items() if nome.startswith(k)), 0)
        sub = qtd * preco
        total += sub
        tr += f"<tr><td>{nome}</td><td>{qtd} {un}</td><td>{brl(preco)}</td><td class='muted'>{faixa}</td><td>{brl(sub)}</td><td class='muted'>{onde}</td></tr>"
    tr += f"<tr><th colspan='4'>total estimado</th><th>{brl(total)}</th><th></th></tr>"
    return f"<table><tr><th>item</th><th>qtd</th><th>unit. médio</th><th>faixa</th><th>subtotal</th><th>onde</th></tr>{tr}</table>", total


def moveis_proposta(k):
    ids = ["rack", "jantar", "cadj", "cama", "cabec", "criado", "bicama", "mesa", "cadeira", "cafe", "mesaesc", "camaesc", "mesav"]
    ids = (["sofa160", "poltrona"] if k == "C" else ["sofa"]) + ids
    return [(PRECO_MOVEIS[i][0], 1, "un", PRECO_MOVEIS[i][1], PRECO_MOVEIS[i][2], PRECO_MOVEIS[i][3]) for i in ids]


# ---------------------------------------------------------------- página
def fig(svg, cap):
    svg = svg.replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;border-radius:10px;border:1px solid #DDD5C7"')
    return f'<figure class="schema">{svg}<figcaption>{cap}</figcaption></figure>'


def pagina(figs, checks):
    q = qtd_compras()
    TAB_ELE, TOT_ELE = tabela_preco(PRECO_ELETRICA, q)
    TAB_LUZ, TOT_LUZ = tabela_preco(PRECO_LUZ)
    TAB_MOV_A, TOT_MOV_A = tabela_preco(moveis_proposta("A"))
    TAB_MOV_C, TOT_MOV_C = tabela_preco(moveis_proposta("C"))
    TAB_BANHO, TOT_BANHO = tabela_preco(PRECO_BANHO)
    css = open(os.path.join(os.path.dirname(OUT), "templates", "base_head.html"), encoding="utf-8").read()
    props = ""
    for k, pr in PROPOSTAS.items():
        li = "".join(f"<li>{t}</li>" for t in pr["resumo"])
        ch = "".join(f'<li class="{"ok" if ok else "bad"}"><b>{"OK" if ok else "!!"}</b> {t}</li>' for ok, t in checks[k])
        props += f'''<section id="prop{k}"><hr class="rule"><p class="eyebrow">Proposta {k}</p><h2>{pr["titulo"].split("·", 1)[1].strip().capitalize()}</h2>
<ul class="lista-solta">{li}</ul>{figs["proposta_" + k]}
<details open><summary class="muted">Checagens do simulador ({sum(1 for ok, _ in checks[k] if ok)}/{len(checks[k])} aprovadas)</summary><ul class="checks">{ch}</ul></details></section>'''
    circ = "".join(f"<tr><td>{n}</td><td>{a}</td><td>{b}</td><td class='cota'>{c}</td></tr>" for n, (a, b, c) in CIRC.items())
    leg = "".join(f"<li><b>{k}</b> {v}</li>" for k, v in TIPOS.items())
    return f'''<title>Propostas e Elétrica</title>
{css}
<style>
  .checks{{list-style:none;padding:0;margin:8px 0 0}} .checks li{{font-size:.85rem;padding:3px 0;border-bottom:1px solid var(--line)}} .checks b{{font-family:"IBM Plex Mono",monospace}}
  .ok b{{color:var(--ok)}} .bad b{{color:var(--cota)}} details summary{{cursor:pointer;font-size:.9rem}}
  table{{border-collapse:collapse;width:100%;font-size:.9rem;margin:12px 0}} th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}} th{{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--wood)}}
  .leg{{columns:2;font-size:.85rem;padding-left:1.1em}} .leg b{{font-family:"IBM Plex Mono",monospace}}
  @page{{size:A4 landscape;margin:12mm}} @media print{{body{{background:#fff;padding:0;font-size:11.5px;line-height:1.45}} .wrap{{max-width:none}} section{{margin-top:0;break-before:page}} section:first-of-type{{break-before:auto}} header{{padding:0 0 8px}} h2,h3,h4,.eyebrow{{break-after:avoid-page;break-inside:avoid}} h2{{margin-top:0}} h3{{margin-top:14px}} p,li{{orphans:3;widows:3}} .eyebrow+h2+p,.eyebrow+h2+ul{{break-before:avoid-page}} .schema{{break-inside:avoid;break-before:avoid-page;margin:6px 0}} .schema svg{{max-height:92mm;width:auto;max-width:100%;margin:0 auto}} table{{break-inside:auto}} tr{{break-inside:avoid}} thead{{display:table-header-group}} th{{white-space:nowrap}} .callout,.check{{break-inside:avoid;padding:10px 14px;margin:10px 0}} details{{display:block}} details>*:not(summary){{display:none}} details summary{{list-style:none}} .leg{{columns:3}} .pg{{break-before:page}} .checks{{columns:2;font-size:.72rem;column-gap:18px}} .checks li{{padding:1px 0;break-inside:avoid}} details summary{{font-size:.8rem;margin-top:4px}} .lista-solta li{{margin-bottom:.15em}} h3+table,h3+p,h4+table{{break-before:avoid-page}}}}
</style>
<div class="wrap">
<header><p class="eyebrow">Plano de reforma · rev. 07/09/2026</p><h1>Fluxo, três propostas e elétrica</h1>
<p class="standfirst">Obra de estrutura e piso só no banheiro; no resto do apartamento muda a posição dos móveis e a elétrica. As três propostas abaixo usam os mesmos móveis (mais uma poltrona na C) e passaram pelo mesmo simulador de circulação. Escolham uma, ou misturem cômodos de propostas diferentes.</p></header>

<section id="fluxo"><hr class="rule"><p class="eyebrow">Como se anda no apê</p><h2>Mapa de fluxo</h2>
<p>Três rotas diárias. A social vai da entrada, pela sala, até o hall de 0,85 m que distribui os dois quartos e o banheiro: é o caminho de madrugada, e por isso leva luz de vigília com sensor e nada de móvel na virada. A de serviço passa pela porta de correr de 0,70 da cozinha até a lavanderia, único acesso ao quarto/escritório e ao lavabo. A da varanda atravessa a sala. Os pontos vermelhos são os gargalos: onde a largura já é a mínima e não pode receber móvel.</p>
{figs["fluxo"]}
<div class="callout"><h3>O que o fluxo pede das propostas</h3><ul class="lista-solta">
<li><strong>Entrada → hall dos quartos</strong> sem desviar de cadeira: mínimo 0,60 m, ideal 0,90 m. A proposta A entrega 0,61; B e C entregam 1,15.</li>
<li><strong>Cozinha</strong>: corredor entre a bancada fixa e o que ficar na parede oposta, mínimo 0,90 m (todas entregam 1,06 m).</li>
<li><strong>Lavabo e escritório</strong> dependem da lavanderia: manter 0,60 m livres entre tanque, máquina e as duas portas.</li>
<li><strong>Varanda</strong>: a porta de correr de 1,40 m fica de frente para o vão entre sofá e rack.</li></ul></div></section>

{props}

<section id="eletrica"><hr class="rule"><p class="eyebrow">Elétrica nova</p><h2>Proposta de elétrica</h2>
<p>O quadro (QDC) fica onde já está: na cozinha, parede da sala, entre a porta de correr da entrada e o começo da bancada. Tudo sai dele por 12 circuitos, separados por uso, como pede a NBR 5410: iluminação em dois, tomadas de uso geral em quatro, e um circuito exclusivo para cada aparelho pesado (geladeira, micro-ondas, máquina de lavar, chuveiro e dois ares-condicionados). Quadro com disjuntor geral, DR de 30 mA nas áreas molhadas e no chuveiro, DPS contra surtos, e 4 espaços de reserva. A bitola do chuveiro depende da tensão do prédio (127 ou 220 V): confirmar na conta de luz antes de comprar fio.</p>
{figs["eletrica"]}
<div class="pg"></div><h3>Legenda dos símbolos</h3><ul class="leg">{leg}</ul>
<h3>Circuitos</h3><table><tr><th>nº</th><th>circuito</th><th>o que atende</th><th>cabo · disjuntor</th></tr>{circ}</table>
<div class="callout"><h3>Escolhas pensadas para 60+</h3><ul class="lista-solta">
<li>Interruptores a 1,00 m do piso e tomadas entre 0,40 e 1,10 m: ninguém se abaixa para ligar nada.</li>
<li>Interruptor paralelo na cabeceira dos dois quartos e no hall: apaga a luz deitado e acende antes de sair do quarto.</li>
<li>Luz de vigília com sensor de presença no hall e LED sob os armários da cozinha: luz baixa e automática à noite.</li>
<li>Tomada dupla dos dois lados da cama e uma no canto da TV com ponto de internet; campainha e interfone na entrada.</li>
<li>Exaustor no banheiro e na cozinha acionado junto com a luz.</li>
<li>Pontos de luz: os mesmos do mapa de iluminação (15 de teto e 10 auxiliares). Cada arandela e luminária de mesa tem interruptor próprio ao lado ou no corpo; os plafons duplos da sala e da cozinha acendem juntos no mesmo interruptor.</li>
<li>Torre lavadora + secadora: duas tomadas de 20 A lado a lado na parede da direita da lavanderia, cada uma no seu circuito (lavadora 2,5 mm² e 20 A; secadora 4,0 mm² e 25 A, conforme a placa do aparelho). Lavadora a 1,30 m do piso, secadora a 1,60 m, as duas a menos de 1,50 m do plugue e fora do respingo do tanque.</li>
<li>Eletroduto vazio até a sala e o quarto 2 para ar-condicionado futuro: passar o fio depois sem quebrar parede.</li></ul></div>
<div class="check"><h3>Antes de contratar o eletricista</h3><ol>
<li>Confirmar tensão (127/220 V) e o padrão de entrada com a concessionária: chuveiro de 7.500 W pode exigir aumento de carga.</li>
<li>Pedir projeto com ART e memorial de cálculo; a obra em prumada (chuveiro) entra no plano de reforma do condomínio.</li>
<li>Fazer a elétrica junto com o banheiro (fase 1), antes da pintura: paredes abertas uma vez só.</li>
<li>Trocar o quadro inteiro; reaproveitar fiação antiga só se o eletricista medir a isolação.</li></ol></div></section>

<section id="compras"><hr class="rule"><p class="eyebrow">Lista de compras</p><h2>Material da elétrica (estimativa para orçamento)</h2>
<p>Contagem tirada dos pontos do desenho. A metragem de cabo é estimada pelo caminho do quadro até o ponto mais longe de cada circuito, pelo teto, com 30 % de folga; o eletricista fecha a conta na obra. Cabo vem em rolo de 100 m: arredondar para cima.</p>
<table><tr><th>item</th><th>quantidade</th></tr>{"".join(f"<tr><td>{a}</td><td class='cota'>{b}</td></tr>" for a, b in compras())}</table></section>

<section id="luz"><hr class="rule"><p class="eyebrow">Iluminação</p><h2>Mapa de iluminação: quantas lâmpadas e de que cor</h2>
<p><strong>Uma lâmpada no meio basta só nos cômodos pequenos</strong> (lavanderia, lavabo, entrada, varanda). Nos outros não: aos 60 anos o olho precisa de duas a três vezes mais luz que aos 20, e uma lâmpada só no centro deixa sombra justamente onde se trabalha: bancada, espelho, cabeceira, mesa. A conta usada foi lux alvo × área ÷ 0,5, dividida entre os pontos de teto; o resto vem de luz auxiliar perto da tarefa. Sala e cozinha ganham dois pontos de teto; quartos, banheiro e escritório ficam com um plafon mais arandelas ou luminária de mesa, cada uma com seu interruptor.</p>
{figs["iluminacao"]}
<div class="pg"></div>
{tabela_luz()}
<div class="callout"><h3>Cor da lâmpada (temperatura em kelvin)</h3><ul class="lista-solta">
<li><strong>2700 K, branco quente:</strong> quartos, estar e varanda. Relaxa e não atrapalha o sono.</li>
<li><strong>3000 K, branco morno:</strong> jantar, circulação, banheiro e escritório. Aconchegante mas nítido.</li>
<li><strong>4000 K, branco neutro:</strong> cozinha, lavanderia, espelhos e mesas de trabalho. Mostra a cor real da comida, da roupa e do rosto. Nada de 6500 K (azulado, de hospital).</li>
<li><strong>IRC 90 ou mais em tudo:</strong> reprodução de cor alta ajuda a distinguir remédio, comida e degrau.</li>
<li><strong>Sem ofuscamento:</strong> plafons com difusor leitoso, nunca lâmpada nua no campo de visão; arandelas voltadas para a parede.</li>
<li><strong>Dimmer</strong> no estar e nos quartos: a mesma lâmpada serve para ler e para a madrugada.</li></ul></div></section>

<section id="custos"><hr class="rule"><p class="eyebrow">Quanto custa</p><h2>Preços médios pesquisados (setembro de 2026)</h2>
<p>Pesquisa feita em Leroy Merlin, Telhanorte, Magazine Luiza, Casas Bahia, Madeira Madeira, Amazon.com.br e Mercado Livre. Preço médio de produto de linha intermediária; a faixa vai do mais barato que serve ao bom. Frete, mão de obra e imprevistos ficam fora, exceto onde indicado. <strong>Já têm e saem da conta:</strong> {", ".join(JA_TEM).lower()}.</p>
<h3>Elétrica: material</h3>{TAB_ELE}
<div class="pg"></div><h3>Iluminação: luminárias e lâmpadas</h3>{TAB_LUZ}
<p class="muted">Mão de obra do eletricista para refazer o apartamento inteiro (rasgos, passagem, quadro, pontos): faixa de R$ 6.000 a 12.000 dependendo da região e de quem fecha o gesso. Pedir 3 orçamentos com o desenho em mãos.</p>
<div class="pg"></div><h3>Móveis por proposta</h3>
<p>A e B usam os mesmos móveis (mudam só de lugar). A C troca o sofá de 2,10 por um de 1,60 mais a poltrona reclinável.</p>
<h4>Propostas A e B</h4>{TAB_MOV_A}
<div class="pg"></div><h4>Proposta C</h4>{TAB_MOV_C}
<div class="pg"></div><h3>Banheiro (versão 1: box na janela, vaso no nicho)</h3>{TAB_BANHO}
<div class="callout terra"><h3>Resumo</h3><ul class="lista-solta">
<li>Elétrica (material + luminárias): <b>{brl(TOT_ELE + TOT_LUZ)}</b>, mais mão de obra.</li>
<li>Móveis: <b>{brl(TOT_MOV_A)}</b> (A ou B) ou <b>{brl(TOT_MOV_C)}</b> (C).</li>
<li>Banheiro completo com mão de obra: <b>{brl(TOT_BANHO)}</b>; sem a hidráulica extra da versão 1, {brl(TOT_BANHO - 2000)}.</li>
<li>Tudo junto, sem o eletricista: <b>{brl(TOT_ELE + TOT_LUZ + TOT_MOV_A + TOT_BANHO)}</b> a <b>{brl(TOT_ELE + TOT_LUZ + TOT_MOV_C + TOT_BANHO)}</b>. Dá para fasear: banheiro e elétrica primeiro, móveis conforme sobrar.</li></ul></div></section>

<footer>Desenhos gerados por <code>tools/propostas.py</code> sobre a planta medida no local. Checagens: circulação mínima 0,60, frente de armário de correr 0,65, sofá↔rack 0,80, corredor de cozinha 0,90, varredura de porta livre. Elétrica é proposta de pontos e circuitos para orientar o projeto do eletricista, não substitui o projeto executivo (NBR 5410).</footer>
</div>'''


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    figs, checks = {}, {}
    figs["fluxo"] = fig(fluxo(), "Rotas sobre a planta vazia. Setas = sentido de quem entra; pontos vermelhos = larguras mínimas.")
    for k, pr in PROPOSTAS.items():
        items = montar(pr["overrides"], pr["extras"])
        checks[k] = validar(items)
        svg = PL.mobiliado(items, pr["titulo"])
        open(os.path.join(OUT, f"proposta_{k}.svg"), "w", encoding="utf-8").write(svg)
        figs["proposta_" + k] = fig(svg, "Banheiro sempre na versão 1 (box na janela, vaso no nicho); armários e bancada existentes em marrom.")
        print(f"Proposta {k}:", *[f"\n  [{'OK ' if ok else '!! '}] {t}" for ok, t in checks[k]])
    figs["eletrica"] = fig(eletrica(), "Números ao lado dos símbolos = circuito. Móveis da proposta A em cinza só para referência de onde as tomadas servem.")
    figs["iluminacao"] = fig(iluminacao(), "Círculos grandes = pontos de teto com a potência da lâmpada LED; círculos pequenos = arandelas e luminárias de mesa; barra azul = fita LED sob os armários da cozinha. Cor do círculo = temperatura de cor.")
    for nome, svg in (("fluxo.svg", fluxo()), ("eletrica.svg", eletrica()), ("iluminacao.svg", iluminacao())):
        open(os.path.join(OUT, nome), "w", encoding="utf-8").write(svg)
    html = pagina(figs, checks)
    import re as _re
    html = _re.sub(r"<table><tr>(.*?)</tr>", lambda m: "<table><thead><tr>" + m.group(1) + "</tr></thead>", html)
    out = os.path.join(OUT, "propostas.html")
    open(out, "w", encoding="utf-8").write(html)
    print("propostas.html:", len(html) // 1024, "KB")
    if not all(ok for k in checks for ok, _ in checks[k]):
        print("ATENÇÃO: há checagens reprovadas")
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge):
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                        f"--print-to-pdf={os.path.join(OUT, 'propostas.pdf')}", "file:///" + out.replace("\\", "/")], check=False, timeout=90)
        print("propostas.pdf")
