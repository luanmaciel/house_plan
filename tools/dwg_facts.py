"""Extrai fatos do DWG do CAD (via ezdwg) para os agentes: linhas, arcos de porta,
textos de cômodo, cotas e blocos, já em METROS (o DWG está em unidades de metro).

Uso:  python tools/dwg_facts.py <planta.dwg>   -> out/dwg_facts.json + resumo no terminal
"""
import collections
import json
import math
import os
import sys

import ezdwg

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DWG = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
OUT = os.path.join(BASE, "out", "dwg_facts.json")


def xy(v):
    return [round(v[0], 3), round(v[1], 3)]


doc = ezdwg.read(DWG)
facts = dict(versao=doc.version, linhas=[], arcos_porta=[], textos=[], cotas=[], blocos=[])
for e in doc.modelspace().iter_entities():
    d = dict(e.dxf)
    if e.dxftype == "LINE":
        facts["linhas"].append(xy(d["start"]) + xy(d["end"]))
    elif e.dxftype == "ARC":
        facts["arcos_porta"].append(dict(dobradica=xy(d["center"]), raio=round(d["radius"], 2),
                                         de=round(d["start_angle"], 1), ate=round(d["end_angle"], 1)))
    elif e.dxftype == "TEXT":
        facts["textos"].append(dict(texto=d["text"], em=xy(d["insert"])))
    elif e.dxftype == "DIMENSION":
        facts["cotas"].append(dict(medida=round(d["actual_measurement"], 3), de=xy(d["defpoint2"]), ate=xy(d["defpoint3"])))
    elif e.dxftype == "INSERT":
        facts["blocos"].append(dict(nome=d["name"], em=xy(d["insert"]), rot=round(d.get("rotation") or 0, 1)))

xs = [v for l in facts["linhas"] for v in (l[0], l[2])]; ys = [v for l in facts["linhas"] for v in (l[1], l[3])]
facts["extensao_m"] = dict(largura=round(max(xs) - min(xs), 2), altura=round(max(ys) - min(ys), 2),
                           origem=[round(min(xs), 3), round(min(ys), 3)])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(facts, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"DWG {facts['versao']} em metros: {facts['extensao_m']['largura']} x {facts['extensao_m']['altura']} m")
print(f"linhas {len(facts['linhas'])} | arcos de porta {len(facts['arcos_porta'])} | textos {len(facts['textos'])} | cotas {len(facts['cotas'])} | blocos {len(facts['blocos'])}")
for a in facts["arcos_porta"]:
    print("  porta: dobradiça", a["dobradica"], "raio", a["raio"], "ângulos", a["de"], "->", a["ate"])
print("  cotas (m):", sorted({c["medida"] for c in facts["cotas"]}))
print("  blocos:", collections.Counter(b["nome"].split("$")[-1].strip() for b in facts["blocos"]).most_common())
print("saida:", OUT)
