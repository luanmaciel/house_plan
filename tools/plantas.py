"""Duas plantas do apartamento inteiro, a partir da mesma fonte da prancheta.

  out/cotas.svg      só paredes, portas e a medida interna de cada cômodo
  out/mobiliado.svg  paredes + móveis planejados (posições de tools/prancheta.py)

Uso: python tools/plantas.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prancheta as P  # noqa: E402  (carrega geo + ITEMS sem gravar o HTML)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
PX = 90
G = P.geo
R = G["rooms"]
COL = dict(wood="#A06B3F", sage="#5F7355", red="#B93A2B", muted="#6E6355", bed="#8a8275", ink="#1c1a17", cota="#B93A2B")
MONO = 'font-family="IBM Plex Mono, Consolas, monospace"'
NOMES = dict(banho="BANHEIRO", nicho="nicho", q1="QUARTO 1", q1alc="alcova", q2="QUARTO 2", sala="SALA", entrada="ENTRADA",
             cozinha="COZINHA", lavanderia="LAVANDERIA", lavabo="LAVABO", escritorio="QUARTO/ESCRIT.", varanda="VARANDA")


def px(v):
    return f"{v * PX + 20:.1f}"


def fmt(v):
    return f"{v:.2f}".replace(".", ",")


def base(titulo):
    w, h = G["W"] * PX + 40, G["H"] * PX + 60
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{titulo}">',
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         f'<text x="20" y="{h - 14:.0f}" {MONO} font-size="12" font-weight="600" fill="{COL["muted"]}">{titulo}</text>']
    for d in G["doors"]:
        a = (d["hx"] + d["sx"] * d["r"], d["hy"]); b = (d["hx"], d["hy"] + d["sy"] * d["r"])
        sw = 1 if d["sx"] * d["sy"] > 0 else 0
        s.append(f'<path d="M{px(d["hx"])},{px(d["hy"])} L{px(a[0])},{px(a[1])} A{d["r"] * PX:.1f},{d["r"] * PX:.1f} 0 0 {sw} {px(b[0])},{px(b[1])} Z" '
                 f'fill="#A8742C" fill-opacity=".12" stroke="#A8742C" stroke-dasharray="4 3"/>')
    for sl in G.get("sliders", []):
        s.append(f'<line x1="{px(sl[0])}" y1="{px(sl[1])}" x2="{px(sl[2])}" y2="{px(sl[3])}" stroke="{COL["sage"]}" stroke-width="3" stroke-dasharray="8 4"/>')
    for l in G["lines"]:
        s.append(f'<line x1="{px(l[0])}" y1="{px(l[1])}" x2="{px(l[2])}" y2="{px(l[3])}" stroke="{COL["ink"]}" stroke-width="1.6"/>')
    return s


AREA = {"sala": R["sala_top"][2] * R["sala_top"][3] + R["sala_bot"][2] * R["sala_bot"][3]}   # sala em L: não é o retângulo cheio


def cotas():
    s = base("Apartamento · medidas internas de cada cômodo (metros)")
    for k, nome in NOMES.items():
        x, y, w, h = R[k]
        cx, cy = x + w / 2, y + h / 2
        peq = w * h < 2.2
        fs = 9 if peq else 12
        s.append(f'<text x="{px(cx)}" y="{px(cy)}" {MONO} font-size="{fs}" font-weight="600" fill="{COL["muted"]}" text-anchor="middle">{nome}</text>')
        s.append(f'<text x="{px(cx)}" y="{float(px(cy)) + fs + 2:.1f}" {MONO} font-size="{fs + 1}" fill="{COL["cota"]}" text-anchor="middle">{fmt(w)} × {fmt(h)}</text>')
        s.append(f'<text x="{px(cx)}" y="{float(px(cy)) + 2 * fs + 5:.1f}" {MONO} font-size="{fs}" fill="{COL["muted"]}" text-anchor="middle">{fmt(AREA.get(k, w * h))} m²</text>')
    s.append("</svg>")
    return "\n".join(s)


def mobiliado(items=None, titulo="Apartamento · móveis planejados"):
    items = P.ITEMS if items is None else items
    s = base(titulo)
    for k, nome in NOMES.items():
        if k in ("nicho", "q1alc"):
            continue
        x, y, w, h = R[k]
        s.append(f'<text x="{px(x + 0.08)}" y="{px(y + h - 0.08)}" {MONO} font-size="10" fill="{COL["muted"]}">{nome}</text>')
    for it in items:
        c = COL[it["c"]]
        dash = ' stroke-dasharray="5 4"' if it["dash"] or it["night"] else ""
        s.append(f'<rect x="{px(it["x"])}" y="{px(it["y"])}" width="{it["w"] * PX:.1f}" height="{it["h"] * PX:.1f}" '
                 f'fill="{c}" fill-opacity="{it["op"]}" stroke="{c}" stroke-width="1.6"{dash}/>')
        if it["dash"] and not it["night"]:
            continue  # cadeiras: só o contorno
        vert = it["h"] > it["w"] * 1.6
        tx, ty = float(px(it["x"] + 0.05)), float(px(it["y"] + 0.15))
        rot = f' transform="rotate(90 {tx:.1f} {ty:.1f})"' if vert else ""
        s.append(f'<text x="{tx:.1f}" y="{ty:.1f}" {MONO} font-size="8" fill="{c}"{rot}>{it["label"]}</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for nome, fn in (("cotas.svg", cotas), ("mobiliado.svg", mobiliado)):
        svg = fn()
        assert svg.count("<rect") >= 1 and "QUARTO 1" in svg
        open(os.path.join(OUT, nome), "w", encoding="utf-8").write(svg)
        print("->", nome, len(svg) // 1024, "KB")
    # PDFs separados, uma página paisagem cada (vetorial, via PyMuPDF)
    import fitz
    for svg_name, pdf_name in (("cotas.svg", "planta-1-medidas.pdf"), ("mobiliado.svg", "planta-2-moveis.pdf")):
        d = fitz.open("svg", open(os.path.join(OUT, svg_name), "rb").read())
        fitz.open("pdf", d.convert_to_pdf()).save(os.path.join(OUT, pdf_name))
        print("->", pdf_name)
