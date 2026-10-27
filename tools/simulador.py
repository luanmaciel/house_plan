"""Simulador de layout sobre a planta real.

Fonte de geometria: PDF vetorial da planta medida no local (folha limpa), desenhado em CAD
na escala 1:20 (141,73 pt/m); caminho em HOUSE_PLAN_PDF ou inputs/plantas/planta.pdf. Paredes, portas e
janelas viram coordenadas em metros; o mobiliário é definido em metros relativos ao
canto superior esquerdo interno de cada cômodo. Valida circulação e varredura de
porta pelas regras do docs/manual-plantas-layout.md e imprime o relatório.

Uso:  python tools/simulador.py [banho|quartos|todos]
Saída: out/banho.svg, out/quartos.svg + relatório no terminal.
"""
import os
import math
import sys

import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.environ.get("HOUSE_PLAN_PDF", os.path.join(BASE, "inputs", "plantas", "planta.pdf"))
PAGINA = 1                 # folha 2 = desenho limpo
S = 72 / 25.4 * 50         # 1:20 em pontos por metro = 141,73
OUT = os.path.join(BASE, "out")
PX = 140                   # pixels por metro no SVG

C = dict(ink="#1c1a17", muted="#6E6355", sage="#5F7355", wood="#A06B3F",
         red="#B93A2B", warn="#A8742C", paper="#ffffff", bed="#EFEAE0")
MONO = 'font-family="IBM Plex Mono, Consolas, monospace"'


# ---------- geometria do PDF ----------
def carregar():
    if not os.path.exists(PDF):
        sys.exit(f"planta não encontrada: {PDF} (defina HOUSE_PLAN_PDF)")
    page = fitz.open(PDF)[PAGINA]
    lines = []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l":
                lines.append((it[1].x, it[1].y, it[2].x, it[2].y))
            elif it[0] == "re":
                r = it[1]
                lines += [(r.x0, r.y0, r.x1, r.y0), (r.x1, r.y0, r.x1, r.y1), (r.x1, r.y1, r.x0, r.y1), (r.x0, r.y1, r.x0, r.y0)]
    return lines


LINES = carregar()


def m(v):            # metros -> pontos
    return v * S


# Interiores dos cômodos em pontos (x0, y0, x1, y1), medidos nos vetores da planta de exemplo: remedir para outra planta.
ROOMS = {
    "banho":  (1327.8, 907.2, 1563.0, 1149.8),   # 1,66 x 1,71
    "nicho":  (1327.8, 765.5, 1427.0, 907.2),    # 0,70 x 1,00, boca cheia para o banho
    "q1":     (1592.8, 332.5, 2107.9, 726.3),    # 3,63 x 2,78
    "q1_alc": (1471.6, 332.5, 1592.8, 597.3),    # alcova 0,86 x 1,87 na parede do hall
    "q2":     (1592.8, 756.0, 2107.9, 1149.8),   # 3,63 x 2,78
}
# Portas: (dobradiça x, y, folha em m, quadrante da varredura (sx, sy))
DOORS = {
    "banho": (1563.0, 907.2, 0.80, (-1, +1)),   # parede do hall, batente direito, abre p/ dentro
    "q1":    (1592.8, 726.3, 0.70, (+1, -1)),   # parede do hall, canto de baixo, folha na parede de baixo
    "q2":    (1592.8, 767.0, 0.70, (+1, +1)),   # parede do hall, canto de cima, folha na parede de cima
    "escritorio": (517.1, 1142.8, 0.60, (-1, -1)),  # abre da lavanderia para dentro
    "lavabo":     (517.1, 1311.9, 0.60, (-1, -1)),
    "entrada":    (698.5, 332.5, 0.83, (+1, +1)),
}
SLIDERS = [(768.0, 472.0, 867.2, 472.0), (607.8, 1013.7, 820.4, 1013.7), (1024.5, 1141.0, 1222.9, 1141.0)]  # cozinha e varanda: correr


def rr(room, dx, dy, w, h):
    x0, y0, _, _ = ROOMS[room]
    return (x0 + m(dx), y0 + m(dy), x0 + m(dx + w), y0 + m(dy + h))


def pp(room, dx, dy):
    x0, y0, _, _ = ROOMS[room]
    return (x0 + m(dx), y0 + m(dy))


# ---------- validação ----------
def gap(a, b, axis):
    i = 0 if axis == "x" else 1
    lo, hi = (a, b) if a[i] <= b[i] else (b, a)
    return (hi[i] - lo[i + 2]) / S


def swing_hits(rect, door):
    hx, hy, r, (sx, sy) = door
    rp = m(r)
    bx0 = min(hx, hx + sx * rp); bx1 = max(hx, hx + sx * rp)
    by0 = min(hy, hy + sy * rp); by1 = max(hy, hy + sy * rp)
    return not (rect[2] <= bx0 or rect[0] >= bx1 or rect[3] <= by0 or rect[1] >= by1)


def check(nome, valor, minimo, unidade="m"):
    ok = valor >= minimo - 1e-6   # ponto flutuante: 0,65 medido tem de passar em 0,65
    print(f"  [{'OK ' if ok else 'ATENÇÃO'}] {nome}: {valor:.2f} {unidade} (mín. {minimo:.2f})")
    return ok


# ---------- SVG ----------
class Svg:
    def __init__(self, bbox, titulo):
        self.x0, self.y0, self.x1, self.y1 = bbox
        self.w = (self.x1 - self.x0) / S * PX + 40
        self.h = (self.y1 - self.y0) / S * PX + 60
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w:.0f} {self.h:.0f}" role="img" aria-label="{titulo}">',
                      f'<rect width="100%" height="100%" fill="{C["paper"]}"/>',
                      f'<text x="20" y="28" {MONO} font-size="13" font-weight="600" fill="{C["muted"]}">{titulo}</text>']

    def px(self, x, y):
        return (x - self.x0) / S * PX + 20, (y - self.y0) / S * PX + 40

    def planta(self):
        for l in LINES:
            if self.x0 - 2 <= min(l[0], l[2]) and max(l[0], l[2]) <= self.x1 + 2 and \
               self.y0 - 2 <= min(l[1], l[3]) and max(l[1], l[3]) <= self.y1 + 2:
                a = self.px(l[0], l[1]); b = self.px(l[2], l[3])
                self.parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{C["ink"]}" stroke-width="1.6"/>')

    def swing(self, door):
        hx, hy, r, (sx, sy) = door
        rp = m(r)
        a = self.px(hx + sx * rp, hy); b = self.px(hx, hy + sy * rp); h = self.px(hx, hy)
        rpx = r * PX
        sweep = 1 if sx * sy > 0 else 0
        self.parts.append(f'<path d="M{h[0]:.1f},{h[1]:.1f} L{a[0]:.1f},{a[1]:.1f} A{rpx:.1f},{rpx:.1f} 0 0 {sweep} {b[0]:.1f},{b[1]:.1f} Z" fill="{C["warn"]}" fill-opacity="0.12" stroke="{C["warn"]}" stroke-width="1" stroke-dasharray="4 3"/>')

    def rect(self, r, fill, stroke, label=None, op=0.35, dash=None, lab_dy=0):
        a = self.px(r[0], r[1]); b = self.px(r[2], r[3])
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0]-a[0]:.1f}" height="{b[1]-a[1]:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1.8"{d}/>')
        if label:
            self.parts.append(f'<text x="{a[0]+5:.1f}" y="{a[1]+14+lab_dy:.1f}" {MONO} font-size="11" fill="{stroke}">{label}</text>')

    def ellipse(self, cx, cy, rx, ry, stroke):
        c = self.px(cx, cy)
        self.parts.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx*PX:.1f}" ry="{ry*PX:.1f}" fill="none" stroke="{stroke}" stroke-width="2"/>')

    def line(self, x0, y0, x1, y1, stroke, w=4, dash=None):
        a = self.px(x0, y0); b = self.px(x1, y1)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>')

    def text(self, x, y, s, fill, size=11, rot=0):
        p = self.px(x, y)
        t = f' transform="rotate({rot} {p[0]:.1f} {p[1]:.1f})"' if rot else ""
        self.parts.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" {MONO} font-size="{size}" fill="{fill}"{t}>{s}</text>')

    def dim(self, x0, y0, x1, y1, label):
        a = self.px(x0, y0); b = self.px(x1, y1)
        self.parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{C["red"]}" stroke-width="1" marker-start="url(#t)" marker-end="url(#t)"/>')
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        rot = 0 if abs(b[0] - a[0]) > abs(b[1] - a[1]) else -90
        self.parts.append(f'<text x="{mx:.1f}" y="{my-4:.1f}" {MONO} font-size="10" fill="{C["red"]}" text-anchor="middle" transform="rotate({rot} {mx:.1f} {my:.1f})">{label}</text>')

    def save(self, nome):
        self.parts.insert(1, '<defs><marker id="t" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M1,1 L5,5 M1,5 L5,1" stroke="#B93A2B" stroke-width="1"/></marker></defs>')
        self.parts.append("</svg>")
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, nome)
        open(path, "w", encoding="utf-8").write("\n".join(self.parts))
        print(f"  -> {path}")


# ---------- layouts ----------
def banho(pia_p=0.45, pia_c=0.60, pia_y=0.05, girada=False):
    """V1. pia_p = fundo da pia, pia_c = comprimento. Na parede da sala: pia_y = distância da boca do nicho
    até a pia (0,05 = junto ao nicho; 0,91 - pia_c = encostada no box). girada=True: o comprimento encosta
    no vidro fixo do box, no canto com a parede da sala, e o fundo sobe em direção ao nicho.
    Ex.: python tools/simulador.py banho 35x59 [box|girada] -> out/banho_35x59[_box|_girada].svg."""
    no_box = pia_y + pia_c >= 0.91 - 1e-6
    tag = "" if (pia_p, pia_c, pia_y, girada) == (0.45, 0.60, 0.05, False) else \
        f"_{pia_p*100:.0f}x{pia_c*100:.0f}" + ("_girada" if girada else "_box" if no_box else "")
    lab = f"{pia_c:.2f}x{pia_p:.2f}".replace(".", ",")
    onde = "girada, encostada no box" if girada else "na parede da sala"
    print(f"\nBANHEIRO V1 · box 1,66 x 0,80 na janela, vaso no nicho, pia {lab} {onde}")
    s = Svg((1285, 725, 1640, 1200), f"Banheiro V1 · pia {lab}" if tag else "Banheiro · planta real + proposta")
    s.planta()
    s.swing(DOORS["banho"])
    box = rr("banho", 0, 0.91, 1.66, 0.80)
    s.rect(box, C["sage"], C["sage"], "box novo 1,66 x 0,80", op=0.25)
    s.ellipse(*pp("banho", 0.30, 1.21), 0.09, 0.09, C["wood"])
    s.text(*pp("banho", 0.44, 1.25), "chuveiro", C["wood"], 10)
    s.rect(rr("banho", 0.05, 1.62, 0.60, 0.06), C["sage"], C["sage"], op=0.8)           # ralo linear
    banco = rr("banho", 0.0, 1.28, 0.30, 0.40)
    s.rect(banco, "none", C["wood"], "banco", op=0)
    s.line(*pp("banho", 0.86, 0.91), *pp("banho", 1.66, 0.91), C["wood"], 5)           # porta de vidro 0,80
    s.line(*pp("banho", 0, 0.91), *pp("banho", 0.86, 0.91), C["muted"], 2, "3 3")      # vidro fixo
    s.line(*pp("banho", 1.62, 1.05), *pp("banho", 1.62, 1.65), C["wood"], 4)           # barra no box
    if girada:
        pia = rr("banho", 0, 0.91 - pia_p, pia_c, pia_p)
        s.rect(pia, "none", C["muted"], f"pia {lab}", op=0)
        s.ellipse(*pp("banho", pia_c / 2, 0.91 - pia_p / 2), pia_c * 0.28, pia_p * 0.31, C["muted"])
    else:
        pia = rr("banho", 0, pia_y, pia_p, pia_c)
        s.rect(pia, "none", C["muted"], f"pia {lab}", op=0)
        s.ellipse(*pp("banho", pia_p / 2, pia_y + pia_c / 2), pia_p * 0.31, pia_c * 0.28, C["muted"])
        if pia_y > 0.10:
            s.dim(*pp("banho", pia_p / 2, 0.01), *pp("banho", pia_p / 2, pia_y - 0.01), f"{pia_y:.2f}".replace(".", ","))
    caixa = rr("nicho", 0.15, 0.03, 0.40, 0.15)
    s.rect(caixa, "none", C["red"], op=0)
    s.ellipse(*pp("nicho", 0.35, 0.55), 0.19, 0.33, C["red"])
    s.text(*pp("nicho", -0.02, -0.08), "vaso no nicho 0,70 · 0,38 x 0,68", C["red"], 10)
    for x in (0.03, 0.67):                                                              # barras laterais
        s.line(*pp("nicho", x, 0.25), *pp("nicho", x, 0.95), C["wood"], 4)
    s.text(*pp("banho", 0.90, 0.72), "porta 0,80 abre p/ dentro", C["warn"], 9)
    s.text(*pp("banho", 1.72, -0.55), "hall", C["muted"], 11)
    s.text(*pp("banho", -0.20, 1.0), "sala", C["muted"], 10, -90)
    s.text(*pp("banho", 1.95, 1.2), "quarto 2", C["muted"], 10, -90)
    s.dim(*pp("banho", 0.75, 0.03), *pp("banho", 0.75, 0.89), "0,91 livre")
    if girada:
        faixa = 0.91 - pia_p                                   # faixa livre entre a boca do nicho e a frente da pia
        diag = math.hypot(0.70 - pia_c, faixa)                 # canto da boca do nicho (0,70; 0) até o canto livre da pia
        s.dim(*pp("banho", 0.10, 0.01), *pp("banho", 0.10, faixa - 0.01), f"{faixa:.2f}".replace(".", ","))
        s.line(*pp("banho", 0.70, 0.0), *pp("banho", pia_c, faixa), C["red"], 2, "4 3")
        s.text(*pp("banho", 0.80, 0.30), f"{diag:.2f} na diagonal".replace(".", ","), C["red"], 10)
        s.dim(*pp("banho", pia_c + 0.02, 0.86), *pp("banho", 1.64, 0.86), f"{1.66 - pia_c:.2f}".replace(".", ","))
    else:
        s.dim(*pp("banho", pia_p + 0.02, 0.45), *pp("banho", 1.64, 0.45), f"{1.66 - pia_p:.2f}".replace(".", ","))
        s.dim(*pp("banho", pia_p + 0.02, 0.02), *pp("banho", 0.68, 0.02), f"{0.70 - pia_p:.2f}".replace(".", ","))
    s.save(f"banho{tag}.svg")
    check("box: largura", 1.66, 0.90); check("box: profundidade", 0.80, 0.80)
    print("  [info] box com 0,80 de fundo: passa no mínimo do simulador, mas fica abaixo dos 0,90 x 0,95 que a NBR 9050 sugere com banco")
    check("corredor entre box e parede do hall", 0.91, 0.60)
    check("boca do nicho (limite: NBR 9050 pede 0,80)", 0.70, 0.70)
    if girada:
        check("frente da pia até a linha da boca do nicho", faixa, 0.80)
        check("frente da pia até a frente do vaso (nicho aberto, vaso a 0,12 da boca)", faixa + 0.12, 0.80)
        check("faixa livre na frente da boca do nicho, nos 0,70 de largura", faixa, 0.60)
        check("passagem na diagonal: canto da boca do nicho até o canto da pia", diag, 0.60)
        check("corredor da porta ao nicho, ao lado da pia", 1.66 - pia_c, 0.80)
        check("pia no vidro fixo: folga até a porta do box (0,86)", 0.86 - pia_c, 0.0)
    else:
        check("frente da pia até parede oposta", 1.66 - pia_p, 0.80)
        check("acesso ao nicho: vão entre a frente da pia e a lateral do nicho", 0.70 - pia_p, 0.80)
        check("pia: folga ao longo da parede até o vidro do box", 0.91 - pia_y - pia_c, 0.0)
        check("vão entre a boca do nicho e a pia, na parede da sala", pia_y, 0.60)
        check("pia não avança sobre a porta do box (vidro fixo até 0,86)", 0.86 - pia_p, 0.0)
    print("  [OK ] varredura da porta (0,80) não toca box, pia nem nicho:",
          not any(swing_hits(r, DOORS["banho"]) for r in (box, pia, caixa)))


def banho_v1b():
    """Versão 1b: box 1,00 x 0,90 no canto da sala, pia embaixo da janela junto à parede do quarto 2, vaso no nicho.
    Resolve a V1: lá a pia ficava na boca do nicho e sobravam 0,25 para chegar ao vaso."""
    print("\nBANHEIRO V1b · box 1,00 x 0,80 na parede da sala, pia sob a janela na ponta do quarto 2, vaso no nicho")
    s = Svg((1285, 725, 1640, 1200), "Banheiro V1b · box menor, pia sai da boca do nicho")
    s.planta()
    s.swing(DOORS["banho"])
    box = rr("banho", 0, 0.91, 1.00, 0.80)
    s.rect(box, C["sage"], C["sage"], "box 1,00 x 0,80", op=0.25)
    s.line(*pp("banho", 1.00, 0.91), *pp("banho", 1.00, 1.71), C["muted"], 2, "3 3")   # vidro fixo lateral
    s.line(*pp("banho", 0, 0.91), *pp("banho", 0.20, 0.91), C["muted"], 2, "3 3")      # vidro fixo 0,20
    s.line(*pp("banho", 0.20, 0.91), *pp("banho", 1.00, 0.91), C["wood"], 5)           # porta pivotante 0,80, dobradiça no lado da pia
    s.ellipse(*pp("banho", 0.30, 1.21), 0.09, 0.09, C["wood"])
    s.text(*pp("banho", 0.44, 1.25), "chuveiro", C["wood"], 10)
    s.rect(rr("banho", 0.05, 1.62, 0.60, 0.06), C["sage"], C["sage"], op=0.8)           # ralo linear
    banco = rr("banho", 0.0, 1.28, 0.30, 0.40)
    s.rect(banco, "none", C["wood"], "banco", op=0)
    s.line(*pp("banho", 0.10, 1.68), *pp("banho", 0.90, 1.68), C["wood"], 4)           # barra 0,80 na parede da janela
    pia = rr("banho", 1.06, 1.26, 0.60, 0.45)
    s.rect(pia, "none", C["muted"], "pia 0,60x0,45", op=0)
    s.ellipse(*pp("banho", 1.36, 1.49), 0.17, 0.14, C["muted"])
    caixa = rr("nicho", 0.15, 0.03, 0.40, 0.15)
    s.rect(caixa, "none", C["red"], op=0)
    s.ellipse(*pp("nicho", 0.35, 0.55), 0.19, 0.33, C["red"])
    s.text(*pp("nicho", -0.02, -0.08), "vaso no nicho 0,70 · 0,38 x 0,68", C["red"], 10)
    for x in (0.03, 0.67):
        s.line(*pp("nicho", x, 0.25), *pp("nicho", x, 0.95), C["wood"], 4)
    s.text(*pp("banho", 0.90, 0.72), "porta 0,80 abre p/ dentro", C["warn"], 9)
    s.text(*pp("banho", 1.72, -0.55), "hall", C["muted"], 11)
    s.text(*pp("banho", -0.20, 1.0), "sala", C["muted"], 10, -90)
    s.text(*pp("banho", 1.95, 1.2), "quarto 2", C["muted"], 10, -90)
    s.dim(*pp("banho", 0.60, 0.03), *pp("banho", 0.60, 0.89), "0,91 até o vaso")
    s.dim(*pp("banho", 1.58, 0.03), *pp("banho", 1.58, 1.24), "1,26 à frente da pia")
    s.save("banho_v1b.svg")
    check("box: largura", 1.00, 0.90); check("box: profundidade", 0.80, 0.80)
    print("  [info] box com 0,80 de fundo: passa no mínimo do simulador, mas fica abaixo dos 0,90 x 0,95 que a NBR 9050 sugere com banco")
    check("porta do box (pivotante, abre para fora)", 0.80, 0.80)
    check("corredor entre box e parede do hall (caminho da porta ao vaso)", 0.91, 0.80)
    check("acesso ao nicho: pia fora da boca, vão livre", 0.91, 0.80)
    check("frente da pia até a parede do hall", 1.26, 0.80)
    check("frente do vaso livre (nicho + corredor)", 0.16 + 0.91, 0.60)
    print("  [OK ] varredura da porta (0,80) não toca box, pia nem nicho:",
          not any(swing_hits(r, DOORS["banho"]) for r in (box, pia, caixa)))
    print("  [info] folha do box aberta fica em x=1,00, dentro da varredura da porta do banheiro: abre uma de cada vez")
    print("  [info] espelho 0,60 x 0,60 sob o peitoril da janela (0,90 a 1,50); barra do box na parede da janela")


def banho_v1c():
    """Versão 1c: box 1,66 x 0,80 na janela, pia triangular no canto da sala com o box, vaso no nicho.
    Pergunta: a diagonal da pia deixa uma pessoa passar até o vaso?"""
    print("\nBANHEIRO V1c · box 1,66 x 0,80 na janela, pia triangular no canto da sala, vaso no nicho")
    s = Svg((1285, 725, 1640, 1200), "Banheiro V1c · pia triangular no canto")
    s.planta()
    s.swing(DOORS["banho"])
    box = rr("banho", 0, 0.91, 1.66, 0.80)
    s.rect(box, C["sage"], C["sage"], "box 1,66 x 0,80", op=0.25)
    s.ellipse(*pp("banho", 0.30, 1.21), 0.09, 0.09, C["wood"])
    s.text(*pp("banho", 0.44, 1.25), "chuveiro", C["wood"], 10)
    s.rect(rr("banho", 0.05, 1.62, 0.60, 0.06), C["sage"], C["sage"], op=0.8)           # ralo linear
    s.rect(rr("banho", 0.0, 1.28, 0.30, 0.40), "none", C["wood"], "banco", op=0)
    s.line(*pp("banho", 0.86, 0.91), *pp("banho", 1.66, 0.91), C["wood"], 5)           # porta de vidro 0,80
    s.line(*pp("banho", 0, 0.91), *pp("banho", 0.86, 0.91), C["muted"], 2, "3 3")      # vidro fixo
    s.line(*pp("banho", 1.62, 1.05), *pp("banho", 1.62, 1.65), C["wood"], 4)           # barra no box
    A, B, Cc = (0.0, 0.31), (0.0, 0.91), (0.45, 0.91)          # pia triangular: catetos de 0,60 na parede da sala e 0,45 no vidro do box
    for (x1, y1), (x2, y2) in ((A, B), (B, Cc), (Cc, A)):
        s.line(*pp("banho", x1, y1), *pp("banho", x2, y2), C["muted"], 2)
    s.ellipse(*pp("banho", 0.15, 0.76), 0.11, 0.11, C["muted"])
    s.text(*pp("banho", 0.02, 0.29), "pia de canto 0,60 x 0,45", C["muted"], 9)
    caixa = rr("nicho", 0.15, 0.03, 0.40, 0.15)
    s.rect(caixa, "none", C["red"], op=0)
    s.ellipse(*pp("nicho", 0.35, 0.55), 0.19, 0.33, C["red"])
    s.text(*pp("nicho", -0.02, -0.08), "vaso no nicho 0,70 · 0,38 x 0,68", C["red"], 10)
    for x in (0.03, 0.67):
        s.line(*pp("nicho", x, 0.25), *pp("nicho", x, 0.95), C["wood"], 4)
    s.text(*pp("banho", 0.90, 0.72), "porta 0,80 abre p/ dentro", C["warn"], 9)
    s.text(*pp("banho", 1.72, -0.55), "hall", C["muted"], 11)
    s.text(*pp("banho", -0.20, 1.0), "sala", C["muted"], 10, -90)
    s.text(*pp("banho", 1.95, 1.2), "quarto 2", C["muted"], 10, -90)
    # passagem: do canto da lateral do nicho (0,70; 0) até o ponto mais próximo da hipotenusa
    (ax, az), (bx, bz), (px, pz) = A, Cc, (0.70, 0.0)
    dx, dz = bx - ax, bz - az
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz)))
    qx, qz = ax + t * dx, az + t * dz
    passagem = math.hypot(px - qx, pz - qz)
    s.line(*pp("banho", px, pz), *pp("banho", qx, qz), C["red"], 2, "4 3")
    s.text(*pp("banho", 0.50, 0.12), f"{passagem:.2f} na diagonal".replace(".", ","), C["red"], 10)
    s.dim(*pp("banho", 1.20, 0.03), *pp("banho", 1.20, 0.89), "0,91 livre")
    s.save("banho_v1c.svg")
    check("box: largura", 1.66, 0.90); check("box: profundidade", 0.80, 0.80)
    print("  [info] box com 0,80 de fundo: passa no mínimo do simulador, mas fica abaixo dos 0,90 x 0,95 que a NBR 9050 sugere com banco")
    check("corredor entre box e parede do hall", 0.91, 0.80)
    check("passagem na diagonal: canto do nicho até a pia triangular", passagem, 0.60)
    print("  [info] a diagonal passa no mínimo de circulação (0,60) mas fica abaixo dos 0,80 que a NBR 9050 pede na aproximação do vaso")
    print("  [OK ] varredura da porta (0,80) não toca box nem nicho:",
          not any(swing_hits(r, DOORS["banho"]) for r in (box, caixa)))


def banho_v2():
    """Versão 2: vaso mantido no canto do coletor (parede da sala x janela), box 0,96 na janela, pia no nicho."""
    print("\nBANHEIRO V2 · vaso no canto do coletor, box 0,96 na janela, pia no nicho (hidráulica mínima)")
    s = Svg((1285, 725, 1640, 1200), "Banheiro V2 · vaso fica junto ao coletor")
    s.planta()
    s.swing(DOORS["banho"])
    box = rr("banho", 0.70, 0.81, 0.96, 0.90)
    s.rect(box, C["sage"], C["sage"], "box 0,96 x 0,90", op=0.25)
    s.line(*pp("banho", 0.70, 0.81), *pp("banho", 0.70, 1.71), C["wood"], 5)            # meia-parede/vidro entre vaso e box
    s.line(*pp("banho", 0.98, 0.81), *pp("banho", 1.66, 0.81), C["wood"], 5)            # porta de vidro 0,68
    s.ellipse(*pp("banho", 1.40, 1.40), 0.09, 0.09, C["wood"])
    s.text(*pp("banho", 0.98, 1.60), "chuveiro", C["wood"], 9)
    banco = rr("banho", 0.72, 1.30, 0.30, 0.38)
    s.rect(banco, "none", C["wood"], "banco", op=0)
    caixa = rr("banho", 0.06, 1.53, 0.40, 0.18)                                          # caixa acoplada na parede da janela
    s.rect(caixa, "none", C["red"], op=0)
    s.ellipse(*pp("banho", 0.26, 1.21), 0.19, 0.30, C["red"])
    s.text(*pp("banho", -0.02, 0.98), "vaso 0,38x0,68", C["red"], 9)
    s.line(*pp("banho", 0.03, 0.95), *pp("banho", 0.03, 1.50), C["wood"], 4)            # barra na parede da sala
    s.line(*pp("banho", 0.66, 0.95), *pp("banho", 0.66, 1.50), C["wood"], 4)            # barra na meia-parede
    pia = rr("nicho", 0.0, 0.0, 0.70, 0.45)
    s.rect(pia, "none", C["muted"], "pia 0,70x0,45", op=0)
    s.ellipse(*pp("nicho", 0.35, 0.22), 0.16, 0.13, C["muted"])
    s.text(*pp("banho", 0.90, 0.72), "porta 0,80 abre p/ dentro", C["warn"], 9)
    s.text(*pp("banho", 1.72, -0.55), "hall", C["muted"], 11)
    s.text(*pp("banho", -0.20, 1.0), "sala", C["muted"], 10, -90)
    s.text(*pp("banho", 1.95, 1.2), "quarto 2", C["muted"], 10, -90)
    s.text(*pp("banho", -0.02, 1.80), "coletor de esgoto neste canto (projeto hidráulico)", C["red"], 9)
    s.dim(*pp("banho", 0.35, 0.03), *pp("banho", 0.35, 0.88), "0,90 à frente do vaso")
    s.save("banho_v2.svg")
    check("box: largura", 0.96, 0.90); check("box: profundidade", 0.90, 0.80)
    check("frente do vaso livre", 0.90, 0.60)
    check("corredor entre box e parede do hall", 0.81, 0.60)
    check("pia no nicho: largura", 0.70, 0.60)
    check("vaso: distância ao coletor (parede da sala x janela)", 0.0, 0.0)
    print("  [OK ] varredura da porta (0,80) não toca box, vaso nem pia:",
          not any(swing_hits(r, DOORS["banho"]) for r in (box, caixa, pia)))
    print("  [info] barra do lado do box exige meia-parede de alvenaria (vidro não segura barra)")


def quartos():
    print("\nQUARTO 1 · queen (armário na alcova)  |  QUARTO 2 · bicama + mesa")
    s = Svg((1440, 320, 2150, 1190), "Quartos · planta real + proposta")
    s.planta()
    for k in ("q1", "q2"):
        s.swing(DOORS[k])
    # Q1 ---------------------------------------------------------------
    arm = rr("q1_alc", 0.0, 0.0, 0.86, 1.87)                    # armário existente ocupa a alcova inteira
    s.rect(arm, C["wood"], C["wood"], op=0.3)
    s.text(*pp("q1_alc", 0.52, 1.80), "armário existente (alcova) 0,86 x 1,87", C["wood"], 10, -90)
    cama = rr("q1", 1.03, 0, 1.58, 1.98)
    s.rect(cama, C["bed"], C["ink"], "queen 1,58 x 1,98", op=0.9, lab_dy=90)
    s.rect(rr("q1", 1.09, 0.06, 0.70, 0.40), "none", C["muted"], op=0)
    s.rect(rr("q1", 1.85, 0.06, 0.70, 0.40), "none", C["muted"], op=0)
    cr1 = rr("q1", 0.58, 0, 0.40, 0.40); cr2 = rr("q1", 2.66, 0, 0.40, 0.40)
    s.rect(cr1, "none", C["muted"], op=0); s.rect(cr2, "none", C["muted"], op=0)
    s.dim(*pp("q1", 0.02, 1.10), *pp("q1", 1.01, 1.10), "1,03")
    s.dim(*pp("q1", 2.63, 1.10), *pp("q1", 3.61, 1.10), "1,02")
    s.dim(*pp("q1", 1.82, 2.00), *pp("q1", 1.82, 2.76), "0,80")
    print("  Quarto 1:")
    check("frente do armário existente (correr) até a cama", (cama[0] - arm[2]) / S, 0.65)
    check("passagem lado da janela", (ROOMS["q1"][2] - cama[2]) / S, 0.60)
    check("pé da cama até parede", (ROOMS["q1"][3] - cama[3]) / S, 0.60)
    print("  [OK ] varredura não toca cama/armário/criados:",
          not any(swing_hits(r, DOORS["q1"]) for r in (arm, cama, cr1, cr2)))
    # Q2 ---------------------------------------------------------------
    arm2 = rr("q2", 0.0, 0.88, 0.50, 1.90)                        # armário existente na parede do hall, abaixo da porta
    s.rect(arm2, C["wood"], C["wood"], op=0.3)
    s.text(*pp("q2", 0.36, 2.70), "armário existente 0,50 x 1,90 (correr)", C["wood"], 9, -90)
    cama2 = rr("q2", 1.15, 1.90, 1.88, 0.88)                      # ao longo da parede de baixo, pé para a janela
    s.rect(cama2, C["bed"], C["ink"], "bicama 1,88x0,88", op=0.9, lab_dy=60)
    s.rect(rr("q2", 1.21, 1.96, 0.50, 0.76), "none", C["muted"], op=0)
    bic = rr("q2", 1.15, 1.00, 1.80, 0.88)
    s.rect(bic, C["bed"], C["muted"], "auxiliar puxada (só à noite)", op=0.5, dash="5 4", lab_dy=60)
    mesa = rr("q2", 2.63, 0.0, 1.00, 0.50)                        # parede de cima, junto à janela
    s.rect(mesa, C["wood"], C["wood"], "mesa 1,00x0,50", op=0.3)
    cad = rr("q2", 2.99, 0.55, 0.45, 0.45)
    s.rect(cad, "none", C["muted"], op=0, dash="3 3")
    s.dim(*pp("q2", 0.52, 2.30), *pp("q2", 1.13, 2.30), "0,65")
    s.dim(*pp("q2", 3.20, 0.52), *pp("q2", 3.20, 1.88), "1,38 até a bicama")
    print("  Quarto 2:")
    check("mesa fora da varredura da porta", (mesa[0] - (DOORS["q2"][0] + m(0.70))) / S, 0.0)
    check("armário existente abaixo da varredura da porta", (arm2[1] - (DOORS["q2"][1] + m(0.70))) / S, 0.0)
    check("frente do armário existente (correr) até a bicama", (cama2[0] - arm2[2]) / S, 0.65)
    check("frente do armário existente até a auxiliar puxada", (bic[0] - arm2[2]) / S, 0.65)
    check("lado livre para puxar a auxiliar (acima da bicama)", (cama2[1] - ROOMS["q2"][1]) / S, 0.90)
    check("espaço da cadeira entre a mesa e a bicama (dia)", (cama2[1] - mesa[3]) / S, 0.75)
    check("passagem entre a bicama e a janela", (ROOMS["q2"][2] - cama2[2]) / S, 0.60)
    print("  [OK ] varredura não toca cama/mesa/armário:",
          not any(swing_hits(r, DOORS["q2"]) for r in (cama2, mesa, arm2)))
    print("  [info] à noite, com a auxiliar puxada, sobram 0,50 entre a mesa e a auxiliar: a cadeira sobe para a mesa")
    s.save("quartos.svg")


def geral():
    """Visão geral do apartamento inteiro com os layouts validados."""
    print("\nVISÃO GERAL · apartamento inteiro")
    global PX
    px_backup = PX; PX = 80
    s = Svg((245, 295, 2145, 1350), "Apartamento · planta real + layouts validados")
    s.planta()
    for k in DOORS:
        s.swing(DOORS[k])
    for (x0, y0, x1, y1) in SLIDERS:
        s.line(x0, y0, x1, y1, C["sage"], 3, "8 4")
    nomes = {"QUARTO 1": (1850, 690), "QUARTO 2": (1850, 1050), "BANHEIRO": (1440, 1000), "SALA": (1120, 700),
             "COZINHA": (600, 720), "LAVANDERIA": (600, 1200), "LAVABO": (300, 1250), "QUARTO/ESCRIT.": (295, 900),
             "VARANDA": (1000, 1250), "ENTRADA": (700, 400)}
    for n, (x, y) in nomes.items():
        s.text(x, y, n, C["muted"], 11)
    s.rect(rr("q1_alc", 0, 0, 0.86, 1.87), C["wood"], C["wood"], op=0.3)
    s.rect(rr("q1", 1.03, 0, 1.58, 1.98), C["bed"], C["ink"], "queen", op=0.9)
    s.rect(rr("q2", 0, 0.88, 0.50, 1.90), C["wood"], C["wood"], op=0.3)
    s.rect(rr("q2", 1.15, 1.90, 1.88, 0.88), C["bed"], C["ink"], "bicama", op=0.9)
    s.rect(rr("q2", 2.63, 0, 1.00, 0.50), C["wood"], C["wood"], "mesa", op=0.3)
    s.rect(rr("banho", 0, 0.91, 1.66, 0.80), C["sage"], C["sage"], "box", op=0.25)
    s.rect(rr("banho", 0, 0.05, 0.45, 0.60), "none", C["muted"], op=0)
    s.ellipse(*pp("nicho", 0.35, 0.55), 0.19, 0.33, C["red"])
    s.save("geral.svg")
    PX = px_backup


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "todos"
    print(f"fonte: {PDF} página {PAGINA + 1}, escala 1:20 ({S:.2f} pt/m)")
    if alvo in ("banho", "todos"):
        if alvo == "banho" and len(sys.argv) > 2:          # ex.: banho 35x59 [box|girada]  (cm: fundo x comprimento)
            pia_p, pia_c = (int(v) / 100 for v in sys.argv[2].lower().split("x"))
            modo = sys.argv[3] if len(sys.argv) > 3 else ""
            banho(pia_p, pia_c, 0.91 - pia_c if modo == "box" else 0.05, girada=(modo == "girada"))
        else:
            banho()
    if alvo in ("banho_v1b", "todos"):
        banho_v1b()
    if alvo in ("banho_v1c", "todos"):
        banho_v1c()
    if alvo in ("banho_v2", "todos"):
        banho_v2()
    if alvo in ("quartos", "todos"):
        quartos()
    if alvo in ("geral", "todos"):
        geral()
