# 資料庫設計 (爭議仲裁功能)

## 1. ER 圖（實體關係圖）
```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string role "admin, landlord, tenant"
    }
    
    CONTRACTS {
        int id PK
        int landlord_id FK
        int tenant_id FK
        string property_address
    }
    
    DISPUTES {
        int id PK
        int contract_id FK
        int initiator_id FK
        string reason
        string status "pending, reviewing, resolved"
        string admin_decision
        int admin_id FK
        datetime created_at
        datetime resolved_at
    }
    
    DISPUTE_EVIDENCES {
        int id PK
        int dispute_id FK
        int uploader_id FK
        string photo_type "move_in, move_out"
        string file_url
        datetime uploaded_at
    }
    
    USERS ||--o{ CONTRACTS : "owns/rents"
    CONTRACTS ||--o{ DISPUTES : "has"
    USERS ||--o{ DISPUTES : "initiates/resolves"
    DISPUTES ||--o{ DISPUTE_EVIDENCES : "contains"
    USERS ||--o{ DISPUTE_EVIDENCES : "uploads"
# 資料庫設計 (DB DESIGN)

## 1. ER 圖（實體關係圖）

```mermaid
erDiagram
    USERS {
        INTEGER id PK
        TEXT username
        TEXT email
    }
    LEASES {
        INTEGER id PK
        INTEGER user_id FK
        TEXT address
        INTEGER monthly_rent
        TEXT start_date
        TEXT end_date
    }
    PAYMENTS {
        INTEGER id PK
        INTEGER user_id FK
        INTEGER lease_id FK
        INTEGER amount
        TEXT payment_date
        TEXT payment_method
        TEXT status
    }

    USERS ||--o{ LEASES : "has"
    USERS ||--o{ PAYMENTS : "makes"
    LEASES ||--o{ PAYMENTS : "receives"
```

## 2. 資料表詳細說明

### USERS
系統使用者表，包含房東、房客與管理員。
- `id`: INTEGER, Primary Key
- `username`: TEXT, 必填, 使用者名稱
- `role`: TEXT, 必填, 角色 (admin, landlord, tenant)

### CONTRACTS
租賃合約表，紀錄房東與房客的租賃關係。
- `id`: INTEGER, Primary Key
- `landlord_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `tenant_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `property_address`: TEXT, 必填, 租屋地址

### DISPUTES
爭議案件表，記錄每次的仲裁請求。
- `id`: INTEGER, Primary Key
- `contract_id`: INTEGER, 必填, Foreign Key (CONTRACTS.id)
- `initiator_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `reason`: TEXT, 必填, 爭議原因與說明
- `status`: TEXT, 必填, 狀態 (pending, reviewing, resolved)
- `admin_decision`: TEXT, 管理員的裁決結果說明
- `admin_id`: INTEGER, Foreign Key (USERS.id)
- `created_at`: DATETIME, 必填, 發起時間
- `resolved_at`: DATETIME, 裁決時間

### DISPUTE_EVIDENCES
爭議證據表，記錄雙方上傳的照片。
- `id`: INTEGER, Primary Key
- `dispute_id`: INTEGER, 必填, Foreign Key (DISPUTES.id)
- `uploader_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `photo_type`: TEXT, 必填, 照片類型 (move_in, move_out)
- `file_url`: TEXT, 必填, 圖片存放路徑
- `uploaded_at`: DATETIME, 必填, 上傳時間
### `users` (使用者 / 租客)
儲存租客的基本資訊。
- `id` (INTEGER): Primary Key, 自動遞增。
- `username` (TEXT): 租客姓名，必填。
- `email` (TEXT): 聯絡信箱，必填且唯一。

### `leases` (租約)
儲存租約資訊與每月應繳金額。
- `id` (INTEGER): Primary Key, 自動遞增。
- `user_id` (INTEGER): Foreign Key，關聯至 `users.id`，代表承租人。
- `address` (TEXT): 租屋處地址，必填。
- `monthly_rent` (INTEGER): 每月應繳租金，必填。
- `start_date` (TEXT): 租約起始日 (ISO 格式 YYYY-MM-DD)。
- `end_date` (TEXT): 租約結束日 (ISO 格式 YYYY-MM-DD)。

### `payments` (繳費紀錄)
紀錄每一筆線上繳費交易，防詐騙平台的核心紀錄。
- `id` (INTEGER): Primary Key, 自動遞增。
- `user_id` (INTEGER): Foreign Key，關聯至 `users.id`。
- `lease_id` (INTEGER): Foreign Key，關聯至 `leases.id`。
- `amount` (INTEGER): 實際繳款金額。
- `payment_date` (TEXT): 繳費完成時間 (ISO 格式 YYYY-MM-DD HH:MM:SS)。
- `payment_method` (TEXT): 繳費方式，如 "Credit Card"。
- `status` (TEXT): 交易狀態，如 "Completed", "Failed"。
