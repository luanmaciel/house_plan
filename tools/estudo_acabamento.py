"""Estudo de acabamento: apartamento de 3 dormitórios, rev. 04/10/2026.

Geometria em metros montada a partir das COTAS ESCRITAS na planta do prédio
(foto da prancha "apto tipo", perspectiva retificada, 195 px/m) e da planta de vendas
(armários embutidos). Paredes internas estimadas em 0,15.
Orientação: a da prancha "apto tipo" (cozinha em cima à direita); a unidade real pode
estar espelhada/girada, as medidas não mudam.

Escopo: piso da sala e da cozinha, cozinha planejada,
portas dos armários embutidos dos quartos, acabamento do teto do banheiro. Nada de
hidráulica nem elétrica.

Saídas em out/: acabamento_cotas.svg, acabamento_cozinha.svg, acabamento.html (+ .pdf via Edge).
Uso: python tools/estudo_acabamento.py
"""
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "out")
T = 0.15                      # parede interna estimada
COL = dict(ink="#1c1a17", muted="#6E6355", wood="#A06B3F", sage="#5F7355", red="#B93A2B",
           warn="#A8742C", win="#6A8FB5", wall="#3a342d", bed="#8a8275")
MONO = 'font-family="IBM Plex Mono, Consolas, monospace"'

# ---------------------------------------------------------------- geometria (x, y, w, h) interiores
R = {
    "wc":       (1.75, 0.00, 0.90, 1.82),
    "area":     (1.75, 1.97, 1.85, 1.95),
    "cozinha":  (3.75, 1.97, 3.50, 1.95),
    "hall":     (7.40, 1.97, 0.96, 1.95),     # hall de entrada, 0,96 ao lado da cozinha
    "q3":       (0.00, 4.07, 2.65, 1.96),     # ex "dorm. empregada ou 3º opcional"
    "arm3":     (0.00, 6.03, 1.80, 0.60),     # armário embutido do q3 (planta de vendas)
    "banho":    (2.84, 4.07, 2.05, 1.93),     # cota 1,84; medido ~1,93 na foto
    "jantar":   (5.04, 4.07, 3.32, 2.93),
    "corredor": (1.95, 6.18, 3.09, 0.82),     # hall íntimo, 0,82
    "cor_fim":  (1.95, 6.18, 0.70, 1.05),     # ponta do corredor entre as portas do q1 e do q3
    "arm1":     (0.00, 6.78, 1.80, 0.60),     # armário embutido do q1, costas com o do q3
    "q1":       (0.00, 7.38, 2.70, 3.03),     # cota total 3,63 = 3,03 + armário 0,60
    "q2":       (2.85, 7.15, 2.70, 3.20),
    "estar":    (5.66, 7.00, 2.70, 2.93),
}
NOME = dict(wc="WC", area="ÁREA", cozinha="COZINHA", hall="HALL", q3="QUARTO 3", arm3="armário", banho="BANHEIRO",
            jantar="JANTAR", corredor="corredor", q1="QUARTO 1", arm1="armário", q2="QUARTO 2", estar="ESTAR")
# (dobradiça x, y, folha, quadrante sx, sy)
DOORS = [
    ("entrada", 8.36, 2.05, 0.80, -1, +1), ("hall→cozinha", 7.25, 2.05, 0.80, -1, +1),
    ("área→cozinha", 3.75, 2.05, 0.70, +1, +1), ("wc", 2.55, 1.82, 0.65, -1, -1),
    ("banho", 4.85, 6.00, 0.70, -1, -1), ("q2", 2.95, 7.15, 0.70, +1, +1),
    ("q1", 2.65, 7.38, 0.70, -1, +1), ("q3", 2.65, 6.03, 0.70, -1, -1),
]
WINDOWS = [  # (x1, y1, x2, y2) sobre a face da parede
    (0.0, 4.80, 0.0, 6.115), (0.69, 10.41, 2.005, 10.41), (3.54, 10.35, 4.855, 10.35),
    (5.78, 9.93, 8.235, 9.93), (1.78, 1.97, 3.58, 1.97), (1.85, 0.0, 2.55, 0.0),
]

# ---------------------------------------------------------------- quantitativos
def area(k):
    return R[k][2] * R[k][3]

PISO = {"sala (jantar + estar)": area("jantar") + area("estar"), "hall de entrada": area("hall"), "cozinha": area("cozinha")}
PISO_EXTRA = {"corredor dos quartos (opcional, mesmo piso)": area("corredor")}
PISO_BASE = sum(PISO.values())
RODAPE = (3.32 + 5.86 + 2.70 + 2.93 + 0.62 + 2.93) - 0.82 - 0.96 + (2 * 0.96 + 2 * 1.95 - 0.96 - 0.80 - 0.80)  # sala em L + hall, menos vãos
PE_DIREITO = 2.60                       # estimado (prédio dos anos 80); conferir
ARM_FRENTE = 2 * (1.80 * PE_DIREITO)    # duas frentes de armário, uma face
TETO_BANHO = area("banho")

# cozinha planejada: parede da sala (y = 3,92), módulos da esquerda (área) para a direita (hall)
MODULOS = [("filler", 0.15), ("cooktop/forno", 0.60), ("preparo", 0.60),
           ("pia (cuba à esq.)", 1.20), ("apoio", 0.20), ("geladeira", 0.75)]
PROF_BANCADA, PROF_TORRE = 0.60, 0.40
TORRE = (4.50, 1.97, 1.90, PROF_TORRE)  # parede oposta, entre as folhas das duas portas abertas
CORREDOR_COZ = R["cozinha"][3] - PROF_BANCADA - PROF_TORRE


def fmt(v, n=2):
    return f"{v:.{n}f}".replace(".", ",")


# ---------------------------------------------------------------- svg
def px(v, px_m, off=20):
    return f"{v * px_m + off:.1f}"


def door_path(d, px_m):
    _, hx, hy, r, sx, sy = d
    a = (hx + sx * r, hy); b = (hx, hy + sy * r)
    sw = 1 if sx * sy > 0 else 0
    return (f'<path d="M{px(hx, px_m)},{px(hy, px_m)} L{px(a[0], px_m)},{px(a[1], px_m)} A{r * px_m:.1f},{r * px_m:.1f} 0 0 {sw} '
            f'{px(b[0], px_m)},{px(b[1], px_m)} Z" fill="{COL["warn"]}" fill-opacity=".12" stroke="{COL["warn"]}" stroke-dasharray="4 3"/>')


def door_gap(d, px_m):
    """Apaga a parede no vão da porta (retângulo branco sobre a parede)."""
    _, hx, hy, r, sx, sy = d
    # vão: ao longo da parede, do lado oposto ao sentido da folha aberta. A folha aberta vai para (sx, 0); o vão corre em y.
    # Convenção aqui: portas de parede vertical (x fixo) têm o vão em y: de hy até hy + sy*r.
    vertical = d[0] in ("entrada", "hall→cozinha", "área→cozinha")
    if vertical:
        x0, y0, w, h = hx - T, min(hy, hy + sy * r), 2 * T, r
    else:
        x0, y0, w, h = min(hx, hx + sx * r), hy - T, r, 2 * T
    return f'<rect x="{px(x0, px_m)}" y="{px(y0, px_m)}" width="{w * px_m:.1f}" height="{h * px_m:.1f}" fill="#fff"/>'


def planta(px_m=90):
    W = (8.36 + 2 * T) * px_m + 40; H = (10.41 + 2 * T) * px_m + 70
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Planta: medidas internas">',
         '<rect width="100%" height="100%" fill="#ffffff"/>']
    # paredes: envelope de cada cômodo expandido em T, depois o interior branco por cima
    for k, (x, y, w, h) in R.items():
        if k in ("arm1", "arm3", "cor_fim"):
            continue
        s.append(f'<rect x="{px(x - T + T, px_m)}" y="{px(y - T + T, px_m)}" width="{(w + 2 * T) * px_m:.1f}" height="{(h + 2 * T) * px_m:.1f}" fill="{COL["wall"]}" transform="translate({-T * px_m:.1f} {-T * px_m:.1f})"/>')
    for k, (x, y, w, h) in R.items():
        if k in ("arm1", "arm3"):
            continue
        s.append(f'<rect x="{px(x, px_m)}" y="{px(y, px_m)}" width="{w * px_m:.1f}" height="{h * px_m:.1f}" fill="#fff"/>')
    for k in ("arm1", "arm3"):
        x, y, w, h = R[k]
        s.append(f'<rect x="{px(x, px_m)}" y="{px(y, px_m)}" width="{w * px_m:.1f}" height="{h * px_m:.1f}" fill="{COL["wood"]}" fill-opacity=".35" stroke="{COL["wood"]}"/>')
        s.append(f'<text x="{px(x + 0.06, px_m)}" y="{px(y + 0.40, px_m)}" {MONO} font-size="9" fill="{COL["wood"]}">armário embutido 1,80 × 0,60</text>')
    for d in DOORS:
        s.append(door_gap(d, px_m)); s.append(door_path(d, px_m))
    # aberturas sem porta: hall → jantar e corredor → jantar
    for x, y, w, h in ((7.40, 3.92, 0.96, T), (5.04 - T, 6.18, 2 * T, 0.82)):
        s.append(f'<rect x="{px(x, px_m)}" y="{px(y, px_m)}" width="{w * px_m:.1f}" height="{h * px_m:.1f}" fill="#fff"/>')
    for x1, y1, x2, y2 in WINDOWS:
        s.append(f'<line x1="{px(x1, px_m)}" y1="{px(y1, px_m)}" x2="{px(x2, px_m)}" y2="{px(y2, px_m)}" stroke="{COL["win"]}" stroke-width="5"/>')
    # piso em escopo: hachura leve
    for k in ("jantar", "estar", "hall", "cozinha"):
        x, y, w, h = R[k]
        s.append(f'<rect x="{px(x, px_m)}" y="{px(y, px_m)}" width="{w * px_m:.1f}" height="{h * px_m:.1f}" fill="{COL["sage"]}" fill-opacity=".10"/>')
    for k, nome in NOME.items():
        if k in ("arm1", "arm3"):
            continue
        x, y, w, h = R[k]; cx, cy = x + w / 2, y + h / 2
        peq = w * h < 2.6; fs = 9 if peq else 12
        s.append(f'<text x="{px(cx, px_m)}" y="{px(cy, px_m)}" {MONO} font-size="{fs}" font-weight="600" fill="{COL["muted"]}" text-anchor="middle">{nome}</text>')
        s.append(f'<text x="{px(cx, px_m)}" y="{float(px(cy, px_m)) + fs + 2:.1f}" {MONO} font-size="{fs + 1}" fill="{COL["red"]}" text-anchor="middle">{fmt(w)} × {fmt(h)}</text>')
        if not peq:
            s.append(f'<text x="{px(cx, px_m)}" y="{float(px(cy, px_m)) + 2 * fs + 5:.1f}" {MONO} font-size="{fs}" fill="{COL["muted"]}" text-anchor="middle">{fmt(w * h)} m²</text>')
    s.append(f'<text x="20" y="{H - 34:.0f}" {MONO} font-size="11" font-weight="600" fill="{COL["muted"]}">Medidas internas pelas cotas da planta do prédio (m)</text>')
    s.append(f'<text x="20" y="{H - 18:.0f}" {MONO} font-size="10" fill="{COL["muted"]}">verde = piso em escopo · marrom = armários embutidos (planta de vendas) · azul = janelas · leques = portas · paredes de 0,15 estimadas</text>')
    s.append("</svg>")
    return "\n".join(s)


def cozinha(px_m=170):
    x0, y0, w, h = R["cozinha"]
    W = (w + 2.2) * px_m; H = (h + 1.3) * px_m
    ox, oy = 0.9 * px_m, 0.55 * px_m

    def P(x, y):
        return f"{(x - x0) * px_m + ox:.1f},{(y - y0) * px_m + oy:.1f}"

    def rect(x, y, ww, hh, fill, op, stroke=None, dash=""):
        X, Y = P(x, y).split(",")
        return (f'<rect x="{X}" y="{Y}" width="{ww * px_m:.1f}" height="{hh * px_m:.1f}" fill="{fill}" fill-opacity="{op}" '
                f'stroke="{stroke or fill}" stroke-width="1.6"{dash}/>')

    def txt(x, y, t, fs=10, fill=COL["ink"], anchor="start", rot=0):
        X, Y = P(x, y).split(",")
        tr = f' transform="rotate({rot} {X} {Y})"' if rot else ""
        return f'<text x="{X}" y="{Y}" {MONO} font-size="{fs}" fill="{fill}" text-anchor="{anchor}"{tr}>{t}</text>'

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Cozinha planejada: proposta">',
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         rect(x0 - T, y0 - T, w + 2 * T, h + 2 * T, COL["wall"], 1), rect(x0, y0, w, h, "#fff", 1)]
    # vãos e leques das portas (área à esquerda, hall à direita; folhas encostam na parede de cima)
    for d in DOORS:
        if d[0] in ("hall→cozinha", "área→cozinha"):
            _, hx, hy, r, sx, sy = d
            s.append(rect(hx - T, hy, 2 * T, r, "#fff", 1))
            a = (hx + sx * r, hy); b = (hx, hy + sy * r); sw = 1 if sx * sy > 0 else 0
            s.append(f'<path d="M{P(hx, hy)} L{P(*a)} A{r * px_m:.1f},{r * px_m:.1f} 0 0 {sw} {P(*b)} Z" fill="{COL["warn"]}" fill-opacity=".12" stroke="{COL["warn"]}" stroke-dasharray="4 3"/>')
    # bancada na parede da sala
    yb = y0 + h - PROF_BANCADA; x = x0
    for nome, ww in MODULOS:
        c = COL["muted"] if nome in ("geladeira", "filler", "apoio") else COL["wood"]
        s.append(rect(x, yb, ww, PROF_BANCADA, c, .25 if nome != "filler" else .08))
        if nome != "filler":
            s.append(txt(x + 0.04, yb + 0.14, nome, 8, c)); s.append(txt(x + 0.04, yb + 0.26, fmt(ww), 8, COL["red"]))
        x += ww
    s.append(rect(x0 + 0.15, yb, 0.60, PROF_BANCADA, COL["red"], 0, COL["red"], ' stroke-dasharray="3 3"'))
    s.append(txt(x0 + 0.18, yb + 0.52, "coifa acima, duto p/ área", 7, COL["red"]))
    # ponto hidráulico atual (marcador na parede) e aéreos (texto no corredor, sobre a bancada)
    cx, cy = P(x0 + 1.80, y0 + h + 0.075).split(",")
    s.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{COL["win"]}"/>')
    s.append(txt(x0 + 1.80, y0 + h + 0.11, "ponto de água e esgoto atual (~1,80 da área)", 7, "#fff", "middle"))
    s.append(txt(x0 + 0.95, yb - 0.08, "aéreos de 0,35 sobre a bancada (base a 1,45 do piso), exceto sobre o cooktop", 7, COL["wood"]))
    # torre rasa na parede oposta
    tx, ty, tw, th = TORRE
    s.append(rect(tx, ty, tw, th, COL["sage"], .25))
    s.append(txt(tx + 0.05, ty + 0.15, "torre rasa 1,90 × 0,40", 8, COL["sage"]))
    s.append(txt(tx + 0.05, ty + 0.28, "micro-ondas a 1,00-1,40 · despensa com cestos · vassouras", 7, COL["sage"]))
    # corredor
    X1, Y1 = P(x0 + 2.2, ty + th).split(","); X2, Y2 = P(x0 + 2.2, yb).split(",")
    s.append(f'<line x1="{X1}" y1="{Y1}" x2="{X2}" y2="{Y2}" stroke="{COL["red"]}" stroke-width="1"/>')
    s.append(txt(x0 + 2.25, ty + th + 0.5, f"{fmt(CORREDOR_COZ)} livre", 10, COL["red"]))
    X1, Y1 = P(x0 + 3.45, y0 + 0.05).split(","); X2, Y2 = P(x0 + 3.45, yb).split(",")
    s.append(f'<line x1="{X1}" y1="{Y1}" x2="{X2}" y2="{Y2}" stroke="{COL["red"]}" stroke-width="1" stroke-dasharray="3 3"/>')
    s.append(txt(x0 + 3.40, y0 + 1.15, "1,20 até a geladeira", 8, COL["red"], "middle", -90))
    # rótulos de parede
    s.append(txt(x0 + w / 2, y0 - 0.22, "parede externa (sem janela na planta)", 9, COL["muted"], "middle"))
    s.append(txt(x0 + w / 2, y0 + h + 0.30, "parede da sala de jantar · bancada 3,50 × 0,60", 9, COL["muted"], "middle"))
    s.append(txt(x0 - 0.22, y0 + h / 2, "ÁREA DE SERVIÇO (porta 0,70 · gás)", 9, COL["muted"], "middle", -90))
    s.append(txt(x0 + w + 0.28, y0 + h / 2, "HALL DE ENTRADA (porta 0,80)", 9, COL["muted"], "middle", 90))
    s.append(txt(x0 - 0.8, y0 + h + 0.95, "Cozinha 3,50 × 1,95 · proposta de marcenaria (rev. 04/10/2026) · medidas em metros", 10, COL["muted"]))
    s.append("</svg>")
    return "\n".join(s)


# ---------------------------------------------------------------- página
PRECOS = [  # (item, faixa, base, fonte)
    ("Porcelanato nacional acetinado 60×60", "R$ 45 a 90/m²", "material", "antoniettasp.com.br"),
    ("Assentamento de porcelanato", "R$ 82 a 105/m²", "mão de obra + argamassa + rejunte", "chamaopro.com.br"),
    ("Remoção do piso antigo", "R$ 20 a 40/m²", "+ caçamba", "chamaopro.com.br"),
    ("Vinílico LVT em régua (Tarkett, Durafloor)", "R$ 80 a 150/m²", "material; premium 220 a 250", "afrel.com.br, tumelero.com.br"),
    ("Instalação de vinílico", "R$ 35 a 65/m²", "sem remoção; autonivelante +25 a 55/m²", "instaladordepisos.com.br"),
    ("Cozinha planejada, marcenaria de bairro", "R$ 12 a 20 mil", "bancada 2,70 + torre, instalada", "larpontual.com.br, portalleodias.com"),
    ("Cozinha planejada, Italínea/Favorita", "R$ 18 a 30 mil", "mesma configuração", "larpontual.com.br"),
    ("Bancada de granito 2,70 m (São Gabriel)", "R$ 2 a 4 mil", "R$ 650 a 950/m instalado", "larpontual.com.br"),
    ("Portas de armário: envelopamento vinílico", "R$ 150 a 300/m²", "instalado (Alltak, Imprimax)", "revesthome.com.br"),
    ("Portas de armário: esmalte à base d'água", "R$ 100 a 250/porta", "R$ 140 a 320/m²", "pinturasp.com.br"),
    ("Portas de armário: laca PU em oficina", "R$ 180 a 450/porta", "R$ 250 a 600/m²", "lackcores.com.br"),
    ("Portas novas em MDF na caixaria existente", "R$ 450 a 950/m²", "de frente, instaladas", "orcamentozap.com.br"),
    ("Teto do banheiro: tratamento de bolor + antimofo", "R$ 350 a 800", "serviço completo, 4 m²", "pinturasp.com.br"),
    ("Teto do banheiro: forro de PVC", "R$ 600 a 1.200", "instalado, 4 m²", "guiareforma.com"),
]


def tabela(linhas):
    th = "".join(f"<th>{h}</th>" for h in ("Item", "Faixa", "Base", "Fonte (set/out 2026)"))
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return f'<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def pagina():
    head = open(os.path.join(BASE, "templates", "base_head.html"), encoding="utf-8").read()

    def svg(name):
        return open(os.path.join(OUT, name), encoding="utf-8").read().replace(
            '<svg xmlns="http://www.w3.org/2000/svg"', '<svg xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;border-radius:10px;"')

    piso_rows = "".join(f"<tr><td>{k}</td><td>{fmt(v)} m²</td></tr>" for k, v in PISO.items())
    extra_rows = "".join(f"<tr><td>{k}</td><td>{fmt(v)} m²</td></tr>" for k, v in PISO_EXTRA.items())
    mods = ", ".join(f"{n} ({fmt(w)})" for n, w in MODULOS if n != "filler")
    return f'''<title>Plano de acabamento</title>
{head}
<style>
  table {{ width:100%; border-collapse:collapse; font-size:.92rem; margin:10px 0 18px; }}
  th, td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
  thead th {{ font-family:"IBM Plex Mono",monospace; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); white-space:nowrap; }}
  @page {{ size: A4; margin: 14mm 12mm; }}
  @media print {{
    body {{ background:#fff; padding:0; font-size:12.5px; }} .wrap {{ max-width:none; }} header {{ padding-top:0; }} section {{ margin-top:28px; }}
    .schema, .fase, .callout, .check, .ficha div, tr {{ break-inside:avoid; }} thead {{ display:table-header-group; }}
    .schema svg {{ max-height:150mm; width:auto; max-width:100%; margin:0 auto; }} .ficha .cota {{ white-space:normal; }}
    .ficha div, .fase, .check, .opt {{ box-shadow:none; }} a {{ color:inherit; text-decoration:none; }}
  }}
</style>

<div class="wrap">

<header>
  <p class="eyebrow">Plano de acabamento · rev. 04/10/2026</p>
  <h1>Plano de acabamento</h1>
  <p class="standfirst">Apartamento de 3 dormitórios, com armários embutidos já feitos em dois quartos. A reforma é enxuta de propósito: <strong>trocar o piso da sala e da cozinha, fazer a cozinha planejada, renovar as portas dos armários dos quartos e dar acabamento no teto do banheiro</strong>. Nada de hidráulica, nada de elétrica.</p>
</header>

<section id="ficha">
  <hr class="rule">
  <p class="eyebrow">O apartamento em números</p>
  <h2>Medidas pelas cotas da planta do prédio</h2>
  <div class="ficha">
    <div><b>Sala (em L) · {fmt(area("jantar") + area("estar"), 1)} m²</b><span class="cota">jantar 3,32 × 2,93 · estar 2,70 × 2,93 · 5,86 de fundo</span></div>
    <div><b>Hall de entrada · {fmt(area("hall"), 1)} m²</b><span class="cota">0,96 × 1,95, ao lado da cozinha</span></div>
    <div><b>Cozinha · {fmt(area("cozinha"), 1)} m²</b><span class="cota">3,50 × 1,95 · portas 0,70 (área) e 0,80 (hall)</span></div>
    <div><b>Área de serviço · {fmt(area("area"), 1)} m²</b><span class="cota">1,85 × 1,95 · janela padrão 1,80 com saída da coifa</span></div>
    <div><b>WC de serviço · {fmt(area("wc"), 1)} m²</b><span class="cota">0,90 × 1,82</span></div>
    <div><b>Banheiro · {fmt(TETO_BANHO, 1)} m²</b><span class="cota">2,05 × 1,84 (cota) · interno, sem janela</span></div>
    <div><b>Quarto 1 · {fmt(area("q1"), 1)} m²</b><span class="cota">2,70 × 3,03 + armário embutido 1,80 × 0,60</span></div>
    <div><b>Quarto 2 · {fmt(area("q2"), 1)} m²</b><span class="cota">2,70 × 3,20 · sem armário na planta</span></div>
    <div><b>Quarto 3 · {fmt(area("q3"), 1)} m²</b><span class="cota">2,65 × 1,96 + armário embutido 1,80 × 0,60</span></div>
    <div><b>Corredor dos quartos</b><span class="cota">0,82 de largura</span></div>
    <div><b>Janelas (grade padrão)</b><span class="cota">dormitórios 1,315 · sala 2,455 · altura 1,20</span></div>
    <div><b>Pé-direito*</b><span class="cota">2,60 (estimado, conferir)</span></div>
  </div>
  <p class="muted" style="margin-top:14px; font-size:.9rem;">Fonte: planta "apto tipo" do prédio (fotografada em 04/10/2026, perspectiva corrigida pela moldura da prancha, 195 px/m) e planta de vendas (que traz os armários embutidos). As cotas escritas batem com a foto retificada dentro de 5 cm; o banheiro mediu 1,93 de fundo contra 1,84 escrito. Paredes internas estimadas em 0,15. A planta é do apartamento tipo: a unidade real pode ser a versão espelhada, as medidas são as mesmas. Tudo com * é estimativa.</p>
  <div class="callout">
    <h3>Premissas do estudo</h3>
    <ul class="lista-solta">
      <li><strong>Escopo:</strong> só acabamento e marcenaria. Sem quebrar parede, sem mexer em tubo, sem mexer em fio. Isso tira da conta o responsável técnico de obra pesada e a janela de corte de água do prédio.</li>
      <li><strong>Armários:</strong> os quartos 1 e 3 já têm armário embutido de 1,80 × 0,60, costas com costas. Ficam; só as portas ganham cara nova.</li>
    </ul>
  </div>
</section>

<section id="planta">
  <hr class="rule">
  <p class="eyebrow">Planta</p>
  <h2>O apartamento só com as medidas</h2>
  <p>Medida interna de cada cômodo (largura × profundidade, em metros). Em verde, o piso que entra na obra: sala, hall de entrada e cozinha, uma superfície contínua sem porta no meio (a cozinha abre para o hall e o hall para o jantar).</p>
  <figure class="schema">
    {svg("acabamento_cotas.svg")}
    <figcaption>Gerado por <code>tools/estudo_acabamento.py</code> a partir das cotas. Posição exata das portas do corredor e das janelas: conferir no local. Serve para conferir com a trena antes de comprar.</figcaption>
  </figure>
</section>

<section id="piso">
  <hr class="rule">
  <p class="eyebrow">Item 1 · Piso</p>
  <h2>Sala e cozinha: {fmt(PISO_BASE, 1)} m² de piso novo</h2>
  <table><thead><tr><th>Ambiente</th><th>Área</th></tr></thead><tbody>{piso_rows}
  <tr><td><strong>Total em escopo</strong></td><td><strong>{fmt(PISO_BASE, 1)} m²</strong> → comprar <strong>{fmt(PISO_BASE * 1.10, 0)} m²</strong> (+10 %, mesmo lote)</td></tr>
  {extra_rows}
  <tr><td>Rodapé (sala + hall, descontando vãos)</td><td>{fmt(RODAPE, 1)} m → comprar 22 m</td></tr></tbody></table>
  <h3>Recomendação</h3>
  <p><strong>Porcelanato acetinado nacional 60 × 60</strong> (nem polido, nem muito rústico), um só material da sala até a cozinha, rejunte de cor próxima. Para os pés de 60+, o que importa é: superfície fosca/acetinada que não escorrega molhada (classe R10 serve para a cozinha), peça grande para ter menos rejunte, e <strong>nenhum degrau</strong> nas portas dos quartos, do banheiro e da área. Alternativa boa e mais barata de instalar: <strong>vinílico em régua (LVT)</strong>, quente, silencioso e antiderrapante, mas só se o piso atual estiver firme e plano (até 3 mm por metro); senão a conta do nivelamento come a economia.</p>
  <div class="check">
    <h3>O que decide o orçamento (conferir no local antes de pedir preço)</h3>
    <ol>
      <li><strong>Qual é o piso atual</strong> da sala (taco? cerâmica?) e da cozinha (cerâmica, provavelmente), e se está bem aderido. Isso define remover ou sobrepor.</li>
      <li><strong>Nível entre a sala e os quartos.</strong> Sobrepor porcelanato sobre o piso antigo sobe 1,5 a 2 cm e cria degrau na porta dos quartos: para 60+ a regra é remover o antigo e assentar no mesmo nível. Vinílico colado sobe 3 a 5 mm e dispensa a remoção.</li>
      <li><strong>A bancada atual da cozinha</strong> (1,75 m com pia, na parede da sala) sai antes do piso, para o piso novo passar por baixo da marcenaria.</li>
      <li><strong>Prazo do porcelanato:</strong> 2 a 6 semanas para chegar; pedir tudo de uma vez com 10 % de sobra do mesmo lote (tonalidade muda entre lotes).</li>
      <li><strong>Condomínio:</strong> avisar a administração (horário de obra, caçamba, elevador de serviço). Troca de piso sem alteração estrutural não exige projeto, mas muitos condomínios pedem o aviso por escrito (NBR 16280).</li>
    </ol>
  </div>
</section>

<section id="cozinha">
  <hr class="rule">
  <p class="eyebrow">Item 2 · Cozinha planejada</p>
  <h2>Cozinha corredor de 3,50 × 1,95: tudo numa parede, torre rasa na outra</h2>
  <p>A cozinha é estreita: com bancada de 0,60 nas duas paredes sobram 0,75 de corredor, apertado demais para duas pessoas ou um andador. A proposta usa a <strong>parede da sala</strong> para a linha de trabalho inteira (3,50 m: {mods}) e a <strong>parede oposta</strong> só para uma torre rasa de 0,40 entre as duas portas, que ficam na ponta de cima e abrem com a folha encostando nessa parede. Resultado: <span class="cota">{fmt(CORREDOR_COZ)}</span> livres no corredor e <span class="cota">1,20</span> na frente da geladeira.</p>
  <figure class="schema">
    {svg("acabamento_cozinha.svg")}
    <figcaption>Proposta de marcenaria, gerada por <code>tools/estudo_acabamento.py</code>. A pia fica sobre o ponto de água e esgoto existente (a 1,80 da parede da área); o cooktop fica na ponta da área, perto da prumada de gás e com duto curto da coifa até a saída padrão na janela da área.</figcaption>
  </figure>
  <h3>Por que assim</h3>
  <ul class="lista-solta">
    <li><strong>Pia no lugar da atual:</strong> o ponto de água e o esgoto não mudam, a marcenaria só recorta a bancada. É o que mantém a promessa de "nada de hidráulica".</li>
    <li><strong>Cooktop na ponta da área:</strong> o gás do prédio (prumada de rua) entra por esse lado e a coifa ganha o caminho mais curto até a janela da área, que já tem a saída padrão de 30 × 20. Forno elétrico embaixo do cooktop, na altura de 0,55 a 0,95, ou fogão de piso no mesmo módulo se preferirem o jeito de sempre.</li>
    <li><strong>Geladeira na ponta do hall:</strong> quem chega da rua com compras não atravessa a cozinha. A porta do hall fica na ponta de cima e não bate na geladeira.</li>
    <li><strong>Torre rasa de 0,40 na parede oposta:</strong> micro-ondas a 1,00 a 1,40 do piso (sem levantar panela quente acima do ombro), despensa com cestos puxáveis entre 0,40 e 1,40, e um vão para vassoura e tábua. 1,90 de largura: cabe entre as folhas das duas portas abertas.</li>
    <li><strong>Regras 60+ dentro dos módulos:</strong> gavetões telescópicos em vez de porta nos baixos (nada de agachar), aéreos com a base a 1,45 do piso e a primeira prateleira de uso diário até 1,60, puxador de alça ou cava, LED embaixo dos aéreos, bancada em cor contrastante com o piso.</li>
  </ul>
  <div class="callout terra">
    <h3>Elétrica: o que a cozinha pede e o que foi decidido</h3>
    <p>A planta do prédio mostra na cozinha uma tomada especial de 220 V na parede da sala (meio da bancada) e as tomadas comuns de 127 V. A decisão de projeto é <strong>não mexer na elétrica</strong>, então: cooktop a gás (não de indução, que precisaria de circuito novo de 32 A), micro-ondas e forno elétrico pequenos em tomadas existentes, coifa ligada na tomada mais próxima. Se quiserem reabrir isso, o momento certo é com a marcenaria ainda fora: 2 ou 3 tomadas novas na régua da bancada custam pouco e evitam extensão sobre a pia.</p>
  </div>
  <div class="check">
    <h3>Para pedir orçamento à marcenaria (3 orçamentos)</h3>
    <ol>
      <li>Bancada de 3,50 × 0,60 com cuba à esquerda do módulo da pia, recorte para cooktop de 4 bocas; pedra: granito São Gabriel (barato, escuro, contrasta com piso claro) ou quartzo claro.</li>
      <li>Baixos: 2 gaveteiros de 0,60 (um sob o preparo, um sob o cooktop com o forno), módulo da pia 1,20 com porta e lixeira embutida, nicho da geladeira de 0,75.</li>
      <li>Aéreos de 0,35 ao longo da bancada, exceto sobre o cooktop (coifa de parede de 0,60).</li>
      <li>Torre rasa 1,90 × 0,40 × 2,20 na parede oposta: nicho do micro a 1,00 a 1,40, despensa com cestos, vão para vassoura.</li>
      <li>Medição só depois do piso assentado e com a bancada velha removida; MDF entra por último, com a obra limpa.</li>
      <li>Conferir o elevador do prédio (cabine e porta) antes de aprovar módulos altos: chapa inteira pode não subir.</li>
    </ol>
  </div>
</section>

<section id="quartos">
  <hr class="rule">
  <p class="eyebrow">Item 3 · Quartos</p>
  <h2>Armários embutidos: ficam; só as portas mudam de cara</h2>
  <p>A planta de vendas mostra dois armários de <span class="cota">1,80 × 0,60</span>, costas com costas na parede entre o quarto 1 e o quarto 3. O quarto 2 não tem armário desenhado; se existir, soma-se à conta. Com pé-direito estimado de 2,60, são cerca de <strong>{fmt(ARM_FRENTE, 1)} m² de frente</strong> (as duas, uma face), algo como 6 portas de abrir de 0,60 ou 4 de correr. Nada disso se compra antes de contar as portas no local e ver o material (compensado, madeira maciça, fórmica).</p>
  <div class="opts">
    <div class="opt"><div class="opt-head"><h3>A · Envelopamento vinílico</h3><span class="custo">R$ 150 a 300/m²</span><span class="tag-melhor">mais barato e rápido</span></div>
      <p>Adesivo de móvel (Alltak, Imprimax) aplicado por profissional, em um dia, sem cheiro e sem tirar as portas. Padrões de madeira clara ou cor lisa.</p>
      <div class="pros-cons"><div class="pros"><h4>A favor</h4><ul><li>Reversível, sem poeira, sem prazo de secagem.</li><li>Cobre fórmica e laminado, que tinta não segura bem.</li></ul></div><div class="cons"><h4>Contra</h4><ul><li>Porta empenada ou com frisos fundos marca o adesivo.</li><li>Dura 5 a 8 anos; cantos podem soltar com o tempo.</li></ul></div></div></div>
    <div class="opt"><div class="opt-head"><h3>B · Pintura (laca PU em oficina ou esmalte à base d'água no local)</h3><span class="custo">R$ 100 a 450/porta</span></div>
      <p>Portas saem, vão para oficina, voltam laqueadas; ou pintor no local com esmalte à base d'água e primer para madeira/fórmica. Dá para escolher qualquer cor da paleta.</p>
      <div class="pros-cons"><div class="pros"><h4>A favor</h4><ul><li>Acabamento de móvel novo, sobretudo a laca.</li><li>Resolve riscos e pequenos amassados (massa antes).</li></ul></div><div class="cons"><h4>Contra</h4><ul><li>Fórmica exige primer específico; sem isso descasca.</li><li>Oficina leva 1 a 2 semanas com as portas fora.</li></ul></div></div></div>
    <div class="opt"><div class="opt-head"><h3>C · Portas novas em MDF na caixaria existente</h3><span class="custo">R$ 450 a 950/m²</span></div>
      <p>A marcenaria da cozinha faz frentes novas no mesmo MDF, com dobradiças ou trilhos novos. Caixaria, prateleiras e cabideiros ficam.</p>
      <div class="pros-cons"><div class="pros"><h4>A favor</h4><ul><li>Combina com a cozinha; ferragens novas (soft-close, puxador cava).</li><li>Única opção se as portas atuais estão empenadas ou com os trilhos gastos.</li></ul></div><div class="cons"><h4>Contra</h4><ul><li>3 a 5 vezes o preço do envelopamento.</li><li>Entra na fila da marcenaria (30 a 60 dias).</li></ul></div></div></div>
  </div>
  <div class="callout">
    <h3>Por dentro (opcional, mas barato de fazer junto)</h3>
    <ul class="lista-solta">
      <li>Roupa do dia a dia entre 0,40 e 1,40 do chão: prateleiras e gavetas nessa faixa; cabideiro a no máximo 1,60 ou puxa-cabide.</li>
      <li>Puxador de alça grande ou cava; LED com sensor dentro do armário.</li>
      <li>Trocar dobradiças e trilhos gastos enquanto as portas estão fora custa quase nada.</li>
    </ul>
  </div>
</section>

<section id="banheiro">
  <hr class="rule">
  <p class="eyebrow">Item 4 · Banheiro</p>
  <h2>Teto: acabamento, sem tocar em tubo ou fio</h2>
  <p>O banheiro tem <span class="cota">{fmt(TETO_BANHO, 1)} m²</span> de teto e é <strong>interno, sem janela</strong> (cercado pela cozinha, pelo jantar, pelo corredor e pelo quarto 3). Teto feio em banheiro assim é quase sempre bolor por vapor preso, não infiltração. Antes de pintar, olhar: se há manchas de água com contorno marrom (infiltração do vizinho de cima: aí é conversa com o condomínio antes de qualquer tinta) ou só pontos escuros difusos (bolor).</p>
  <h3>Sequência que funciona</h3>
  <ol>
    <li>Raspar o que está solto; lavar o teto com água sanitária diluída (1:3) ou fungicida de parede; deixar secar 24 h.</li>
    <li>Fundo preparador ou selador acrílico; massa acrílica só onde houver buraco ou descascado; lixa fina.</li>
    <li>Duas demãos de <strong>tinta acrílica antimofo acetinada</strong> (linha banheiro/cozinha). Esmalte à base d'água também serve e limpa melhor.</li>
    <li>Se o reboco estiver muito solto ou ondulado, pular a massa e colocar <strong>forro de PVC branco</strong> (R$ 600 a 1.200 instalado): esconde tudo, aguenta vapor e dá para tirar depois.</li>
  </ol>
  <p class="muted" style="font-size:.9rem;">Ressalva honesta: sem ventilação, o bolor volta em 1 a 2 anos. Enquanto a elétrica fica fora do escopo, a mitigação é deixar a porta aberta depois do banho e usar o rodo no box. Um exaustor na luz do banheiro é a única coisa que resolve de vez, e pode entrar numa etapa futura.</p>
</section>

<section id="fases">
  <hr class="rule">
  <p class="eyebrow">Ordem e prazos</p>
  <h2>O que fazer, em que ordem</h2>
  <ol class="fases">
    <li class="fase"><span class="fase-num">0</span><div><h3>Medir e orçar · 1 a 2 semanas</h3><p>Trena a laser: cada cômodo da planta, pé-direito, nível entre sala e quartos, contar e fotografar as portas dos armários, fotografar o teto do banheiro e a bancada atual. 3 orçamentos de piso (material + assentamento), 3 de marcenaria, 2 de pintura/envelopamento.</p><p class="por-que">Tudo neste documento parte de cotas de planta; a trena fecha os centímetros antes de gastar.</p></div></li>
    <li class="fase"><span class="fase-num">1</span><div><h3>Comprar o piso e travar a marcenaria · semana 2</h3><p>Pedir o porcelanato (2 a 6 semanas de prazo) e assinar com a marcenaria com projeto congelado (fila de 30 a 60 dias). Avisar o condomínio.</p><p class="por-que">São os dois prazos longos; o resto espera por eles.</p></div></li>
    <li class="fase"><span class="fase-num">2</span><div><h3>Obra de piso · 1 a 2 semanas, apê vazio</h3><p>Tirar a bancada velha da cozinha, remover o piso antigo (ou regularizar), assentar o novo, rejuntar, rodapé. No mesmo pacote: teto do banheiro e pintura geral das paredes se quiserem.</p><p class="por-que">Poeira toda de uma vez, antes de qualquer móvel entrar.</p></div></li>
    <li class="fase"><span class="fase-num">3</span><div><h3>Portas dos armários · 1 a 2 semanas, em paralelo</h3><p>Envelopamento no local (1 dia) ou portas na oficina de laca enquanto o piso é feito.</p><p class="por-que">Não depende do piso; aproveita o apê vazio.</p></div></li>
    <li class="fase"><span class="fase-num">4</span><div><h3>Medição final e montagem da cozinha · 2 a 3 dias de montagem</h3><p>Marcenaria mede com o piso pronto e a obra limpa; monta; pedra da bancada entra depois dos módulos (1 a 2 semanas após a medição da pedra).</p><p class="por-que">MDF não entra em obra com poeira; a pedra só se mede com os módulos no lugar.</p></div></li>
    <li class="fase"><span class="fase-num">5</span><div><h3>Mudança</h3><p>Com piso, cozinha e armários prontos. Total realista do início das medições até a mudança: <strong>8 a 12 semanas</strong>, quase todo esperando fornecedor.</p><p class="por-que">Morar com a cozinha pronta é o que faz a reforma valer.</p></div></li>
  </ol>
</section>

<section id="custos">
  <hr class="rule">
  <p class="eyebrow">Quanto custa</p>
  <h2>Faixas de preço pesquisadas (setembro e outubro de 2026)</h2>
  {tabela(PRECOS)}
  <div class="conta">
    <p><b>Conta de padeiro para o escopo inteiro</b> ({fmt(PISO_BASE * 1.10, 0)} m² de piso, cozinha de 3,50 m com torre, {fmt(ARM_FRENTE, 0)} m² de portas, teto de 4 m²):</p>
    <ul class="lista-solta">
      <li>Piso porcelanato 60×60 removendo o antigo: R$ 4,5 a 7 mil. Vinílico sem remoção: R$ 3,5 a 6,5 mil.</li>
      <li>Cozinha planejada + bancada de granito: R$ 14 a 24 mil (marcenaria de bairro) ou R$ 20 a 34 mil (loja de planejados).</li>
      <li>Portas dos armários: R$ 1,5 a 3 mil (envelopamento) · R$ 1,5 a 5,5 mil (pintura) · R$ 4 a 9 mil (portas novas).</li>
      <li>Teto do banheiro: R$ 0,4 a 1,2 mil.</li>
      <li><b>Total: R$ 21 a 36 mil</b> na versão econômica, <b>R$ 30 a 50 mil</b> com loja de planejados e portas novas.</li>
    </ul>
  </div>
  <p class="muted" style="font-size:.9rem;">Faixas de mercado, não tabela de loja; a cozinha só tem preço real depois do projeto e da medição. Pedir sempre 2 a 3 orçamentos por serviço.</p>
</section>

<section id="paleta">
  <hr class="rule">
  <p class="eyebrow">Estilo</p>
  <h2>A paleta continua a mesma</h2>
  <div class="swatches">
    <figure class="sw"><div class="sw-chip" style="background:#8A6A4F"></div><figcaption><b>LOURO FREIJÓ</b>madeira · frentes da cozinha e portas dos armários</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#A79A82"></div><figcaption><b>DUST</b>neutro quente · caixaria</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#D6CDB4"></div><figcaption><b>NEVADA</b>claro · interiores e piso</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#9A9C9B"></div><figcaption><b>NIMBÓ</b>cinza · contraste</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#2E2B29"></div><figcaption><b>SÃO GABRIEL</b>granito · bancada escura sobre piso claro</figcaption></figure>
    <figure class="sw"><div class="sw-chip" style="background:#BC6A4A"></div><figcaption><b>TERRACOTA</b>tinta · um detalhe só</figcaption></figure>
  </div>
  <p style="margin-top:18px;"><strong>Contraste é conforto</strong> para olhos 60+: piso claro acetinado, bancada escura, puxador que se vê contra a porta, luz quente (2700 a 3000 K) forte sobre a bancada.</p>
</section>

<footer>
  Fonte de geometria: planta "apto tipo" do prédio fotografada (perspectiva corrigida) e planta de vendas; cotas escritas, paredes estimadas. Desenhos e quantitativos por <code>tools/estudo_acabamento.py</code>; regras de ergonomia em <code>docs/manual-plantas-layout.md</code>. Preços são faixas de mercado pesquisadas na web. Guia de conversa, não substitui a medição no local nem o orçamento do fornecedor.
</footer>

</div>
'''


def pdf(html_path, pdf_path):
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge):
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                        f"--print-to-pdf={pdf_path}", "file:///" + html_path.replace("\\", "/")], timeout=90)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    # checagens: o que quebraria em silêncio
    assert abs(PISO_BASE - 26.3) < 0.2, PISO_BASE
    assert abs(sum(w for _, w in MODULOS) - R["cozinha"][2]) < 1e-9, "módulos não fecham 3,50"
    assert CORREDOR_COZ >= 0.90, CORREDOR_COZ
    # torre fora dos leques das portas (raio 0,70 à esq., 0,80 à dir.)
    tx, ty, tw, th = TORRE
    assert tx >= R["cozinha"][0] + 0.70 and tx + tw <= R["cozinha"][0] + R["cozinha"][2] - 0.80
    for nome, fn in (("acabamento_cotas.svg", planta), ("acabamento_cozinha.svg", cozinha)):
        s = fn(); assert "COZINHA" in s or "torre" in s
        open(os.path.join(OUT, nome), "w", encoding="utf-8").write(s); print("->", nome, len(s) // 1024, "KB")
    html = pagina(); assert "—" not in html and "–" not in html, "travessão proibido"
    out = os.path.join(OUT, "acabamento.html"); open(out, "w", encoding="utf-8").write(html)
    print("-> acabamento.html", len(html) // 1024, "KB  | piso", fmt(PISO_BASE), "m² | rodapé", fmt(RODAPE), "m | frentes", fmt(ARM_FRENTE), "m²")
    pdf(out, os.path.join(OUT, "acabamento.pdf")); print("-> acabamento.pdf", os.path.exists(os.path.join(OUT, "acabamento.pdf")))
