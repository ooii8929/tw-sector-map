# tw-sector-map

台股產業分類 × 題材標籤 × 產業鏈位置 JSON 資料集 | 2163 stocks × 34 sectors × 822 themes × 47 value chains

## 資料結構

所有資料在 `data/stocks.json`，每檔股票一個 object：

```json
{
  "code": "2330",
  "name": "台積電",
  "market": "TWSE",
  "sector": "半導體業",
  "themes": ["IC製造", "晶圓代工"],
  "tags": {
    "tech": ["CoWoS", "先進封裝", "晶圓代工"],
    "supply": ["NVIDIA供應鏈", "Apple供應鏈"]
  },
  "chain": [
    {
      "industry": "半導體",
      "stream": "中游",
      "segment": "IC/晶圓製造",
      "ic_code": "D000"
    }
  ]
}
```

### 四層標籤

| 層級 | 來源 | 說明 | 範例 |
|------|------|------|------|
| L1 `sector` | TWSE/TPEX/ESB 官方 | 34 大產業別 | 半導體業、光電業 |
| L2 `themes` | MoneyDJ | 800+ 題材分類 | 晶圓代工、MLCC |
| L3 `tags` | 人+AI | 產品線 + 供應鏈 | CoWoS、Apple供應鏈 |
| L4 `chain` | 櫃買中心產業價值鏈 | 47 產業 × 上中下游 × 312 子分類 | 半導體/中游/IC晶圓製造 |

### L4 Chain 欄位

來自[櫃買中心產業價值鏈資訊平台](https://ic.tpex.org.tw/)，自動爬取。

一家公司可能出現在多條產業鏈（array），例如台達電同時在半導體、自動化、電動車輛產業。

三種 stream 結構：
- **上中下游**（32 個傳統產業）：半導體、PCB、通信網路...
- **自定義分層**（5 個前瞻產業）：AI（應用與服務/核心技術/運算資源）、資安（資安產品/資安服務）...
- **子行業**（10 個 flat 產業）：stream = segment（如金融→金控業/銀行業/保險業）

## 檔案說明

```
data/
  stocks.json          ← 主資料，2163 檔股票全部欄位
  by-chain.json        ← 按產業鏈分組（47 產業 × 上中下游 × 子分類 → 公司列表）
  cross-industry.json  ← 跨產業關聯（371 對，≥3 家共同公司）
views/
  by-sector.md         ← 按 L1 產業別瀏覽
  by-chain.md          ← 按 L4 產業鏈瀏覽
scripts/
  build.py             ← 重建 views
```

## 如何使用

```python
import json

with open('data/stocks.json') as f:
    stocks = json.load(f)

# 找 CoWoS 概念股
cowos = [s for s in stocks if 'CoWoS' in s.get('tags',{}).get('tech',[])]

# 找半導體上游
semi_up = [s for s in stocks
           for c in s.get('chain',[])
           if c['industry'] == '半導體' and c['stream'] == '上游']

# 找跨 AI + 半導體的公司
ai_semi = [s for s in stocks
           if {c['industry'] for c in s.get('chain',[])} >= {'人工智慧', '半導體'}]
```

```bash
# jq 查詢
jq '[.[] | select(.chain[]?.industry == "半導體" and .chain[]?.stream == "上游")] | length' data/stocks.json

# 找特定產業鏈的所有公司
jq '.["半導體"]["上游"]' data/by-chain.json
```

## 資料來源

- [TWSE 證交所](https://isin.twse.com.tw/isin/C_public.jsp?strMode=2)
- [TPEX 櫃買中心](https://isin.twse.com.tw/isin/C_public.jsp?strMode=4)
- [ESB 興櫃](https://isin.twse.com.tw/isin/C_public.jsp?strMode=5)
- [MoneyDJ 題材分類](https://www.moneydj.com/Z/ZH/ZHA/ZHA.djhtm)
- [櫃買中心產業價值鏈資訊平台](https://ic.tpex.org.tw/) — L4 chain 欄位來源

## Changelog

- **v5** (2026-05-01) — 改為單一 JSON 結構，移除 2163 個 YAML 檔，新增 by-chain.json + cross-industry.json
- **v4** (2026-04-30) — 新增 L4 `chain` 欄位（櫃買中心產業價值鏈），47 產業 × 312 子分類 × 上中下游
- **v3** (2026-04-17) — 新增 211 檔興櫃股票（ESB），總數 1952 → 2163
- **v2** (2026-04-16) — 新增族群資金流向應用（Sector Flow），L3 enricher 覆蓋率 91.4%
- **v1** (2026-04-15) — 初版，1952 檔上市櫃股票，L1 + L2 + L3 三層標籤
