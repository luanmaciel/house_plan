"""Passo 1 (interface B): manda a imagem da planta ao Gemini e imprime o JSON espacial.

Uso: python tools/gemini_vision.py inputs/plantas/x.png [--projeto x] [--usos "q1: cama_casal, criado x2"]
Requer GEMINI_API_KEY no ambiente ou em .env na raiz.
"""
import base64
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "gemini-2.5-pro"


def api_key():
    k = os.environ.get("GEMINI_API_KEY")
    env = os.path.join(BASE, ".env")
    if not k and os.path.exists(env):
        for ln in open(env, encoding="utf-8"):
            if ln.startswith("GEMINI_API_KEY="):
                k = ln.split("=", 1)[1].strip().strip('"')
    if not k:
        sys.exit("GEMINI_API_KEY ausente (defina no ambiente ou em .env)")
    return k


def prompt(projeto, usos):
    md = open(os.path.join(BASE, "system_prompts.md"), encoding="utf-8").read()
    bloco = md.split("## 1. Gemini")[1].split("```")[1]
    return bloco.replace("{{PROJETO}}", projeto).replace("{{USOS_POR_COMODO}}", usos)


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    img = a[0]
    projeto = a[a.index("--projeto") + 1] if "--projeto" in a else os.path.splitext(os.path.basename(img))[0]
    usos = a[a.index("--usos") + 1] if "--usos" in a else "todos os cômodos: cama, armario, mesa, sofa conforme o tipo"
    low = img.lower()
    mime = "application/pdf" if low.endswith(".pdf") else "image/png" if low.endswith(".png") else "image/jpeg"
    body = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(open(img, "rb").read()).decode()}},
            {"text": prompt(projeto, usos)},
        ]}],
        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key()},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        txt = json.load(r)["candidates"][0]["content"]["parts"][0]["text"]
    txt = re.sub(r"^```(json)?|```$", "", txt.strip(), flags=re.M)
    print(json.dumps(json.loads(txt), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
