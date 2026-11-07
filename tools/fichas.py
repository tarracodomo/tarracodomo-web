import re
import shutil
from pathlib import Path

from PIL import Image

RAIZ = Path(".")
IMG = RAIZ / "img"
CREDITO = "https://github.com/tarracodomo/tarracodomo-web/blob/main/ATTRIBUCION.md"

MAPA = {
    "doc-esp32-cam": ("esp32-cam.webp", "Placa ESP32-CAM con c\u00e1mara OV2640 y ranura para tarjeta microSD"),
    "doc-esp32": ("esp32-devkit.webp", "Placa de desarrollo ESP32 DevKit con m\u00f3dulo WROOM-32"),
    "doc-hc-sr04": ("sensor-ultrasonidos.webp", "M\u00f3dulo de sensor de distancia por ultrasonidos HC-SR04"),
    "doc-esp8266": ("esp8266.webp", "M\u00f3dulo ESP8266 en placa de desarrollo con antena WiFi"),
    "doc-wemos-d1": ("wemos-d1-mini.webp", "Placa WeMos D1 Mini basada en ESP8266"),
    "doc-wemos-d1-r32": ("esp32-dev-board.webp", "Placa ESP32 en formato Wemos D1 R32"),
    "doc-dht": ("dht11.webp", "Sensor de temperatura y humedad DHT11 conectado a un ESP8266"),
}

PATRON = re.compile(
    r"<h2([^>]*)>\s*Especificaciones t[e\u00e9]cnicas\s*</h2>\s*(<table class=\"spec\">.*?</table>)",
    re.S,
)

ESTILOS_EN_LINEA = [
    ('<div style="display:flex;gap:26px;align-items:flex-start;flex-wrap:wrap;margin-bottom:24px">', '<div class="ficha">'),
    ('<figure style="flex:0 0 300px;max-width:300px;margin:0">', "<figure>"),
    ('<div style="flex:1 1 320px;min-width:260px">', '<div class="datos">'),
    (' style="width:100%;height:auto;border-radius:10px;border:1px solid #e5e5e5"', ""),
    ('<h2 style="margin-top:0">', "<h2>"),
]


def bloque(archivo, alt, ancho, alto):
    return (
        '<div class="ficha">\n'
        "<figure>\n"
        f'<img src="/img/{archivo}" alt="{alt}" width="{ancho}" height="{alto}" '
        'loading="lazy" decoding="async">\n'
        f"<figcaption>Foto de Wikimedia Commons. <a href=\"{CREDITO}\">Cr\u00e9dito</a>.</figcaption>\n"
        "</figure>\n"
        '<div class="datos">\n'
    )


def main():
    cambiadas = []
    for archivo_html in sorted(RAIZ.glob("*.html")):
        texto = archivo_html.read_text(encoding="utf-8")
        original = texto

        for viejo, nuevo in ESTILOS_EN_LINEA:
            texto = texto.replace(viejo, nuevo)

        if 'class="ficha"' not in texto:
            datos = MAPA.get(archivo_html.stem)
            if datos:
                imagen, alt = datos
                ruta = IMG / imagen
                if ruta.exists():
                    with Image.open(ruta) as im:
                        ancho, alto = im.size

                    def sustituir(m):
                        return (
                            bloque(imagen, alt, ancho, alto)
                            + f"<h2{m.group(1)}>Especificaciones t\u00e9cnicas</h2>\n"
                            + m.group(2)
                            + "\n</div>\n</div>"
                        )

                    nuevo_texto = PATRON.sub(sustituir, texto, count=1)
                    if nuevo_texto != texto:
                        texto = nuevo_texto

        if texto != original:
            archivo_html.write_text(texto, encoding="utf-8")
            cambiadas.append(archivo_html.stem)

    for archivo_html in sorted(RAIZ.glob("*.html")):
        if archivo_html.stem in ("index", "404"):
            continue
        destino = RAIZ / archivo_html.stem
        destino.mkdir(exist_ok=True)
        shutil.copyfile(archivo_html, destino / "index.html")

    print(f"Paginas modificadas: {len(cambiadas)}")
    for nombre in cambiadas:
        print(" -", nombre)


if __name__ == "__main__":
    main()
