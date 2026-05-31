# Claude Session 魚骨圖

把你在 Claude Code 裡做過的所有對話，用**魚骨圖（石川圖）**的方式視覺化呈現。

---

## 這是什麼

Claude Code 每次對話都會在 `~/.claude/projects/` 留下 `.jsonl` 紀錄檔。
時間一久，你根本不記得在哪個專案做過什麼。

這個工具會：

1. 掃描 `~/.claude/projects/` 底下所有專案
2. 依關鍵字自動分類（Java、Python、GitHub、Claude 設定 …）
3. 把「分類 → 專案 → session」的樹狀關係畫成互動式魚骨圖
4. 每個 session 圓點 hover 可以看到那次對話的前幾句摘要

---

## 畫面長這樣

```
                        ┌──────────┐
  Java / Spring Boot ─── ProjectA ── ● 2024-01-10
                    \              └─ ● 2024-01-15
  Python ────────────── ProjectB ── ● 2024-02-03  ──────► 你 (Ian)
                    \              └─ ● 2024-02-08
  GitHub ─────────────── ProjectC ── ● 2024-03-01
```

右側有概覽面板，列出所有分類、專案數和 session 數，點擊可以跳轉到對應位置。

---

## 功能

| 操作 | 說明 |
|------|------|
| 滾輪 | 縮放 |
| 左鍵拖曳 | 平移 |
| 移到 ● | 顯示該 session 的對話摘要 |
| 右鍵 ProjectCard | 重命名 / 刪除專案節點 |
| `⟳ 重新載入` | 重新掃描 `~/.claude/projects/` |
| `⊞ 全圖` | 縮放回完整視圖 |
| `▶ 概覽` | 切換右側分類面板（Ctrl+B）|
| `Ctrl+R` | 重新載入 |
| `F` | 全圖 |
| `Ctrl + =` / `Ctrl + -` | 放大 / 縮小 |

---

## 安裝與執行

**需求**：Python 3.10 以上

```bash
# 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 安裝相依套件
pip install PySide6

# 執行
python main.py
```

---

## 專案結構

```
PythonProject/
├── main.py                  # 入口點
├── session_parser.py        # 讀取與分類 Claude session 資料
├── session_fishbone.py      # 向下相容的舊入口（轉發到 main.py）
└── fishbone/
    ├── window.py            # 主視窗
    ├── scene.py             # QGraphicsScene，組裝魚骨圖
    ├── view.py              # 可縮放平移的 QGraphicsView
    ├── sidebar.py           # 右側分類概覽面板
    ├── project_card.py      # 專案節點（含右鍵選單）
    ├── session_dot.py       # Session 圓點（含 hover 動畫）
    ├── tooltip.py           # Hover 時的摘要卡片
    ├── loader.py            # 背景載入執行緒
    ├── theme.py             # 顏色與樣式常數
    └── utils.py             # 發光效果、淡入動畫工具
```

---

## 分類邏輯

`session_parser.py` 裡的 `CATEGORY_KEYWORDS` 定義了關鍵字對應的分類。
程式會把專案目錄名稱和 session 前幾行內容拼在一起做關鍵字比對，取分數最高的分類。

想加新分類或修改關鍵字，直接編輯 `CATEGORY_KEYWORDS` 即可。

---

## 資料來源

只讀取，不寫入，不修改任何 Claude 資料。

```
~/.claude/projects/
  └── C--Users-ian-PycharmProjects-MyApp/
        ├── abc123.jsonl
        └── def456.jsonl
```

每個 `.jsonl` 是一次 Claude Code 對話的完整紀錄。
程式只讀取每個檔案的前 80 KB（取前幾條 user 訊息作為摘要），不會全量載入。
