import io
from pathlib import Path
from PIL import Image, ImageOps

source = Path('img')
out = Path('conversion-prueba')
out.mkdir(exist_ok=True)
files = [p for p in source.rglob('*') if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
if not files:
    raise SystemExit('No hay JPG o PNG en img para convertir.')
for path in files:
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert('RGB')
        image.thumbnail((1200, 1600), Image.Resampling.LANCZOS)
        for quality in (82, 76, 70, 64, 58):
            buffer = io.BytesIO()
            image.save(buffer, 'WEBP', quality=quality, method=6)
            if buffer.tell() <= 120000:
                break
        target = out / path.relative_to(source).with_suffix('.webp')
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError(f'Nombre duplicado: {target}')
        target.write_bytes(buffer.getvalue())
        print(f'{path} -> {target}: {image.width}x{image.height}, {target.stat().st_size} bytes')
