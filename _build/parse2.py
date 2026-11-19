import re, json, html, sys
sys.path.insert(0,'.')
from parse import text, unwrap, body_blocks
def parse(path):
    s=open(path,encoding='utf-8').read()
    lds=[]
    for m in re.finditer(r'type="application/ld\+json">(.*?)</script>',s,re.S):
        try: lds.append(json.loads(m.group(1)))
        except Exception: pass
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S); title=text(h1.group(1))
    prods=[d for d in lds if d.get('@type')=='Product']
    by_img={}; 
    for d in prods: by_img.setdefault(d.get('image'),d)
    items=[]
    for d in lds:
        if d.get('@type')!='ImageObject': continue
        desc=d.get('description') or ''
        if not desc.strip(): continue
        p=by_img.get(d.get('contentUrl'))
        m=re.match(r'\s*<(h2|strong)>(.*?)</\1>(.*)',desc,re.S)
        if m: name=text(m.group(2)); body=m.group(3)
        elif p: name=text(((p.get('brand') or '')+' '+p.get('name','')) if p.get('brand') and p.get('brand') not in p.get('name','') else p.get('name','')); body=desc
        else: continue
        if not p:   # image ids don't always match: fall back to brand + name
            key=re.sub(r'[^a-z0-9]','',name.lower())
            for d2 in prods:
                k2=re.sub(r'[^a-z0-9]','',((d2.get('brand') or '')+(d2.get('name') or '')).lower())
                if k2 and (k2==key or key.endswith(re.sub(r'[^a-z0-9]','',(d2.get('name') or '').lower())) and len(d2.get('name') or '')>6):
                    p=d2; break
        url=(p.get('url') or (p.get('offers') or {}).get('url')) if p else None
        if not url:   # last resort: first store link in the description
            for a in re.findall(r'href="([^"]+)"',body):
                if 'refinery29.com' not in a and not a.startswith('/'): url=a; break
        items.append({'name':name,'desc':text(body),'url':unwrap(url) if url else None})
    blocks=body_blocks(s)
    if items:
        intro=[v for k,v in blocks if k=='p']
        return {'title':title,'intro':intro,'items':items,'type':'list'}
    return {'title':title,'blocks':blocks,'type':'blocks'}
out=[]
import os
RAW=os.environ.get('R29_RAW','raw')
for slug in open('articles.txt').read().split():
    a=parse(f'{RAW}/{slug}.html'); a['slug']=slug; out.append(a)
    n=len(a.get('items') or [x for x in a.get('blocks',[]) if x[0]=='i'])
    print(f"{slug:60} {a['type']:6} {n:3} nourl={sum(1 for i in a.get('items',[]) if not i['url'])}")
json.dump(out,open('data.json','w'),ensure_ascii=False,indent=1)
