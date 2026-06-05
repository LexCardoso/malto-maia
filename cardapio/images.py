"""Processamento da foto do produto antes de gravar NO BANCO.

Render free nao tem disco persistente, entao a imagem vai como bytes no Postgres.
Para o banco nao estourar, a foto entra redimensionada (maior lado <= MAX_LADO) e
comprimida em JPEG. Uma foto de celular (5-8 MB) vira ~150-300 KB.
"""
import io

from PIL import Image, ImageOps

MAX_LADO = 1280
QUALIDADE = 82
# Rede de seguranca: o navegador ja recorta/encolhe antes de enviar (cropper.js),
# entao o servidor quase sempre recebe uma imagem pequena. O limite alto cobre o
# caso de JS desligado/falho — o Pillow reduz de qualquer jeito.
TAMANHO_MAX_ENTRADA = 25 * 1024 * 1024  # 25 MB no upload cru


class FotoInvalida(Exception):
    """Arquivo enviado nao e uma imagem valida (ou e grande demais)."""


def processar_foto(arquivo):
    """Recebe um UploadedFile e devolve (bytes_jpeg, "image/jpeg").

    Respeita a orientacao EXIF do celular, achata transparencia em branco e
    reduz o maior lado para MAX_LADO mantendo a proporcao.
    """
    if getattr(arquivo, "size", 0) and arquivo.size > TAMANHO_MAX_ENTRADA:
        raise FotoInvalida("Imagem muito grande (máximo 12 MB).")
    try:
        img = Image.open(arquivo)
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "LA", "P"):
            fundo = Image.new("RGB", img.size, (255, 255, 255))
            img = img.convert("RGBA")
            fundo.paste(img, mask=img.split()[-1])
            img = fundo
        else:
            img = img.convert("RGB")
    except FotoInvalida:
        raise
    except Exception as exc:  # noqa: BLE001 — qualquer erro do Pillow = imagem invalida
        raise FotoInvalida("Arquivo não é uma imagem válida.") from exc
    img.thumbnail((MAX_LADO, MAX_LADO))
    buff = io.BytesIO()
    img.save(buff, format="JPEG", quality=QUALIDADE, optimize=True)
    return buff.getvalue(), "image/jpeg"
