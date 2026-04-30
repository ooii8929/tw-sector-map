# tw-sector-map

TWSE/TPEX sector & theme tag YAML dataset for Taiwan stocks

台股產業分類 × 題材標籤 × 產業鏈位置 YAML 資料集 | 2163 stocks × 34 sectors × 822 themes × 3200+ L3 tags × 47 value chains

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
tags:                         # L3 產業/產品標籤（人+AI 維護）
  tech:                       #   技術/產品線
    - CoWoS
    - 2nm
    - HBM
  supply:                     #   供應鏈歸屬
    - NVIDIA供應鏈
    - Apple供應鏈
chain:                        # L4 產業價值鏈位置（自動，櫃買中心）
  - industry: 半導體           #   47 產業之一
    stream: 中游               #   上游/中游/下游 或產業特定分層
    segment: IC/晶圓製造       #   子分類
    ic_code: D000              #   櫃買中心產業代碼
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

| 欄位 | 說明 | 範例 |
|------|------|------|
| `industry` | 47 個產業分類 | 半導體、印刷電路板、人工智慧 |
| `stream` | 產業鏈位置 | 上游/中游/下游（傳統產業）或自定義分層（如 AI: 應用與服務/核心技術/運算資源） |
| `segment` | 子分類 | IC設計、IC/晶圓製造、IC封裝測試 |
| `ic_code` | 櫃買中心產業代碼 | D000、L000、5300 |

一家公司可能出現在多條產業鏈（array），例如台達電同時在半導體、自動化、電動車輛產業。

三種 stream 結構：
- **上中下游**（32 個傳統產業）：半導體、PCB、通信網路...
- **自定義分層**（5 個前瞻產業）：AI（應用與服務/核心技術/運算資源）、資安（資安產品/資安服務）...
- **子行業**（10 個 flat 產業）：stream = segment（如金融→金控業/銀行業/保險業）


### 市場涵蓋

| 市場 | `market` | 檔數 | 說明 |
|------|----------|------|------|
| 上市 | `TWSE` | 1071 | 全部收錄 |
| 上櫃 | `TPEX` | 881 | 全部收錄 |
| 興櫃 | `ESB` | 211 | 日均量 > 50 張 |

### L3 Tag 規則

只放跟**產業/產品**相關的標籤，不放動能、事件、籌碼。

| 類別 | 定義 | 範例 |
|------|------|------|
| `tech` | 這家公司做什麼產品/技術 | CoWoS, PCIe 6.0, DDR5, ABF載板, 玻纖布 |
| `supply` | 屬於誰的供應鏈 | 台積電供應鏈, Apple供應鏈, NVIDIA供應鏈, 特斯拉供應鏈 |

## 檔案說明

```
stocks/          ← 主資料，直接編輯
  2330.yml
  2454.yml
  ...
views/           ← 自動生成，方便瀏覽
  by-sector.md
  by-tag.md
data/            ← 自動生成，程式用
  sectors.json
  sectors.csv
scripts/
  build.py       ← YAML → JSON/MD/CSV
  enrich_l3.py   ← 自動填充 L3 tags（CMoney + Google News）
```

## 如何貢獻

1. 找到股票：`stocks/2330.yml`
2. 在 `tags.tech` 或 `tags.supply` 加標籤
3. 發 PR，merge 後 GitHub Action 自動更新 views + data

## 如何使用（AI / 程式）

```python
import json

with open('data/sectors.json') as f:
    stocks = json.load(f)

# 找 CoWoS 概念股
cowos = [s for s in stocks if 'CoWoS' in s.get('tags',{}).get('tech',[])]

# 找 NVIDIA 供應鏈
nvidia = [s for s in stocks if 'NVIDIA供應鏈' in s.get('tags',{}).get('supply',[])]

# 找半導體業中有 HBM 技術的
hbm_semi = [s for s in stocks
            if s['sector'] == '半導體業'
            and 'HBM' in s.get('tags',{}).get('tech',[])]
```

## 更新指令

```bash
# 從 YAML 重建所有輸出
python scripts/build.py

# 自動填充 L3 tags（需要網路）
python scripts/enrich_l3.py 30
```

## 資料來源

- [TWSE 證交所](https://isin.twse.com.tw/isin/C_public.jsp?strMode=2)
- [TPEX 櫃買中心](https://isin.twse.com.tw/isin/C_public.jsp?strMode=4)
- [ESB 興櫃](https://isin.twse.com.tw/isin/C_public.jsp?strMode=5)
- [MoneyDJ 題材分類](https://www.moneydj.com/Z/ZH/ZHA/ZHA.djhtm)
- [櫃買中心產業價值鏈資訊平台](https://ic.tpex.org.tw/) — L4 chain 欄位來源，47 產業 × 312 子分類 × 上中下游位置

## 應用：族群資金流向（Sector Flow）

將三大法人每日買賣超按 L1/L2/L3 聚合，追蹤資金流向哪些產業、主題、技術標籤。

### 聚合方式

```
institutional（個股每日三大法人）
  JOIN sector_map_l1 → L1 資金流向（34 產業）
  JOIN sector_map_l2 → L2 資金流向（~820 主題）
  JOIN sector_map_l3 → L3 資金流向（~190 標籤）
```

### 各層級最佳用途

| 層級 | 選股篩選 | 情報觀察 | 說明 |
|------|----------|----------|------|
| L1 | 🏆 最佳 | 太粗 | 粒度剛好，訊號穩定，適合量化策略 |
| L2 | ❌ | 🏆 最佳 | 精確到子主題（晶圓代工 vs IC封裝），適合研究 |
| L3 | ❌ | ✅ 有用 | 技術/供應鏈趨勢（tech:MLCC, supply:Intel供應鏈）|

## Changelog

- **v4** (2026-04-30) — 新增 L4 `chain` 欄位（櫃買中心產業價值鏈），47 產業 × 312 子分類 × 上中下游，2106 檔股票加入產業鏈位置
- **v3** (2026-04-17) — 新增 211 檔興櫃股票（ESB，日均量 > 50 張），總數 1952 → 2163
- **v2** (2026-04-16) — 新增族群資金流向應用（Sector Flow），L3 enricher 覆蓋率 91.4%
- **v1** (2026-04-15) — 初版，1952 檔上市櫃股票，L1 + L2 + L3 三層標籤
