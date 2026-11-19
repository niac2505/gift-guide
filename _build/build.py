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
links='\n'.join(f'<li><a href="{h}">{t}</a></li>' for h,t in [('refinery29/the-art-of-giving.html','Refinery29'),('page-2/index.html','Page 2'),('page-3/index.html','Page 3'),('page-4/index.html','Page 4'),('page-5/index.html','Page 5')])
open(f'{out}/index.html','w').write(page('Home',f'<h1>Home</h1>\n<ul>\n{links}\n</ul>',0))
for n in range(2,6):
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
