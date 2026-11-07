import io, re, shutil
from pathlib import Path
from PIL import Image, ImageOps
from bs4 import BeautifulSoup

ROOT = Path('.')
OUT = ROOT / 'img/propias'
OUT.mkdir(parents=True, exist_ok=True)
ITEMS = [
('arduino-uno.jpg','arduino-uno','Arduino Uno','doc-arduino-uno'),
('dht11-hw036.jpg','dht11','Sensor DHT11 HW036','doc-dht'),
('esp32-2432s028-yellow-cheap.jpg','esp32-pantalla','Placa ESP32-2432S028 con pantalla','doc-pantallas-tactiles'),
('esp32-cam-esp32cam-mb.jpg','esp32-cam','ESP32-CAM con adaptador ESP32-CAM-MB','doc-esp32-cam'),
('esp32.jpg','esp32','Placa ESP32','doc-esp32'),
('esp8266-mod-nodemcu.jpg','esp8266','Placa NodeMCU ESP8266','doc-esp8266'),
('hc-sr04.jpg','hc-sr04','Sensor ultrasónico HC-SR04','doc-hc-sr04'),
('hw-131-regulador-volt.jpg','hw131','Regulador de alimentación HW-131',None),
('hw-131-regulador-volt1.jpg','hw131-detalle','Detalle del regulador HW-131',None),
('hw-383-relay-module.jpg','rele','Módulo de relé HW-383','doc-reles'),
('lcd-092 .jpg','lcd092','Pantalla LCD 092',None),
('panel-tactil-yellow-cheap.jpg','panel-tactil','Panel táctil de la placa con pantalla','doc-pantallas-tactiles'),
('sensor-ir-infrarojos.jpg','sensor-ir','Sensor infrarrojo',None),
('sensor-pir-wemos-wify.jpg','sensor-pir','Sensor PIR y placa de control','doc-pir'),
('ttgo.jpg','ttgo','Placa TTGO','meshtastic'),
]
photos = []
for source, slug, label, page in ITEMS:
    path = ROOT / 'img' / source
    if not path.exists():
        raise RuntimeError(f'Falta el original: {source}')
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert('RGB')
        image.thumbnail((1000,1200), Image.Resampling.LANCZOS)
        for quality in (80,74,68,62,56):
            buf = io.BytesIO()
            image.save(buf,'WEBP',quality=quality,method=6)
            if buf.tell() <= 120000:
                break
        if buf.tell() > 120000:
            image.thumbnail((750,900), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            image.save(buf,'WEBP',quality=60,method=6)
        target = OUT / (slug+'.webp')
        target.write_bytes(buf.getvalue())
        photos.append(dict(slug=slug,label=label,page=page,src='/'+target.as_posix(),w=image.width,h=image.height,size=target.stat().st_size))

def image_tag(soup,p,card=False):
    tag = soup.new_tag('img',src=p['src'],alt=p['label'],width=str(p['w']),height=str(p['h']),loading='lazy',decoding='async')
    tag['style'] = 'display:block;width:100%;height:180px;object-fit:contain;border-radius:10px;margin-bottom:14px' if card else 'display:block;max-width:100%;height:auto;border-radius:12px'
    return tag

def figure(soup,group):
    tag=soup.new_tag('figure')
    tag['class']=['fotos-propias']
    for p in group:
        tag.append(image_tag(soup,p))
    caption=soup.new_tag('figcaption')
    caption.string='Fotografías propias de Tarraco Domo.'
    tag.append(caption)
    return tag

report=[]
for path in sorted(ROOT.glob('*.html')):
    text=path.read_text(encoding='utf-8')
    soup=BeautifulSoup(text,'html.parser')
    main=soup.find('main')
    if not main:
        continue
    changed=False
    group=[p for p in photos if p['page']==path.stem]
    if group:
        existing=main.select_one('.ficha')
        if existing:
            old=existing.find('figure')
            if old:
                old.replace_with(figure(soup,group))
            else:
                existing.insert(0,figure(soup,group))
        else:
            table=main.select_one('table.spec')
            if table:
                heading=table.find_previous_sibling('h2')
                wrapper=soup.new_tag('div',attrs={'class':'ficha'})
                (heading or table).insert_before(wrapper)
                wrapper.append(figure(soup,group))
                data=soup.new_tag('div',attrs={'class':'datos'})
                wrapper.append(data)
                if heading:
                    data.append(heading.extract())
                data.append(table.extract())
            else:
                anchor=main.find('h1')
                if anchor:
                    after=anchor.find_next_sibling('p',class_='sub') or anchor
                    old=main.select_one('figure.fotos-propias')
                    if old:
                        old.decompose()
                    after.insert_after(figure(soup,group))
        changed=True
    for card in main.select('.card'):
        heading=card.find(['h2','h3','h4'])
        if not heading:
            continue
        title=heading.get_text(' ',strip=True).lower()
        href=card.get('href','').split('?')[0].rstrip('/').removesuffix('.html').lstrip('/')
        matches=[p for p in photos if p['page'] and href==p['page']]
        if not matches:
            rules=[('esp32-cam','esp32-cam'),('esp8266','esp8266'),('dht','dht11'),('hc-sr04','hc-sr04'),('pir','sensor-pir'),('relé','rele'),('relés','rele'),('arduino uno','arduino-uno'),('hw-131','hw131'),('hw-383','rele'),('lcd','lcd092'),('ttgo','ttgo'),('táctil','esp32-pantalla')]
            for needle,slug in rules:
                if needle in title:
                    matches=[p for p in photos if p['slug']==slug]
                    break
            if not matches and title.strip()=='esp32':
                matches=[p for p in photos if p['slug']=='esp32']
        if not matches:
            continue
        p=matches[0]
        icon=card.select_one('.ic,.pic')
        if icon:
            icon.clear()
            icon.append(image_tag(soup,p,True))
        else:
            old=card.find('img')
            if old:
                old.replace_with(image_tag(soup,p,True))
            else:
                card.insert(0,image_tag(soup,p,True))
        changed=True
    if path.stem=='tecnologia':
        old=main.find(id='galeria-propia')
        if old:
            old.decompose()
        section=soup.new_tag('section',id='galeria-propia')
        h=soup.new_tag('h2');h.string='Nuestros componentes';section.append(h)
        grid=soup.new_tag('div',attrs={'class':'grid'})
        for p in photos:
            tile=soup.new_tag('div',attrs={'class':'card'})
            if p['page']:
                link=soup.new_tag('a',href='/'+p['page'])
                link.append(image_tag(soup,p,True));tile.append(link)
            else:
                tile.append(image_tag(soup,p,True))
            label=soup.new_tag('p');label.string=p['label'];tile.append(label)
            grid.append(tile)
        section.append(grid)
        note=soup.new_tag('p',attrs={'class':'note'});note.string='Fotografías propias de Tarraco Domo.';section.append(note)
        main.append(section)
        changed=True
    if changed:
        path.write_text(str(soup),encoding='utf-8')
        report.append(path.name)
for path in ROOT.glob('*.html'):
    if path.stem not in ('index','404'):
        dest=ROOT/path.stem
        dest.mkdir(exist_ok=True)
        shutil.copyfile(path,dest/'index.html')
lines=['# Fotos propias publicadas','', '## Imágenes', '']
lines += [f"- {p['slug']}: {p['w']} x {p['h']}, {p['size']} bytes" for p in photos]
lines += ['', '## HTML actualizados',''] + ['- '+name for name in report]
Path('FOTOS-PROPIAS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
