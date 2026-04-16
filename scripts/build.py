"""build.py — Aggregate stocks/*.yml → views + data outputs"""
import os, json, csv, yaml
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCKS_DIR = os.path.join(ROOT, 'stocks')
DATA_DIR = os.path.join(ROOT, 'data')
VIEWS_DIR = os.path.join(ROOT, 'views')

def load_all():
    stocks = []
    for f in sorted(os.listdir(STOCKS_DIR)):
        if not f.endswith('.yml'): continue
        with open(os.path.join(STOCKS_DIR, f), encoding='utf-8') as fh:
            stocks.append(yaml.safe_load(fh))
    return stocks

def write_json(stocks):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, 'sectors.json'), 'w', encoding='utf-8') as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

def write_csv(stocks):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, 'sectors.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['代碼','名稱','產業','市場','題材(L2)','tech','supply','catalyst','momentum'])
        for s in stocks:
            tags = s.get('tags', {})
            w.writerow([s['code'], s['name'], s['sector'], s['market'],
                        ', '.join(s.get('themes',[])),
                        ', '.join(tags.get('tech',[])),
                        ', '.join(tags.get('supply',[])),
                        ', '.join(tags.get('catalyst',[])),
                        ', '.join(tags.get('momentum',[]))])

def write_by_sector(stocks):
    os.makedirs(VIEWS_DIR, exist_ok=True)
    sectors = defaultdict(list)
    for s in stocks: sectors[s['sector']].append(s)
    lines = ['# 按產業分組', '']
    for sec, lst in sorted(sectors.items(), key=lambda x: -len(x[1])):
        lines.append(f'## {sec}（{len(lst)} 檔）\n')
        lines.append('| 代碼 | 名稱 | 市場 | L2 題材 | L3 Tags |')
        lines.append('|------|------|------|---------|---------|')
        for s in sorted(lst, key=lambda x: x['code']):
            themes = ', '.join(s.get('themes',[])[:3])
            all_tags = []
            for cat in ('tech','supply','catalyst','momentum'):
                all_tags.extend(s.get('tags',{}).get(cat,[]))
            tags_str = ', '.join(all_tags[:5]) or '—'
            lines.append(f'| {s["code"]} | {s["name"]} | {s["market"]} | {themes} | {tags_str} |')
        lines.append('')
    with open(os.path.join(VIEWS_DIR, 'by-sector.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def write_by_tag(stocks):
    os.makedirs(VIEWS_DIR, exist_ok=True)
    tag_map = defaultdict(list)
    for s in stocks:
        for cat in ('tech','supply','catalyst','momentum'):
            for t in s.get('tags',{}).get(cat,[]):
                tag_map[f'{cat}/{t}'].append(s)
    if not tag_map:
        with open(os.path.join(VIEWS_DIR, 'by-tag.md'), 'w', encoding='utf-8') as f:
            f.write('# 按 L3 Tag 分組\n\n> 尚無 L3 tags，等待貢獻！\n')
        return
    lines = ['# 按 L3 Tag 分組', '']
    for tag, lst in sorted(tag_map.items()):
        cat, name = tag.split('/', 1)
        lines.append(f'### [{cat}] {name}（{len(lst)} 檔）')
        for s in sorted(lst, key=lambda x: x['code']):
            lines.append(f'- {s["code"]} {s["name"]}')
        lines.append('')
    with open(os.path.join(VIEWS_DIR, 'by-tag.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    stocks = load_all()
    write_json(stocks)
    write_csv(stocks)
    write_by_sector(stocks)
    write_by_tag(stocks)
    tags_count = sum(len(t) for s in stocks for t in s.get('tags',{}).values())
    print(f'✅ {len(stocks)} stocks, {tags_count} L3 tags → JSON + CSV + views')
