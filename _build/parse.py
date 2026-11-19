import re, json, html, sys
def text(h):
    h=re.sub(r'<br\s*/?>',' ',h); h=re.sub(r'<[^>]+>','',h)
    return re.sub(r'\s+',' ',html.unescape(h)).strip()
def parse(path):
    s=open(path,encoding='utf-8').read()
    lds=[]
    for m in re.finditer(r'<script data-react-helmet="true" type="application/ld\+json">(.*?)</script>',s,re.S):
        try: lds.append(json.loads(m.group(1)))
        except Exception: pass
    title=None
    for d in lds:
        if d.get('@type') in ('NewsArticle','Article','BlogPosting') and d.get('headline'): title=d['headline']; break
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)
    if h1: title=text(h1.group(1))
    # intro paragraphs
    intro=[]
    b=re.search(r'<section class="body">(.*?)</section>',s,re.S)
    if b:
        for blk in re.findall(r'<div class="section-text">(.*?)</div>',b.group(1),re.S):
            for part in re.split(r'(?:<br\s*/?>\s*){2,}',blk):
                t=text(part)
                if t and 'sign up for our' not in t.lower(): intro.append(t)
    prod_by_img={}
    for d in lds:
        if d.get('@type')=='Product': prod_by_img.setdefault(d.get('image'),d.get('url') or (d.get('offers') or {}).get('url'))
    items=[]
    for d in lds:
        if d.get('@type')=='ImageObject' and (d.get('description') or '').startswith('<h2>'):
            m=re.match(r'<h2>(.*?)</h2>(.*)',d['description'],re.S)
            items.append({'name':text(m.group(1)),'desc':text(m.group(2)),'url':prod_by_img.get(d.get('contentUrl'))})
    return {'title':title,'intro':intro,'items':items}
if __name__=='__main__':
    out={}
    for slug in open('articles.txt').read().split():
        a=parse(f'raw/{slug}.html'); a['slug']=slug; out[slug]=a
        print(slug, len(a['intro']), len(a['items']), sum(1 for i in a['items'] if i['url']), '|', a['title'])
    json.dump(out,open('data.json','w'),ensure_ascii=False,indent=1)

from urllib.parse import urlparse, parse_qs
def unwrap(u):
    u=html.unescape(u)
    q=parse_qs(urlparse(u).query)
    for k in ('redirect','dest_url','u','url'):
        if k in q and q[k][0].startswith('http'): return q[k][0]
    return u
def body_blocks(s):
    """Walk the article body in order: text, headings, product cards."""
    a=s.find('<section class="body">'); b=s.find('</section>',a)
    # products may sit after </section> for multi-section bodies; take until editorial footer
    e=s.find('<footer',a)
    body=s[a:e if e>0 else b]
    blocks=[]
    tok=re.compile(r'<div class="section-text">(.*?)</div></div></div>|<div class="product"><a href="([^"]+)"[^>]*>(.*?)</a></div>',re.S)
    for m in tok.finditer(body):
        if m.group(1) is not None:
            blk=m.group(1)
            h=re.match(r'\s*<h[23][^>]*>(.*?)</h[23]>\s*$',blk,re.S)
            if h: blocks.append(('h',text(h.group(1)))); continue
            for part in re.split(r'(?:<br\s*/?>\s*){2,}|</?p[^>]*>',blk):
                t=text(part)
                if t and 'sign up for our' not in t.lower(): blocks.append(('p',t))
        else:
            inner=m.group(3)
            brand=re.search(r'class="brand-name">(.*?)</div>',inner,re.S)
            title=re.search(r'class="short-title">(.*?)</div>',inner,re.S)
            price=re.search(r'class="retail-price">(.*?)</span>',inner,re.S)
            sale=re.search(r'class="sale-price">(.*?)</span>',inner,re.S)
            name=' '.join(x for x in [text(brand.group(1)) if brand else '', text(title.group(1)) if title else ''] if x)
            pr=(text(sale.group(1)) if sale and text(sale.group(1)) else '') or (text(price.group(1)) if price else '')
            blocks.append(('i',{'name':name,'url':unwrap(m.group(2)),'desc':pr}))
    return blocks
