import json, html, os, sys
out=sys.argv[1]
data=[a for a in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'data.json'))) if a['slug'] not in ('thoughtful-holiday-gift-quiz','thoughtful-holiday-gifts')]
e=lambda s: html.escape(s or '', quote=True)
def page(title, body, depth):
    return f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>{e(title)}</title>\n</head>\n<body marginwidth="18" marginheight="18">\n{body}\n</body>\n</html>\n'
def item(i):
    name=f'<a href="{e(i["url"])}">{e(i["name"])}</a>' if i.get('url') else e(i['name'])
    return f'<li>{name}<br>\n{e(i["desc"])}</li>' if i.get('desc') else f'<li>{name}</li>'
os.makedirs(f'{out}/refinery29',exist_ok=True)
# home
links='\n'.join(f'<li><a href="{h}">{t}</a></li>' for h,t in [('refinery29/the-art-of-giving.html','Refinery29'),('page-2/index.html','Vogue Gifts Under $100'),('page-3/index.html','Forbes Holiday Gift Guide'),('page-4/index.html','The Atlantic Gift Guide'),('page-5/index.html','Page 5')])
open(f'{out}/index.html','w').write(page('Home',f'<h1>Home</h1>\n<ul>\n{links}\n</ul>',0))
# page 2 is the Vogue collage (built from _build/page2_template.html)
_t=os.path.join(os.path.dirname(os.path.abspath(__file__)),'page2_template.html')
if os.path.exists(_t):
    os.makedirs(f'{out}/page-2',exist_ok=True)
    open(f'{out}/page-2/index.html','w').write(open(_t).read().replace('__IMAGES__',open(os.path.join(os.path.dirname(_t),'page2_images.json')).read().strip()))
# page 3 is the Forbes Vetted gift guide, text only (built from _build/page3_template.html + forbes_gifts.json)
_b=os.path.dirname(os.path.abspath(__file__))
import json as _json
_g=_json.load(open(os.path.join(_b,'forbes_gifts.json'),encoding='utf-8'))
for _x in _g: _x['price']=float(_x['price'] or 0)
# descriptions pasted into forbes_descriptions.txt (under each '### NNN Name' line) fill the hover panels
import re as _re
_d=os.path.join(_b,'forbes_descriptions.txt')
if os.path.exists(_d):
    for _m in _re.finditer(r'^### (\d{3}) [^\n]*\n(.*?)(?=^### |\Z)',open(_d,encoding='utf-8').read(),_re.S|_re.M):
        _txt=_re.sub(r'\n\s*\n+','\n',_m.group(2).strip())
        if _txt: _g[int(_m.group(1))-1]['description']=_txt
os.makedirs(f'{out}/page-3',exist_ok=True)
open(f'{out}/page-3/index.html','w',encoding='utf-8').write(open(os.path.join(_b,'page3_template.html'),encoding='utf-8').read().replace('__GIFTS__',_json.dumps(_g,ensure_ascii=False).replace('</','<\\/')))
# page 4 is The Atlantic's gift guide: images replaced by their text descriptions
# (built from _build/page4_template.html + atlantic_gifts.json + atlantic_descriptions.txt)
import html as _h
_A=_json.load(open(os.path.join(_b,'atlantic_gifts.json'),encoding='utf-8'))
_ad={}
_af=os.path.join(_b,'atlantic_descriptions.txt')
if os.path.exists(_af):
    for _m in _re.finditer(r'^### (\d{2}) [^\n]*\n(.*?)(?=^#{1,3} |\Z)',open(_af,encoding='utf-8').read(),_re.S|_re.M):
        _t=_m.group(2).strip()
        if _t: _ad[int(_m.group(1))]=[p.strip() for p in _re.split(r'\n\s*\n',_t) if p.strip()]
_slug=lambda s:_re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
_cols=['#006edd','#ff2a00','#ff3da5','#00a851','#ff2a00','#006edd']
_e=lambda s:_h.escape(s,quote=True)
_nav=''.join(f'<a href="#{_slug(s["t"])}">{_e(s["t"])}</a>' for s in _A)
_jump=''.join(f'<li><a href="#{_slug(s["t"])}" style="text-decoration-color:{_cols[i%6]}">{_e(s["t"])}</a></li>' for i,s in enumerate(_A))
_secs=[];_n=0
for s in _A:
    cards=[]
    for (title,alt,credit,by,byurl,buy,url) in s['c']:
        _n+=1
        desc=''.join(f'<p>{_e(p)}</p>' for p in _ad.get(_n,[]))
        name,_,role=by.partition(', ')
        byl=(f'<a href="{_e(byurl)}">{_e(name)}</a>' if byurl else _e(name))+(f', {_e(role)}' if role else '')
        buyh=f'<div class="buy"><a href="{_e(url)}" target="_blank" rel="noopener sponsored">{_e(buy)}</a></div>' if url else ''
        cards.append(f'<article class="card"><h3>{_e(title)}</h3><div class="desc">{desc}</div>{buyh}</article>')   # image box, photo credit and writer credit removed
    _secs.append(f'  <section class="gifts" id="{_slug(s["t"])}">\n    <h2>{_e(s["t"])}</h2>\n    <div class="grid">\n' + '\n'.join('      '+c for c in cards) + '\n    </div>\n  </section>')
os.makedirs(f'{out}/page-4',exist_ok=True)
open(f'{out}/page-4/index.html','w',encoding='utf-8').write(open(os.path.join(_b,'page4_template.html'),encoding='utf-8').read().replace('__NAV__',_nav).replace('__JUMP__',_jump).replace('__SECTIONS__','\n'.join(_secs)))
for n in range(5,6):
    os.makedirs(f'{out}/page-{n}',exist_ok=True)
    open(f'{out}/page-{n}/index.html','w').write(page(f'Page {n}',f'<p><a href="../index.html">Home</a></p>\n<h1>Page {n}</h1>\n<p>Coming soon.</p>',1))
# hub
hub=['<p><a href="../index.html">Home</a></p>','<p>The Art of Gifting<br>\nThe holidays aren’t just another shopping occasion to check off your to-do list. This year, we’re reimagining the gift guide: Think hand-picked items that will not only delight, but upgrade. Because as anyone who has ever received a perfect present knows, finding the ultimate present isn’t just about clicking “add to cart.” — it’s an art form.</p>','<p>A Gift For Everyone (Including Yourself)</p>','<p>']
hub.append('<br>\n'.join(f'<a href="{a["slug"]}.html">{e(a["title"])}</a>' for a in data))
hub.append('</p>')
open(f'{out}/refinery29/the-art-of-giving.html','w').write(page('The Art of Gifting','\n'.join(hub),1))

import re as _re
_PDIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),'products')
PRODUCTS={s:os.path.join(_PDIR,s) for s in (os.listdir(_PDIR) if os.path.isdir(_PDIR) else [])}
def _pslug(s): return _re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:70]
def product_pages(a):
    d=PRODUCTS.get(a['slug'])
    if not d: return
    os.makedirs(f'{out}/refinery29/products',exist_ok=True)
    for n,i in enumerate(a['items'],1):
        fp=os.path.join(d,f'{n:02d}.txt')
        if not os.path.exists(fp): continue
        blocks=[b.strip('\n') for b in open(fp,encoding='utf-8').read().strip().split('\n\n')]
        name=blocks[0].split('\n')[0]
        fn=f'products/{_pslug(i["name"])}.html'
        body=[f'<p><a href="../{a["slug"]}.html">{e(a["title"])}</a></p>']
        body+=['<p>'+'<br>\n'.join(e(l) for l in b.split('\n'))+'</p>' for b in blocks]
        open(f'{out}/refinery29/{fn}','w').write(page(name,'\n'.join(body),2))
        i['url']=fn
# articles
for a in data: product_pages(a)
for a in data:
    b=['<p><a href="the-art-of-giving.html">The Art of Gifting</a></p>',f'<p>{e(a["title"])}</p>']
    if a['type']=='list':
        b.append('<p>'+'<br>\n'.join(e(p) for p in a['intro'])+'</p>')
        b.append('<ul>\n'+'\n'.join(item(i) for i in a['items'])+'\n</ul>')
    elif not a.get('blocks'):
        b.append('<p>This article is an interactive quiz on Refinery29, so it has no list of items. Open the source link below to take the quiz.</p>')
    else:
        intro=[]; rest=a['blocks']
        while rest and rest[0][0]=='p': intro.append(rest[0][1]); rest=rest[1:]
        b.append('<p>'+'<br>\n'.join(e(p) for p in intro)+'</p>')
        ul=[]
        def flush():
            if ul: b.append('<ul>\n'+'\n'.join(ul)+'\n</ul>'); ul.clear()
        for k,v in rest:
            if k=='i': ul.append(item(v))
            else:
                flush(); b.append(f'<p>{e(v)}</p>' if k=='p' else f'<h2>{e(v)}</h2>')
        flush()
    open(f'{out}/refinery29/{a["slug"]}.html','w').write(page(a['title'],'\n'.join(b),1))
print(len(data),'articles')
