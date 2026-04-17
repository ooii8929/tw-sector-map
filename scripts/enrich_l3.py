#!/usr/bin/env python3
"""L3 Tag Enricher v3 — Google News RSS + 映射表，附時間戳"""
import yaml, glob, os, json, requests, time, re
import xml.etree.ElementTree as ET
from datetime import datetime

REPO = "/tmp/tw-sector-map-v2"
STOCKS = os.path.join(REPO, "stocks")
PROGRESS = os.path.join(REPO, "data", "enrich_progress.json")

PRIORITY = [
    "半導體業","電子零組件業","光電業","通信網路業","電腦及週邊設備業",
    "資訊服務業","電子通路業","電機機械","其他電子業",
    "生技醫療業","汽車工業","鋼鐵工業","化學工業",
]

TECH = {
    'CoWoS':'CoWoS','HBM':'HBM','2nm':'2nm','3nm':'3nm','5nm':'5nm',
    'DDR5':'DDR5','DDR4':'DDR4','PCIe':'PCIe','ABF載板':'ABF載板','BT載板':'BT載板',
    'IC載板':'IC載板','MLCC':'MLCC','Mini LED':'Mini LED','Micro LED':'Micro LED','OLED':'OLED',
    '矽光子':'矽光子','光通訊':'光通訊','CPO':'CPO','EUV':'EUV',
    '5G':'5G','WiFi':'WiFi','低軌衛星':'低軌衛星','毫米波':'毫米波',
    'AI伺服器':'AI伺服器','電動車':'EV','ADAS':'ADAS',
    'GaAs':'GaAs','GaN':'GaN','SiC':'SiC','InP':'InP',
    '先進封裝':'先進封裝','FOWLP':'FOWLP','PLP':'PLP','InFO':'InFO',
    '車用':'車用電子','伺服器':'伺服器','資料中心':'資料中心',
    '散熱':'散熱','液冷':'液冷散熱','均熱片':'均熱片','熱管':'熱管',
    'PCB':'PCB','HDI':'HDI','軟板':'FPC',
    '晶圓代工':'晶圓代工','IC設計':'IC設計','封測':'封測',
    'DRAM':'DRAM','NAND':'NAND Flash','記憶體':'記憶體',
    '被動元件':'被動元件','連接器':'連接器','電源供應器':'電源供應器',
    '面板':'面板','LED':'LED','光纖':'光纖','鏡頭':'光學鏡頭',
    '石英':'石英振盪器','振盪器':'石英振盪器',
    '太陽能':'太陽能','風電':'風電','儲能':'儲能',
    'CDMO':'CDMO','新藥':'新藥研發','PA':'PA功率放大器',
    '射頻':'射頻','RF':'射頻','砷化鎵':'GaAs',
    '800G':'800G','1.6T':'1.6T','400G':'400G',
    '電池':'電池','鋰電池':'鋰電池','TPU':'TPU','GPU':'GPU',
}

SUPPLY = {
    '蘋果':'Apple供應鏈','Apple':'Apple供應鏈','iPhone':'Apple供應鏈',
    '輝達':'NVIDIA供應鏈','NVIDIA':'NVIDIA供應鏈','GB200':'NVIDIA供應鏈','B200':'NVIDIA供應鏈',
    '特斯拉':'Tesla供應鏈','Tesla':'Tesla供應鏈',
    '高通':'高通供應鏈','AMD':'AMD供應鏈',
    '博通':'博通供應鏈','Broadcom':'博通供應鏈',
    'Intel':'Intel供應鏈','三星':'三星供應鏈',
    'Google':'Google供應鏈','微軟':'微軟供應鏈','Meta':'Meta供應鏈',
    'Lumentum':'Lumentum供應鏈','博通':'博通供應鏈','Broadcom':'博通供應鏈',
}

def load_progress():
    if os.path.exists(PROGRESS): return json.load(open(PROGRESS))
    return {"enriched": []}

def save_progress(prog):
    os.makedirs(os.path.dirname(PROGRESS), exist_ok=True)
    json.dump(prog, open(PROGRESS, "w"), ensure_ascii=False)

def extract_tags(text, name):
    tech = list(dict.fromkeys(v for k,v in TECH.items() if k in text))
    supply = list(dict.fromkeys(v for k,v in SUPPLY.items() if k in text and v.split('供應鏈')[0] not in name))
    return tech, supply

def cmnews(code, name):
    try:
        r = requests.get(f'https://cmnews.com.tw/tag/{name}({code})',
            headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if r.status_code != 200: return ''
        titles = re.findall(r'<a[^>]*href="/article/[^"]+"[^>]*>(.*?)</a>', r.text, re.DOTALL)
        return ' '.join(re.sub(r'<[^>]+>', '', t).strip() for t in titles[:15])
    except: return ''

def google_news(code, name):
    try:
        r = requests.get(f'https://news.google.com/rss/search?q={name}+{code}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant', timeout=5)
        if r.status_code != 200: return '', ''
        root = ET.fromstring(r.text)
        items = root.findall('.//item')
        text = ' '.join((i.find('title').text or '') for i in items[:20])
        pub = items[0].find('pubDate').text[:25] if items else ''
        return text, pub
    except: return '', ''

def run(n=30):
    prog = load_progress()
    done = set(prog["enriched"])
    candidates = []
    for f in sorted(glob.glob(os.path.join(STOCKS, "*.yml"))):
        d = yaml.safe_load(open(f))
        if d["code"] in done: continue
        pri = PRIORITY.index(d.get("sector","")) if d.get("sector","") in PRIORITY else 99
        candidates.append((pri, d["code"], d))
    candidates.sort()
    batch = candidates[:n]
    if not batch:
        print("✅ 全部已填充完畢")
        return

    updated = 0
    for _, code, stock in batch:
        name = stock["name"]
        # 1. Theme-based tags
        theme_text = ' '.join(stock.get("themes", []))
        t1, s1 = extract_tags(theme_text, name)
        # 2. CMoney news (best quality)
        cm_text = cmnews(code, name)
        t2, s2 = extract_tags(cm_text, name)
        # 3. Google News RSS (broad coverage)
        gn_text, last_pub = google_news(code, name)
        t3, s3 = extract_tags(gn_text, name)
        # Merge all (dedupe, preserve order: cmnews first)
        tech = list(dict.fromkeys(t2 + t3 + t1))
        supply = list(dict.fromkeys(s2 + s3 + s1))
        prog["enriched"].append(code)
        if not tech and not supply:
            continue
        stock["tags"] = {"tech": tech, "supply": supply}
        stock["last_enriched"] = datetime.utcnow().strftime("%Y-%m-%d")
        fpath = os.path.join(STOCKS, f"{code}.yml")
        with open(fpath, "w", encoding="utf-8") as f:
            yaml.dump(stock, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        updated += 1
        print(f"  {code} {name}: tech={tech[:5]}, supply={supply[:3]}")
        time.sleep(0.5)

    save_progress(prog)
    print(f"\n📊 {len(batch)} 檔處理, {updated} 檔更新, 累計 {len(prog['enriched'])}/1952")

if __name__ == "__main__":
    import sys
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
