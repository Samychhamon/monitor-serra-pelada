# Coleta notícias sobre o projeto Serra Pelada (Tec Tônicas, Coomigasp, SPCDM, Colossus, Helius) no Google Notícias e grava data/noticias.json.
import json, re, html, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

BUSCAS = [
    'Coomigasp',
    '"Tec Tônicas" OR "Tectônicas Mineração" OR "Tectonicas Mineracao"',
    '"Serra Pelada" (Helius OR Colossus OR SPCDM)',
    '"Serra Pelada" (garimpo OR garimpeiros OR ANM OR SEMAS OR justiça OR decisão OR licença OR mineração OR ouro)',
]
EXIGE = re.compile(r'serra pelada|coomigasp|tect[oô]nicas|tec t[oô]nicas|helius|colossus|spcdm', re.I)
EXCLUIR = re.compile(r'\b(filme|novela|elenco|bilheteria|netflix|globoplay|série|cinema)\b', re.I)
SAIDA = 'data/noticias.json'

def buscar(q):
    url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q + ' when:60d', 'hl': 'pt-BR', 'gl': 'BR', 'ceid': 'BR:pt-419'})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (monitor-serra-pelada)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    itens = []
    for it in root.iter('item'):
        titulo = html.unescape(it.findtext('title') or '').strip()
        fonte = (it.findtext('source') or '').strip()
        if fonte and titulo.endswith(' - ' + fonte):
            titulo = titulo[: -len(' - ' + fonte)]
        try:
            dt = parsedate_to_datetime(it.findtext('pubDate')).astimezone(timezone.utc)
        except Exception:
            continue
        link = (it.findtext('link') or '').strip()
        if link.startswith('https://'):
            itens.append({'titulo': titulo, 'fonte': fonte, 'data': dt.isoformat(), 'url': link})
    return itens

def main():
    try:
        antigos = json.load(open(SAIDA, encoding='utf-8')).get('itens', [])
    except Exception:
        antigos = []
    vistos, todos, novos = set(), [], []
    for q in BUSCAS:
        try:
            todos += buscar(q)
        except Exception as e:
            print('falha na busca', q, e)
    for i in todos + antigos:
        if not EXIGE.search(i['titulo']) or EXCLUIR.search(i['titulo']):
            continue
        chave = re.sub(r'\W+', '', i['titulo'].lower())[:80]
        if chave in vistos:
            continue
        vistos.add(chave)
        novos.append(i)
    novos.sort(key=lambda x: x['data'], reverse=True)
    out = {'verificado': datetime.now(timezone.utc).isoformat(), 'itens': novos[:40]}
    json.dump(out, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(out['itens']), 'notícias')

if __name__ == '__main__':
    main()
