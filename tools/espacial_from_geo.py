"""Passo 1 (interface A): converte inputs/geo.json (vetores do PDF, formato no README) no contrato 01_espacial.

Uso: python tools/espacial_from_geo.py [inputs/geo.json] [--projeto nome]   (grava outputs/01_espacial/<projeto>.json)
A usable_bounding_box aqui é o interior menos a faixa que contém a varredura da porta;
o refinamento por uso (cama, armário) fica no orquestrador com o simulador.
# ponytail: caixa única por cômodo; gerar por uso quando o passo 2 pedir.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMES = dict(banho="Banheiro", nicho="Nicho do box", q1="Quarto 1", q1alc="Alcova quarto 1", q2="Quarto 2",
             sala="Sala", entrada="Entrada", cozinha="Cozinha", lavanderia="Lavanderia", lavabo="Lavabo",
             escritorio="Escritório", varanda="Varanda")


def parede(room, hx, hy):
    x, y, w, h = room
    d = {"oeste": abs(hx - x), "leste": abs(hx - (x + w)), "norte": abs(hy - y), "sul": abs(hy - (y + h))}
    return min(d, key=d.get)


def converter(g):
    rooms = {}
    for rid, (x, y, w, h) in g["rooms"].items():
        portas, caixa = [], {"x": x, "y": y, "w": w, "h": h}
        for d in g["doors"]:
            if d["room"] != rid:
                continue
            r = d["r"]
            vx = d["hx"] if d["sx"] > 0 else d["hx"] - r
            vy = d["hy"] if d["sy"] > 0 else d["hy"] - r
            portas.append({"parede": parede((x, y, w, h), d["hx"], d["hy"]), "vao": r, "abre_para": "dentro",
                           "varredura": {"x": round(vx, 3), "y": round(vy, 3), "w": r, "h": r}})
            # fica com a maior faixa do interior que não contém a varredura
            opcoes = {
                "cima": ((vy - y) * w, {"x": x, "y": y, "w": w, "h": vy - y}),
                "baixo": ((y + h - vy - r) * w, {"x": x, "y": vy + r, "w": w, "h": y + h - vy - r}),
                "esq": ((vx - x) * h, {"x": x, "y": y, "w": vx - x, "h": h}),
                "dir": ((x + w - vx - r) * h, {"x": vx + r, "y": y, "w": x + w - vx - r, "h": h}),
            }
            caixa = max(opcoes.values(), key=lambda t: t[0])[1]
        caixa = {k: round(v, 3) for k, v in caixa.items()}
        rooms[rid] = {
            "nome": NOMES.get(rid, rid),
            "interior": {"x": x, "y": y, "w": w, "h": h},
            "portas": portas,
            "janelas": [],  # ponytail: janelas ainda não estão no geo.json; ver docs/manual-plantas-layout.md §2
            "existente": [],
            "usable_bounding_boxes": [{"uso": "livre", "x": caixa["x"], "y": caixa["y"],
                                       "w_max": caixa["w"], "h_max": caixa["h"], "encosta": None, "cabe": True}],
        }
    return {"projeto": g.get("projeto", "exemplo"), "unidade": "m", "escala_confianca": "vetorial",
            "escala_base": g.get("escala_base", "vetores do PDF da planta"), "rooms": rooms, "duvidas": []}


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    src = a[0] if a else os.path.join(BASE, "inputs", "geo.json")
    out = converter(json.load(open(src, encoding="utf-8")))
    if "--projeto" in sys.argv:
        out["projeto"] = sys.argv[sys.argv.index("--projeto") + 1]
    # self-check: em nenhum cômodo a caixa útil pode invadir a varredura de uma porta
    for rid, r in out["rooms"].items():
        b = r["usable_bounding_boxes"][0]
        for v in (p["varredura"] for p in r["portas"]):
            fora = (b["x"] >= v["x"] + v["w"] - 1e-6 or b["x"] + b["w_max"] <= v["x"] + 1e-6
                    or b["y"] >= v["y"] + v["h"] - 1e-6 or b["y"] + b["h_max"] <= v["y"] + 1e-6)
            assert fora, (rid, b, v)
    dst = os.path.join(BASE, "outputs", "01_espacial", out["projeto"] + ".json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:  # não usar stdout: no Windows o redirect sai em cp1252
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("->", dst)
