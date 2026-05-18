# 流程圖設計 (爭議仲裁功能)

## 1. 使用者流程圖（User Flow）
```mermaid
flowchart LR
    Start([進入網站]) --> Login{身分登入}
    
    Login -->|房東/房客| UserHome[訂單/合約詳情頁]
    UserHome --> UserAction{選擇操作}
    UserAction -->|發起爭議| InitDispute[填寫爭議原因]
    InitDispute --> UploadPhotos[上傳點交與退租照片]
    UploadPhotos --> WaitArbitration[等待管理員裁決]
    WaitArbitration --> ViewResult[查看裁決結果]
    
    Login -->|平台管理員| AdminHome[爭議案件列表頁]
    AdminHome --> AdminAction{選擇操作}
    AdminAction -->|查看案件| ViewDetail[檢視爭議詳情與雙方照片對比]
    ViewDetail --> MakeDecision[填寫裁決結果與說明]
    MakeDecision --> NotifyUsers[送出並通知雙方]
```

## 2. 系統序列圖（Sequence Diagram）
以「管理員送出裁決結果」為例的完整流程：
```mermaid
sequenceDiagram
    actor Admin as 平台管理員
    participant Browser as 管理員瀏覽器
    participant Flask as Flask (Route)
    participant DB as SQLite (Model)
    
    Admin->>Browser: 填寫裁決結果並點擊送出
    Browser->>Flask: POST /admin/disputes/{id}/decide
    Flask->>DB: 查詢 Dispute(id)
    DB-->>Flask: 回傳 Dispute 物件
    Flask->>DB: 更新 status 為 'resolved', 寫入裁決說明
    DB-->>Flask: 更新成功
    Flask-->>Browser: HTTP 302 重導向到案件列表
    Browser->>Admin: 顯示裁決已完成提示
```

## 3. 功能清單對照表

| 功能名稱 | 對應 URL 路徑 | HTTP 方法 | 說明 |
| --- | --- | --- | --- |
| 建立爭議 | `/disputes/create` | GET / POST | 房東/房客填寫表單發起爭議 |
| 上傳照片 | `/disputes/<id>/upload` | GET / POST | 雙方上傳入住與退租照片 |
| 查看案件詳情(用戶) | `/disputes/<id>` | GET | 雙方查看爭議狀態與結果 |
| 爭議案件列表(管理員) | `/admin/disputes` | GET | 管理員查看所有待處理案件 |
| 查看案件與對比照片(管理員) | `/admin/disputes/<id>` | GET | 管理員檢視雙方證據照片 |
| 送出裁決結果(管理員) | `/admin/disputes/<id>/decide` | POST | 管理員送出裁決與說明 |
