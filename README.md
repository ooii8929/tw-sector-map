# tw-sector-map

台股產業 × 個股對照表 | 1900+ stocks × 34 sectors × 800+ themes

> 給 AI 讀的台股知識圖譜 — 人維護，AI 消費

## 資料結構

每檔股票一個 YAML 檔（`stocks/2330.yml`）：

```yaml
code: "2330"
name: 台積電
market: TWSE
sector: 半導體業              # L1 官方分類（自動）
themes:                       # L2 MoneyDJ 題材（自動）
  - 晶圓代工
  - IC製造
tags:                         # L3 標籤（人+AI 共同維護）
  tech:                       #   技術/產品線（穩定）
    - CoWoS
    - 2nm
  supply:                     #   供應鏈角色（穩定）
    - NVIDIA供應鏈
  catalyst:                   #   事件催化劑（時效性）
    - 熊本廠量產
  momentum:                   #   動能標記（AI自動，短期）
    - 外資連買
```

### 三層標籤

| 層級 | 來源 | 時效 | 範例 |
|------|------|------|------|
| L1 `sector` | TWSE/TPEX 官方 | 穩定 | 半導體業、光電業 |
| L2 `themes` | MoneyDJ | 穩定 | 晶圓代工、MLCC |
| L3 `tags` | 人+AI | 分類見下 | CoWoS、Apple供應鏈 |

### L3 Tag 分類

| 類別 | 誰維護 | 時效 | 範例 |
|------|--------|------|------|
| `tech` | 人為主 | 穩定 | CoWoS, PCIe 6.0, DDR5 |
| `supply` | 人+AI | 穩定 | Apple供應鏈, 特斯拉供應鏈 |
| `catalyst` | AI為主 | 會過期 | 降息受惠, 庫存回補 |
| `momentum` | AI自動 | 短期 | 外資連買, 突破年線 |

## 檔案說明

```
stocks/          ← 主資料，直接編輯
  2330.yml
  2454.yml
  ...
views/           ← 自動生成，方便瀏覽
  by-sector.md   ← 按產業分組
  by-tag.md      ← 按 L3 tag 分組
data/            ← 自動生成，程式用
  sectors.json
  sectors.csv
scripts/
  build.py       ← YAML → JSON/MD/CSV
```

## 如何貢獻

1. 找到股票檔案：`stocks/2330.yml`
2. 在 `tags` 下對應類別加標籤
3. 發 PR，merge 後自動更新 views + data

## 如何使用（AI / 程式）

```python
import json

with open('data/sectors.json') as f:
    stocks = json.load(f)

# 找 CoWoS 概念股
cowos = [s for s in stocks if 'CoWoS' in s.get('tags',{}).get('tech',[])]

# 找同時有 AI算力 tech tag + 外資連買 momentum 的股票
hits = [s for s in stocks
        if 'AI算力' in s.get('tags',{}).get('tech',[])
        and '外資連買' in s.get('tags',{}).get('momentum',[])]
```

## 資料來源

- [TWSE 證交所](https://isin.twse.com.tw/isin/C_public.jsp?strMode=2)
- [TPEX 櫃買中心](https://isin.twse.com.tw/isin/C_public.jsp?strMode=4)
- [MoneyDJ 題材分類](https://www.moneydj.com/Z/ZH/ZHA/ZHA.djhtm)
