from pathlib import Path
import shutil, json
from bs4 import BeautifulSoup
from PIL import Image

ROOT=Path('.')
YELLOW='doc-esp32-yellow-cheap-display'

def photo(soup,src,alt):
    path=ROOT/src.lstrip('/')
    if not path.exists():
        raise RuntimeError(f'No existe {src}; ejecuta Publicar fotos propias primero')
    with Image.open(path) as im:
        w,h=im.size
    return soup.new_tag('img',src=src,alt=alt,width=str(w),height=str(h),loading='lazy',decoding='async',style='display:block;width:100%;height:auto;max-height:420px;object-fit:contain;border-radius:12px')

source=ROOT/'doc-esp32-c6.html'
soup=BeautifulSoup(source.read_text(encoding='utf-8'),'html.parser')
name='ESP32 Yellow Cheap Display'
desc='Placa ESP32-2432S028 con pantalla integrada. Fotografías propias de Tarraco Domo.'
soup.title.string=name+' | Tarraco Domo'
url='https://tarracodomo.com/'+YELLOW
for tag in soup.select('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]'):
    tag['content']=desc
for tag in soup.select('meta[property="og:title"],meta[name="twitter:title"]'):
    tag['content']=name+' | Tarraco Domo'
for tag in soup.select('link[rel="canonical"]'):
    tag['href']=url
for tag in soup.select('meta[property="og:url"]'):
    tag['content']=url
for tag in soup.select('script[type="application/ld+json"]'):
    tag.string=json.dumps({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Inicio','item':'https://tarracodomo.com/'},{'@type':'ListItem','position':2,'name':'Documentación','item':'https://tarracodomo.com/documentacion'},{'@type':'ListItem','position':3,'name':name,'item':url}]},ensure_ascii=False)
main=soup.find('main');main.clear()
block=BeautifulSoup('<h1 class="pt">ESP32 Yellow Cheap Display</h1><p class="sub">Placa ESP32-2432S028 con pantalla integrada.</p><div class="doc"><div class="ficha"><figure><figcaption>Fotografía propia de Tarraco Domo.</figcaption></figure><div class="datos"><h2>Identificación de la placa</h2><table class="spec"><tr><th>Modelo</th><td>ESP32-2432S028</td></tr><tr><th>Nombre habitual</th><td>Yellow Cheap Display</td></tr><tr><th>Formato</th><td>Placa ESP32 con pantalla integrada</td></tr></table><p>Esta ficha corresponde a la placa con pantalla fotografiada, no a una ESP32-C6. Las características y conexiones deben verificarse en la documentación de la revisión concreta antes de cablearla.</p></div></div><p class="back"><a href="/documentacion">← Volver a Documentación</a></p></div>','html.parser')
for node in list(block.contents):
    main.append(node)
main.find('figure').insert(0,photo(soup,'/img/propias/esp32-pantalla.webp','Placa ESP32-2432S028 Yellow Cheap Display'))
(ROOT/(YELLOW+'.html')).write_text(str(soup),encoding='utf-8')

for path in sorted(ROOT.glob('*.html')):
    if path.stem=='doc-esp32-c6':
        continue
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    main=soup.find('main')
    if not main:
        continue
    changed=False
    for a in main.find_all('a',href=True):
        if a['href'].rstrip('/').removesuffix('.html')=='/doc-esp32-c6':
            a['href']='/'+YELLOW
            heading=a.find(['h2','h3','h4'])
            if heading:
                heading.string=name
                p=a.find('p')
                if p: p.string='Placa ESP32-2432S028 con pantalla integrada.'
                icon=a.select_one('.ic,.pic')
                if icon:
                    icon.clear();icon.append(photo(soup,'/img/propias/esp32-pantalla.webp',name))
                else:
                    old=a.find('img')
                    if old: old.replace_with(photo(soup,'/img/propias/esp32-pantalla.webp',name))
                    else: a.insert(0,photo(soup,'/img/propias/esp32-pantalla.webp',name))
            else:
                a.string=name
            changed=True
    for card in main.select('.card'):
        heading=card.find(['h2','h3','h4'])
        title=heading.get_text(' ',strip=True).lower() if heading else ''
        href=card.get('href','').rstrip('/').removesuffix('.html')
        if href=='/doc-pantallas-tactiles' or 'pantallas táctiles' in title:
            for img in card.find_all('img'): img.decompose()
            icon=card.select_one('.ic,.pic')
            if icon:
                icon.clear();icon.append(photo(soup,'/img/propias/panel-tactil.webp','Panel táctil Yellow Cheap Display'))
            else: card.insert(0,photo(soup,'/img/propias/panel-tactil.webp','Panel táctil Yellow Cheap Display'))
            changed=True
        if href in ('/doc-wemos-d1','/doc-wemos-d1-r32') or 'wemos d1' in title:
            for img in card.find_all('img'): img.decompose()
            changed=True
    if path.stem=='doc-pantallas-tactiles':
        figures=main.select('.ficha figure,figure.fotos-propias')
        for fig in figures:
            fig.clear();fig.append(photo(soup,'/img/propias/panel-tactil.webp','Panel táctil Yellow Cheap Display'))
            cap=soup.new_tag('figcaption');cap.string='Fotografía propia de Tarraco Domo.';fig.append(cap)
        changed=True
    if path.stem in ('doc-wemos-d1','doc-wemos-d1-r32'):
        for fig in main.select('.ficha figure,figure.fotos-propias'):
            fig.decompose()
        changed=True
    if changed:
        path.write_text(str(soup),encoding='utf-8')

publisher=ROOT/'tools/publicar_propias.py'
if publisher.exists():
    text=publisher.read_text(encoding='utf-8')
    text=text.replace("'Placa ESP32-2432S028 con pantalla','doc-pantallas-tactiles'", "'Placa ESP32-2432S028 con pantalla','"+YELLOW+"'")
    publisher.write_text(text,encoding='utf-8')
legacy=ROOT/'tools/fichas.py'
if legacy.exists():
    lines=legacy.read_text(encoding='utf-8').splitlines()
    legacy.write_text('\n'.join(line for line in lines if not line.lstrip().startswith(('"doc-wemos-d1":','"doc-wemos-d1-r32":')))+'\n',encoding='utf-8')
sitemap=ROOT/'sitemap.xml'
if sitemap.exists():
    sitemap.write_text(sitemap.read_text(encoding='utf-8').replace('https://tarracodomo.com/doc-esp32-c6',url),encoding='utf-8')
for path in ROOT.glob('*.html'):
    if path.stem not in ('index','404'):
        dest=ROOT/path.stem;dest.mkdir(exist_ok=True);shutil.copyfile(path,dest/'index.html')
