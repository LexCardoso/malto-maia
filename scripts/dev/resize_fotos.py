"""Otimiza fotos de FOTOS/ (originais, locais) para static/img/fotos/ (web).

Corrige rotacao EXIF do celular, redimensiona pro tamanho-alvo e salva JPEG
progressivo otimizado. As originais ficam fora do git (FOTOS/ no .gitignore);
so as versoes web entram no repo. Rodar com o venv:

    venv\\Scripts\\python.exe scripts\\dev\\resize_fotos.py
"""
from pathlib import Path

from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent.parent.parent
SRC = BASE / "FOTOS"
OUT = BASE / "static" / "img" / "fotos"
OUT.mkdir(parents=True, exist_ok=True)

# (arquivo original, nome web, maior lado em px)
JOBS = [
    ("WhatsApp Image 2026-05-31 at 20.42.14.jpeg", "hero-cappuccino.jpg", 1400),
    ("WhatsApp Image 2026-06-01 at 18.15.56.jpeg", "fachada.jpg", 1500),
    ("WhatsApp Image 2026-05-31 at 20.42.12 (1).jpeg", "destaque-cappuccino.jpg", 900),
    ("WhatsApp Image 2026-05-31 at 20.42.12 (3).jpeg", "destaque-pao-de-queijo.jpg", 900),
    ("WhatsApp Image 2026-05-31 at 20.42.16 (1).jpeg", "gal-jardim.jpg", 1000),
    ("WhatsApp Image 2026-06-01 at 18.13.14.jpeg", "gal-lousa.jpg", 1300),
    ("WhatsApp Image 2026-05-31 at 20.42.13 (1).jpeg", "gal-cafe.jpg", 1000),
    ("WhatsApp Image 2026-06-01 at 18.13.31.jpeg", "gal-interior.jpg", 1000),
    ("WhatsApp Image 2026-05-31 at 20.42.16.jpeg", "gal-mesa.jpg", 1000),
    ("WhatsApp Image 2026-05-31 at 20.44.53.jpeg", "encomenda.jpg", 1100),
    ("WhatsApp Image 2026-06-01 at 18.15.32.jpeg", "visite.jpg", 1100),
    ("WhatsApp Image 2026-06-01 at 18.13.22.jpeg", "conceito.jpg", 1100),
]


def main():
    if not SRC.exists():
        print(f"FOTOS/ nao encontrada em {SRC}")
        return
    total = 0
    for src_name, dest_name, max_edge in JOBS:
        src = SRC / src_name
        if not src.exists():
            print(f"  FALTA: {src_name}")
            continue
        img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        img.thumbnail((max_edge, max_edge), Image.LANCZOS)
        dest = OUT / dest_name
        img.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
        kb = dest.stat().st_size // 1024
        total += kb
        print(f"  {dest_name:28s} {img.width}x{img.height}  {kb}KB")
    print(f"OK — {total}KB no total em {OUT}")


if __name__ == "__main__":
    main()
