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
