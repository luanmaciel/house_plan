"""Edita as fotos do banheiro (inputs/fotos/banheiro_{1,2,3}.jpg): piso marfim,
armario novo em madeira clara com tampo de quartzo branco, espelho novo com moldura.

Uso: python tools/banheiro_foto.py  -> out/banheiro_foto_{1,2,3}.jpg + out/banheiro_antes_depois.jpg
# ponytail: mascaras por poligono desenhado a mao sobre grade de 25 px; cores relativas ao
# branco da propria foto (as fotos sao escuras, branco real ~195). Troca por inpainting
# generativo (gemini-2.5-flash-image) quando houver GEMINI_API_KEY.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# fatores sobre o branco de referencia da foto
MARFIM = np.array([0.93, 0.92, 0.86])
MADEIRA = np.array([0.86, 0.74, 0.58])
QUARTZO = np.array([0.99, 0.99, 0.99])
QUARTZO_BORDA = np.array([0.90, 0.90, 0.90])
MOLDURA = np.array([0.62, 0.45, 0.30])

FOTOS = {
    1: dict(
        branco=(140, 220, 152, 540),
        piso=[(0, 1004), (300, 970), (320, 968), (320, 797), (600, 800), (709, 876), (709, 1094), (0, 1094)],
        piso_furos=[[(423, 780), (553, 780), (553, 800), (545, 833), (433, 833), (425, 800)],
                    [(380, 780), (418, 780), (418, 802), (380, 802)]],
        armario=[(0, 642), (320, 642), (320, 968), (300, 970), (0, 1004)],
        tampo=[(12, 570), (133, 570), (133, 592), (320, 598), (320, 642), (12, 642)],
        tampo_furos=[[(128, 530), (285, 530), (285, 592), (128, 592)]],
        espelho_velho=[(12, 10), (133, 200), (133, 570), (12, 570)],
        parede_faixa=(138, 158, 205, 526),
        espelho_novo=[(70, 246), (119, 298), (119, 461), (70, 443)],
    ),
    2: dict(
        branco=(50, 600, 250, 900),
        piso=[(160, 1080), (345, 897), (352, 900), (360, 942), (590, 1080)],
    ),
    3: dict(
        branco=(480, 300, 560, 420),
        piso=[(0, 982), (105, 945), (112, 1052), (150, 1095), (330, 1010), (548, 900), (602, 893), (685, 885), (685, 1110), (0, 1110)],
        armario=[(140, 655), (602, 614), (602, 893), (548, 900), (330, 1008), (150, 1095), (112, 1052)],
        tampo=[(95, 565), (598, 565), (598, 612), (140, 650), (95, 612)],
        tampo_borda=[(140, 627), (598, 595), (598, 612), (140, 650)],
        tampo_furos=[[(270, 528), (515, 522), (517, 602), (270, 600)]],
        espelho_velho=[(95, 10), (434, 190), (434, 566), (95, 566)],
        parede_faixa=(448, 500, 195, 515),
        parede_esq=(40, 90),
        espelho_novo=[(245, 240), (495, 290), (495, 427), (245, 442)],
    ),
}


def poly_mask(size, pts, furos=(), feather=1.0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.polygon(pts, fill=255)
    for f in furos:
        d.polygon(f, fill=0)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(feather)), float) / 255


def blend(img, mask, novo):
    m = mask[..., None]
    return img * (1 - m) + novo * m


def tint(rgb, mask, cor, blur=0, lim=(0.5, 1.2)):
    """Recolore mantendo o sombreamento (luminancia relativa a mediana da regiao)."""
    L = rgb @ [0.299, 0.587, 0.114]
    if blur:
        L = np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur)), float)
    med = np.median(L[mask > 0.5])
    return cor * np.clip(L / med, *lim)[..., None]


def ruido(shape, sigma=2.5):
    return np.random.default_rng(0).normal(0, sigma, shape)


def parede(rgb, x0, x1, ytop, ybot, esq=None):
    """Parede sintetica: base = gradiente entre a parede real a esquerda e a direita do espelho;
    textura = faixa de azulejo real (x0:x1) sem a media da linha, repetida espelhada."""
    w = x1 - x0
    idx = (np.arange(rgb.shape[1]) - x0) % (2 * w)
    src = np.where(idx < w, x0 + idx, x0 + 2 * w - 1 - idx)  # a faixa real fica no lugar dela
    faixa = rgb[:, x0:x1]
    dir_ = faixa.mean(axis=1, keepdims=True)
    tex = 0.5 * (faixa - dir_)[:, src - x0]  # meia amplitude: rejunte sugerido, sem 'cortina'
    if esq:
        esq_ = rgb[:, esq[0]:esq[1]].mean(axis=1, keepdims=True)
        t = np.clip((np.arange(rgb.shape[1]) - esq[1]) / (x0 - esq[1]), 0, 1)[None, :, None]
        base = esq_ * (1 - t) + dir_ * t
    else:
        base = np.repeat(dir_, rgb.shape[1], axis=1)
    p = base + tex
    p[:ytop] = base[ytop + 5]
    p[ybot:] = p[ybot - 2]  # sem cuba/torneira que aparecem na faixa perto do tampo
    return p


def editar(n):
    cfg = FOTOS[n]
    im = Image.open(os.path.join(BASE, "inputs", "fotos", f"banheiro_{n}.jpg")).convert("RGB")
    rgb = np.asarray(im, float)
    out = rgb.copy()
    x0, y0, x1, y1 = cfg["branco"]
    wref = rgb[y0:y1, x0:x1].reshape(-1, 3).mean(0)

    # 1. espelho: parede no lugar do espelho antigo, depois recorta o novo com moldura
    if "espelho_velho" in cfg:
        out = blend(out, poly_mask(im.size, cfg["espelho_velho"]), parede(rgb, *cfg["parede_faixa"], cfg.get("parede_esq")))
        out = blend(out, poly_mask(im.size, cfg["espelho_novo"], feather=0.6), rgb * 0.93)  # reflexo original, vidro
        fr = Image.fromarray(out.clip(0, 255).astype(np.uint8))
        d = ImageDraw.Draw(fr)
        d.polygon(cfg["espelho_novo"], outline=tuple((wref * MOLDURA).astype(int)), width=9)
        d.polygon(cfg["espelho_novo"], outline=tuple((wref * MOLDURA * 0.6).astype(int)), width=2)
        out = np.asarray(fr, float)

    # 2. tampo: quartzo branco onde era granito preto (cuba preservada pelo furo)
    if "tampo" in cfg:
        out = blend(out, poly_mask(im.size, cfg["tampo"], cfg.get("tampo_furos", ())), wref * QUARTZO + ruido(rgb.shape))
        if "tampo_borda" in cfg:
            out = blend(out, poly_mask(im.size, cfg["tampo_borda"]), wref * QUARTZO_BORDA + ruido(rgb.shape))

    # 3. armario: madeira clara, mantendo puxadores e frisos pelo sombreamento
    if "armario" in cfg:
        m = poly_mask(im.size, cfg["armario"])
        out = blend(out, m, tint(rgb, m, wref * MADEIRA, lim=(0.35, 1.2)))

    # 4. piso marfim: borra o granito e reaplica so o sombreamento
    m = poly_mask(im.size, cfg["piso"], cfg.get("piso_furos", ()))
    out = blend(out, m, tint(rgb, m, wref * MARFIM, blur=20, lim=(0.55, 1.1)) + ruido(rgb.shape, 1.5))

    res = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    res.save(os.path.join(BASE, "out", f"banheiro_foto_{n}.jpg"), quality=92)
    return im, res


def main():
    pares = [editar(n) for n in (1, 2, 3)]
    h = 900
    tiles = [x.resize((int(x.width * h / x.height), h)) for a, b in pares for x in (a, b)]
    sheet = Image.new("RGB", (sum(t.width for t in tiles) + 10 * (len(tiles) - 1), h), "white")
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width + 10
    sheet.save(os.path.join(BASE, "out", "banheiro_antes_depois.jpg"), quality=88)


if __name__ == "__main__":
    main()
