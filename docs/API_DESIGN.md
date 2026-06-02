# API 與路由設計 (API DESIGN)

本文件描述 Flask 應用程式的路由結構。本專案採伺服器端渲染 (Server-Side Rendering)，因此路由主要回傳 Jinja2 渲染後的 HTML，部分處理表單提交的 POST 請求則回傳重導向 (Redirect) 指令。

## 1. 路由列表

| 路徑 (URL) | 方法 (Method) | Controller 邏輯 | 對應的 View (Jinja2) | 說明 |
| --- | --- | --- | --- | --- |
| `/` | GET | `index()` | `index.html` | 首頁與儀表板。載入目前租客的租約與應繳金額資訊，提供「立即繳費」按鈕。 |
| `/payments/new` | GET | `payment_page()` | `payment_form.html` | 線上繳款表單頁面，讓使用者輸入信用卡號碼等資訊。 |
| `/payments/new` | POST | `process_payment()` | (無，重新導向) | 接收表單資料，寫入 `payments` 資料表。成功後重導向至 `/payments/history`。 |
| `/payments/history`| GET | `payment_history()` | `payment_history.html`| 讀取該租客過去的所有繳費紀錄並列表呈現。 |

## 2. 請求與回應詳細說明

### `GET /`
- **目的**：提供繳費入口。
- **前置動作**：假設以 Mock User (ID=1) 登入。取得 `leases` 資訊。
- **傳遞給模板的資料**：
  - `user`: 目前使用者物件
  - `lease`: 目前租約物件 (包含 `monthly_rent`)

### `GET /payments/new`
- **目的**：顯示付款表單。
- **前端驗證**：HTML5 必填驗證，以及 JS 阻擋表單送出直到確認「防詐騙提示」。

### `POST /payments/new`
- **目的**：處理付款邏輯。
- **接收參數 (Form Data)**：
  - `card_number` (雖然不會真存，但在真實情境中會送到第三方金流)
  - `amount` (繳費金額)
  - 隱藏欄位：`lease_id`
- **處理邏輯**：
  1. 取得當下時間 `payment_date`
  2. 狀態設為 "Completed" (因模擬付款直接成功)
  3. 呼叫 `PaymentModel.create_payment()`
- **回應**：`redirect('/payments/history')`

### `GET /payments/history`
- **目的**：提供歷史帳單查詢，供對帳防詐。
- **傳遞給模板的資料**：
  - `payments`: 陣列，包含所有繳費紀錄的字典。
