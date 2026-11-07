# Carpeta de imagenes

Todas las fotos del sitio van aqui, en WebP, con nombre descriptivo y sin espacios.

## Reglas

- Ancho maximo 1200 px, peso objetivo por debajo de 120 KB.
- Nombre en minusculas, guiones y en espanol: `sensor-pir-hc-sr501.webp`.
- Nada de `IMG_2841.webp` ni de mayusculas sueltas.
- Si una foto es de un cliente, no puede salir ninguna persona, matricula ni portal.

## Uso en las paginas

```html
<picture>
  <source srcset="/img/esp32-cam.webp" type="image/webp">
  <img src="/img/esp32-cam.jpg"
       alt="Placa ESP32-CAM con camara integrada y lector de tarjeta microSD"
       width="1200" height="800" loading="lazy" decoding="async">
</picture>
```

La primera imagen visible de cada pagina no lleva `loading="lazy"`.

## Creditos

Las fotos que vengan de Wikimedia Commons se anotan en `ATTRIBUCION.md`, en la raiz del repositorio, con autor y licencia. Las fotos propias no necesitan credito.
