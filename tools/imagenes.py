import io
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"
UA = {"User-Agent": "tarracodomo-web/1.0 (https://tarracodomo.com)"}
ANCHO = 1200

IMAGENES = [
    ("ESP32-CAM.jpg", "esp32-cam.webp", "Placa ESP32-CAM con c\u00e1mara integrada y lector de tarjeta microSD"),
    ("ESP32.jpg", "esp32-devkit.webp", "Placa de desarrollo ESP32 DevKit con m\u00f3dulo WROOM-32"),
    ("ESP32 Dev Board.jpg", "esp32-dev-board.webp", "Placa ESP32 sobre mesa, vista general de los pines laterales"),
    ("ESP32 on Lolin32 Lite clone board cropped.jpg", "esp32-lolin32.webp", "Placa ESP32 formato Lolin32 Lite con bater\u00eda de litio"),
    ("ESP32-S3 on paper.jpg", "esp32-s3.webp", "Placa ESP32-S3 vista desde arriba sobre fondo blanco"),
    ("ESP-WROOM-32.jpg", "esp-wroom-32.webp", "M\u00f3dulo ESP-WROOM-32 sin placa de desarrollo"),
    ("Meshtastic T-Beam.jpg", "meshtastic-tbeam.webp", "Dispositivo Meshtastic T-Beam con m\u00f3dulo LoRa y GPS"),
    ("TTGO Lora32 Node.jpeg", "ttgo-lora32.webp", "Placa TTGO LoRa32 para redes LoRa"),
    ("BMP280Sensor.jpg", "bmp280.webp", "M\u00f3dulo sensor de presi\u00f3n y temperatura BMP280"),
    ("Capteur-ultrasons.jpg", "sensor-ultrasonidos.webp", "M\u00f3dulo de sensor de distancia por ultrasonidos"),
    ("Leaf Sensor.jpg", "sensor-hoja.webp", "Sensor de humedad de hoja para plantas"),
    ("Esp8266.jpg", "esp8266.webp", "M\u00f3dulo ESP8266 en placa de desarrollo con antena WiFi"),
    ("WeMos D1 Mini front.jpg", "wemos-d1-mini.webp", "Placa WeMos D1 Mini basada en ESP8266"),
    ("ESP8266 with DHT11.jpg", "dht11.webp", "Sensor de temperatura y humedad DHT11 conectado a un ESP8266"),
    ("Maxdetect Humidity and Temperature Sensor - RHT03 10167.jpg", "dht22.webp", "Sensor de temperatura y humedad DHT22, tambi\u00e9n llamado RHT03"),
]


def descargar(nombre):
    url = BASE + urllib.parse.quote(nombre) + f"?width={ANCHO}"
    peticion = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(peticion, timeout=90) as respuesta:
        return respuesta.read()


def main():
    destino = Path("img")
    destino.mkdir(exist_ok=True)
    filas = []
    for origen, salida, alt in IMAGENES:
        try:
            datos = descargar(origen)
            imagen = Image.open(io.BytesIO(datos)).convert("RGB")
            imagen.thumbnail((ANCHO, 1600), Image.LANCZOS)
            ruta = destino / salida
            imagen.save(ruta, "WEBP", quality=80, method=6)
            filas.append((salida, origen, imagen.width, imagen.height, ruta.stat().st_size, alt))
        except Exception as error:
            filas.append((salida, origen, 0, 0, 0, f"ERROR: {error}"))

    lineas = [
        "# Cr\u00e9ditos de im\u00e1genes",
        "",
        "Archivos descargados de Wikimedia Commons. Antes de publicar, abre la p\u00e1gina de cada archivo,",
        "anota el autor y la licencia exacta, y sustituye los campos pendientes.",
        "",
        "| Archivo local | Original en Commons | Tama\u00f1o | Peso | Licencia | Autor |",
        "|---|---|---|---|---|---|",
    ]
    for salida, origen, ancho, alto, peso, alt in filas:
        kb = f"{peso / 1024:.0f} KB" if peso else alt
        enlace = BASE + urllib.parse.quote(origen)
        lineas.append(f"| `img/{salida}` | [{origen}]({enlace}) | {ancho}x{alto} | {kb} | PENDIENTE | PENDIENTE |")
    lineas.append("")
    lineas.append("## Textos alternativos previstos")
    lineas.append("")
    for salida, origen, ancho, alto, peso, alt in filas:
        lineas.append(f"- `img/{salida}`: {alt}")
    Path("ATTRIBUCION.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(f"{s} -> {p} bytes" for s, o, w, h, p, a in filas))


if __name__ == "__main__":
    main()
