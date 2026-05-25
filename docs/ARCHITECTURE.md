# 系統架構設計 (爭議仲裁功能)

## 1. 技術架構說明
- **後端**：Python + Flask (輕量級，適合快速開發)
- **模板引擎**：Jinja2 (與 Flask 原生整合好，直接在後端渲染 HTML 頁面)
- **資料庫**：SQLite (內建於 Python，不需額外架設伺服器，適合 MVP)
- **ORM**：SQLAlchemy (方便操作關聯式資料庫，程式碼更易維護)
- **架構模式**：MVC (Model-View-Controller)
  - **Model**: `models/` - 負責定義資料庫綱要與資料存取邏輯 (如 Dispute, DisputeEvidence 等)。
  - **View**: `templates/` - 負責呈現 HTML 給使用者，使用 Jinja2 語法動態載入資料。
  - **Controller**: `routes/` (或直接寫在 `app.py`) - 接收 HTTP 請求，調用 Model 取得資料，再傳遞給 View 進行渲染。

## 2. 專案資料夾結構
```text
app/
  models/
    __init__.py
    dispute.py         ← 定義 Dispute, DisputeEvidence 等資料表模型
  routes/
    __init__.py
    dispute.py         ← 處理發起爭議、上傳照片、管理員裁決的 API 與頁面路由
  templates/
    disputes/
      create.html      ← 房東/房客發起爭議的頁面
      upload.html      ← 上傳照片的頁面
      admin_list.html  ← 管理員檢視爭議列表
      admin_detail.html← 管理員檢視單一爭議(含雙方照片對比)與送出裁決
      result.html      ← 房東/房客查看裁決結果
  static/
    css/style.css      ← 頁面樣式
    uploads/           ← 存放使用者上傳的照片 (入住/退租照片)
instance/
  database.db          ← SQLite 資料庫檔案
app.py                 ← 程式進入點，初始化 Flask 與註冊路由
```

## 3. 元件關係圖
```mermaid
flowchart LR
    Browser[使用者瀏覽器] -->|HTTP 請求| Route[Flask Route (Controller)]
    Route -->|讀寫資料| Model[SQLAlchemy (Model)]
    Model -->|SQL 查詢| DB[(SQLite 資料庫)]
    DB -->|返回資料| Model
    Model -->|返回資料物件| Route
    Route -->|傳遞資料| Template[Jinja2 Template (View)]
    Template -->|渲染 HTML| Route
    Route -->|HTTP 回應| Browser
```

## 4. 關鍵設計決策
1. **本地端儲存照片 (static/uploads)**：
   - 考量 MVP 開發速度與成本，先將照片直接存放在伺服器的靜態資料夾中，資料庫僅記錄檔案路徑 (URL)。未來若需擴展可改為雲端空間 (如 AWS S3)。
2. **使用 Jinja2 而非前端框架**：
   - 本專案不需要前後端分離，使用 Jinja2 可以最快地完成伺服器端渲染 (SSR)，簡化開發流程與跨源請求問題。
3. **單一資料庫檔案 (SQLite)**：
   - 租屋網站的 MVP 階段資料量與併發不高，SQLite 具備免安裝設定的優勢，可加快開發與測試。
# 系統架構設計 (ARCHITECTURE)

## 1. 技術架構說明

本專案採用經典的 MVC（Model-View-Controller）架構模式進行開發，確保程式碼結構清晰、易於維護。

- **後端框架：Python + Flask (Controller)**
  - Flask 負責接收瀏覽器傳來的 HTTP 請求（如 GET 頁面、POST 繳費資料），驗證邏輯後，呼叫對應的 Model 進行資料庫操作，最後將結果交給 View 渲染。
- **視圖引擎：Jinja2 (View)**
  - 負責將後端傳來的動態資料與 HTML 結合，產生最終的網頁呈現給使用者。不需要前後端分離架構，以降低初期開發複雜度。
- **資料庫：SQLite (Model)**
  - 輕量級關聯式資料庫，資料直接存放在本地檔案 `instance/database.db` 中。我們將透過 Python 內建的 `sqlite3` 模組或輕量級封裝來進行操作。
- **前端樣式：Vanilla CSS & JS**
  - 使用純 CSS 與 JavaScript 實作現代化、響應式（RWD）的介面設計，並加入防詐騙網站特有的安全提示與互動。

## 2. 專案資料夾結構

```text
teamwork-AI-agent/
│
├── app/
│   ├── models/            ← 資料庫模型 (處理與 SQLite 的互動)
│   │   ├── user.py
│   │   ├── lease.py
│   │   └── payment.py
│   ├── routes/            ← Flask 路由 (Controller，處理請求與邏輯)
│   │   └── payment_routes.py
│   ├── templates/         ← Jinja2 HTML 模板 (View)
│   │   ├── base.html
│   │   ├── payment_form.html
│   │   └── payment_history.html
│   └── static/            ← CSS / JS / 圖片 等靜態資源
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
│
├── database/
│   └── schema.sql         ← SQLite 建表語法
│
├── instance/
│   └── database.db        ← SQLite 資料庫檔案 (執行後產生)
│
├── docs/                  ← 專案文件 (PRD, 架構, 流程圖等)
│
└── app.py                 ← 專案進入點 (啟動 Flask Server)
```

## 3. 元件關係圖

以下是系統運作的基礎流程圖，展示從瀏覽器到資料庫的互動方式：

```mermaid
flowchart LR
    Browser([使用者瀏覽器])
    
    subgraph "Flask 應用程式"
        Router[Flask Route\n(Controller)]
        Jinja[Jinja2 Template\n(View)]
        Model[Python Model\n(資料邏輯)]
    end
    
    DB[(SQLite 資料庫)]

    Browser -- "1. 發送請求\n(GET / POST)" --> Router
    Router -- "2. 查詢/寫入資料" --> Model
    Model -- "3. 執行 SQL" --> DB
    DB -- "4. 回傳資料" --> Model
    Model -- "5. 傳遞結果" --> Router
    Router -- "6. 傳遞資料並渲染" --> Jinja
    Jinja -- "7. 回傳 HTML" --> Browser
```

## 4. 關鍵設計決策

1. **不採用完整 ORM (如 SQLAlchemy)**：
   - 為了保持極度輕量與直觀，且功能範圍明確（單純的繳租與查詢），我們採用直接撰寫 SQL 語法結合 Python `sqlite3` 的方式，這樣能更直接掌控資料庫操作並清楚展示 SQL 結構。
2. **啟動時自動注入 Mock Data**：
   - 作為展示與測試用的 MVP，當 Flask 啟動時會檢查資料庫，若無資料則自動產生「測試用的租客與租約資料」，讓測試者一進站就能直接體驗繳款流程，無需繁瑣的註冊步驟。
3. **前端防詐安全設計**：
   - 在 `payment_form.html` 中，將採用高對比度的安全提示 UI，並在表單送出前使用 Vanilla JS 攔截並跳出最終確認 Modal，模擬真實防詐騙系統的保護機制。
