import io
from pathlib import Path
from PIL import Image, ImageOps

IMG = Path('img')
LIMITE_BYTES = 120_000
UMBRAL_ORIGEN = 300_000
ANCHO_MAX, ALTO_MAX = 1200, 1600
CALIDADES = (82, 76, 70, 64, 58, 50)


def convertir(path):
    with Image.open(path) as original:
        imagen = ImageOps.exif_transpose(original).convert('RGB')
        imagen.thumbnail((ANCHO_MAX, ALTO_MAX), Image.Resampling.LANCZOS)
        for calidad in CALIDADES:
            buffer = io.BytesIO()
            imagen.save(buffer, 'WEBP', quality=calidad, method=6)
            if buffer.tell() <= LIMITE_BYTES:
                break
    return imagen.size, buffer.getvalue()


def main():
    archivos = sorted(
        p for p in IMG.glob('*')
        if p.is_file()
        and p.suffix.lower() in {'.jpg', '.jpeg', '.png'}
        and p.stat().st_size > UMBRAL_ORIGEN
    )
    if not archivos:
        print('No hay imagenes por encima de', UMBRAL_ORIGEN, 'bytes.')
        return

    total_antes = 0
    total_despues = 0
    for path in archivos:
        destino = path.with_name(path.stem + '-opt.webp')
        (ancho, alto), datos = convertir(path)
        destino.write_bytes(datos)
        antes = path.stat().st_size
        despues = len(datos)
        total_antes += antes
        total_despues += despues
        print('{0} | {1} KB -> {2} KB | {3}x{4}'.format(
            path.name, antes // 1024, despues // 1024, ancho, alto))

    print('Total: {0} KB -> {1} KB'.format(total_antes // 1024, total_despues // 1024))


if __name__ == '__main__':
    main()
