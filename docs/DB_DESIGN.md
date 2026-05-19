# 資料庫設計 (爭議仲裁與報修溝通中心)

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
    
    REPAIRS {
        int id PK
        int contract_id FK
        int initiator_id FK
        string item_name
        string description
        string status "pending, reviewing, resolved"
        datetime created_at
        datetime updated_at
    }
    
    REPAIR_EVIDENCES {
        int id PK
        int repair_id FK
        int uploader_id FK
        string evidence_type "original, broken"
        string file_url
        datetime uploaded_at
    }

    MESSAGES {
        int id PK
        int repair_id FK
        int sender_id FK
        string content
        datetime created_at
    }
    
    USERS ||--o{ CONTRACTS : "owns/rents"
    CONTRACTS ||--o{ DISPUTES : "has"
    USERS ||--o{ DISPUTES : "initiates/resolves"
    DISPUTES ||--o{ DISPUTE_EVIDENCES : "contains"
    USERS ||--o{ DISPUTE_EVIDENCES : "uploads"
    
    CONTRACTS ||--o{ REPAIRS : "has"
    USERS ||--o{ REPAIRS : "initiates"
    REPAIRS ||--o{ REPAIR_EVIDENCES : "contains"
    USERS ||--o{ REPAIR_EVIDENCES : "uploads"
    REPAIRS ||--o{ MESSAGES : "contains"
    USERS ||--o{ MESSAGES : "sends"
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

### REPAIRS
報修單表，記錄房東與房客間的物品報修請求。
- `id`: INTEGER, Primary Key
- `contract_id`: INTEGER, 必填, Foreign Key (CONTRACTS.id)
- `initiator_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `item_name`: TEXT, 必填, 損壞物品名稱
- `description`: TEXT, 報修詳細說明
- `status`: TEXT, 必填, 狀態 (pending, reviewing, resolved)
- `created_at`: DATETIME, 必填, 發起時間
- `updated_at`: DATETIME, 最後更新時間

### REPAIR_EVIDENCES
報修證據表，記錄物品的原本狀態與損壞狀態。
- `id`: INTEGER, Primary Key
- `repair_id`: INTEGER, 必填, Foreign Key (REPAIRS.id)
- `uploader_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `evidence_type`: TEXT, 必填, 證據類型 (original, broken)
- `file_url`: TEXT, 必填, 檔案存放路徑(照片或影片)
- `uploaded_at`: DATETIME, 必填, 上傳時間

### MESSAGES
報修留言板，記錄雙方的溝通內容作為證據。
- `id`: INTEGER, Primary Key
- `repair_id`: INTEGER, 必填, Foreign Key (REPAIRS.id)
- `sender_id`: INTEGER, 必填, Foreign Key (USERS.id)
- `content`: TEXT, 必填, 留言內容
- `created_at`: DATETIME, 必填, 留言時間
