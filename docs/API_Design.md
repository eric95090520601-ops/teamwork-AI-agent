# API 路由與頁面設計 (爭議仲裁功能)

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| 發起爭議頁面 | GET | `/disputes/create/<contract_id>` | `disputes/create.html` | 顯示填寫爭議原因的表單 |
| 送出爭議請求 | POST | `/disputes/create/<contract_id>` | — | 接收表單並建立 Dispute，重導向到上傳照片頁 |
| 上傳照片頁面 | GET | `/disputes/<dispute_id>/upload` | `disputes/upload.html` | 顯示上傳照片(入住/退租)介面 |
| 處理照片上傳 | POST | `/disputes/<dispute_id>/upload` | — | 儲存檔案並寫入 DisputeEvidence，重導向到詳情頁 |
| 爭議案件詳情(用戶) | GET | `/disputes/<dispute_id>` | `disputes/result.html` | 房東/房客查看自己發起的爭議與裁決結果 |
| 爭議清單(管理員) | GET | `/admin/disputes` | `disputes/admin_list.html` | 列出所有待處理與已裁決的案件 |
| 案件審核(管理員) | GET | `/admin/disputes/<dispute_id>` | `disputes/admin_detail.html` | 管理員檢視雙方上傳的照片並顯示裁決表單 |
| 送出裁決(管理員) | POST | `/admin/disputes/<dispute_id>/decide` | — | 接收管理員裁決結果，更新 Dispute，重導向回列表 |

## 2. 每個路由的詳細說明

### `GET/POST /disputes/create/<contract_id>`
- **輸入**: `contract_id` (URL 參數), `reason` (表單)
- **處理邏輯**: 驗證合約存在且使用者為當事人。POST 時建立 Dispute 物件，設定 initiator_id。
- **輸出**: GET 渲染 `disputes/create.html`，POST 重導向至 `/disputes/<id>/upload`。
- **錯誤處理**: 若非合約當事人返回 403。

### `GET/POST /disputes/<dispute_id>/upload`
- **輸入**: `dispute_id` (URL 參數), `photo` (檔案), `photo_type` (表單: move_in/move_out)
- **處理邏輯**: 驗證使用者為當事人，將照片存入 `static/uploads/`，建立 DisputeEvidence。
- **輸出**: GET 渲染 `disputes/upload.html`，POST 重導向至 `/disputes/<id>`。

### `GET /disputes/<dispute_id>`
- **輸入**: `dispute_id`
- **處理邏輯**: 取得 Dispute 及其 Evidences 供當事人查看。
- **輸出**: 渲染 `disputes/result.html`。

### `GET /admin/disputes`
- **處理邏輯**: 取得所有 Dispute (可依 status 過濾)。
- **輸出**: 渲染 `disputes/admin_list.html`。

### `GET /admin/disputes/<dispute_id>`
- **處理邏輯**: 取得該 Dispute 與雙方的 DisputeEvidence。
- **輸出**: 渲染 `disputes/admin_detail.html`。

### `POST /admin/disputes/<dispute_id>/decide`
- **輸入**: `admin_decision` (表單)
- **處理邏輯**: 更新 Dispute 狀態為 resolved，寫入裁決說明與管理員 ID。
- **輸出**: 重導向至 `/admin/disputes`。

## 3. Jinja2 模板清單
- `base.html`: 網站共用版型 (假設已存在)。
- `disputes/create.html`: 發起爭議表單。
- `disputes/upload.html`: 照片上傳與預覽介面。
- `disputes/result.html`: 爭議案件處理進度與結果。
- `disputes/admin_list.html`: 管理員後台的爭議案件列表。
- `disputes/admin_detail.html`: 管理員審核頁面，包含左右對比入住與退租照片的排版。
