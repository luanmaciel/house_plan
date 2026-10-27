"""Edita as fotos do banheiro com o Gemini de imagem (Nano Banana Pro): piso marfim,
gabinete novo em madeira clara com tampo de quartzo, espelho novo com moldura.

Uso: python tools/banheiro_nano.py [1 2 3] [--modelo gemini-3-pro-image-preview] [--extra "texto a mais no prompt"]
Saida: out/banheiro_nb_{n}.png + out/banheiro_nb_antes_depois.jpg
Requer GEMINI_API_KEY no ambiente ou em .env na raiz (mesma leitura de tools/gemini_vision.py).
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gemini_vision import api_key  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://generativelanguage.googleapis.com/v1beta/models"

PRESERVE = (
    "Preserve exatamente a camera, o enquadramento, a perspectiva, as paredes e azulejos, o teto, a janela, "
    "a iluminacao e todos os objetos nao mencionados. Nao amplie nem redesenhe o banheiro. "
    "Resultado fotorrealista, como uma foto do mesmo imovel depois da reforma."
)
PISO = ("o piso de granito verde por porcelanato polido cor marfim (bege muito claro), placas grandes 80x80 cm "
        "com rejunte fino da mesma cor, respeitando a perspectiva do chao")
GABINETE = ("o gabinete branco sob a pia por um gabinete suspenso em madeira clara (freijo) com gavetas e puxadores "
            "discretos, tampo de quartzo branco, mantendo a cuba branca de apoio e a torneira no mesmo lugar")
ESPELHO = ("o espelho colado ate o teto por um espelho retangular horizontal com moldura fina de madeira clara, "
           "centralizado sobre a cuba, com azulejo branco na parede ao redor")

PROMPTS = {
    1: f"Edite esta foto de banheiro. Troque APENAS: (1) {PISO}; (2) {GABINETE}; (3) {ESPELHO}. {PRESERVE}",
    2: (f"Edite esta foto de banheiro. Troque APENAS {PISO}, incluindo o piso interno do box (visto atraves do vidro, "
        f"com o ralo no mesmo lugar). Mantenha o box de vidro verde, ferragens, chuveiro e paredes exatamente iguais. {PRESERVE}"),
    3: f"Edite esta foto de banheiro. Troque APENAS: (1) {PISO}; (2) {GABINETE}; (3) {ESPELHO}. {PRESERVE}",
}


def req(path, body=None):
    r = urllib.request.Request(URL + path, data=json.dumps(body).encode() if body else None,
                               method="POST" if body else "GET",
                               headers={"Content-Type": "application/json", "x-goog-api-key": api_key()})
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        msg = re.sub(r"\s+", " ", corpo)[:600]
        sys.exit(f"HTTP {e.code} em {path.split(':')[0]}: {msg}")


def escolher_modelo():
    nomes = [m["name"].split("/")[-1] for m in req("?pageSize=200")["models"]]
    for chave in ("3-pro-image", "pro-image", "flash-image"):
        cand = [n for n in nomes if chave in n]
        if cand:
            return sorted(cand)[-1]
    sys.exit("nenhum modelo de imagem disponivel para esta chave: " + ", ".join(nomes))


def gerar(n, modelo, extra=""):
    img = os.path.join(BASE, "inputs", "fotos", f"banheiro_{n}.jpg")
    body = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(open(img, "rb").read()).decode()}},
            {"text": PROMPTS[n] + (" " + extra if extra else "")},
        ]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    if "pro" in modelo:
        body["generationConfig"]["imageConfig"] = {"imageSize": "2K"}
    parts = req(f"/{modelo}:generateContent", body)["candidates"][0]["content"]["parts"]
    for p in parts:
        dado = p.get("inlineData") or p.get("inline_data")
        if dado:
            dest = os.path.join(BASE, "out", f"banheiro_nb_{n}.png")
            open(dest, "wb").write(base64.b64decode(dado["data"]))
            print(f"foto {n}: {dest}")
        elif p.get("text"):
            print(f"foto {n} (texto): {p['text'][:300]}")


def folha(ns):
    h = 900
    tiles = []
    for n in ns:
        for path in (f"inputs/fotos/banheiro_{n}.jpg", f"out/banheiro_nb_{n}.png"):
            im = Image.open(os.path.join(BASE, path)).convert("RGB")
            tiles.append(im.resize((int(im.width * h / im.height), h)))
    sheet = Image.new("RGB", (sum(t.width for t in tiles) + 10 * (len(tiles) - 1), h), "white")
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width + 10
    sheet.save(os.path.join(BASE, "out", "banheiro_nb_antes_depois.jpg"), quality=88)


def main():
    a = sys.argv[1:]
    modelo = a[a.index("--modelo") + 1] if "--modelo" in a else escolher_modelo()
    extra = a[a.index("--extra") + 1] if "--extra" in a else ""
    ns = [int(x) for x in a if x.isdigit()] or [1, 2, 3]
    print("modelo:", modelo)
    for n in ns:
        gerar(n, modelo, extra)
    folha([n for n in (1, 2, 3) if os.path.exists(os.path.join(BASE, "out", f"banheiro_nb_{n}.png"))])


if __name__ == "__main__":
    main()
