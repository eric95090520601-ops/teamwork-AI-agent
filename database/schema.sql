CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'tenant'
);

CREATE TABLE IF NOT EXISTS leases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    address TEXT NOT NULL,
    monthly_rent INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lease_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(lease_id) REFERENCES leases(id)
);

-- ===== 合約違法條款自檢紀錄 =====
CREATE TABLE IF NOT EXISTS contract_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    contract_text TEXT NOT NULL,
    total_issues INTEGER NOT NULL DEFAULT 0,
    high_risk INTEGER NOT NULL DEFAULT 0,
    medium_risk INTEGER NOT NULL DEFAULT 0,
    low_risk INTEGER NOT NULL DEFAULT 0,
    result_json TEXT NOT NULL,
    checked_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ===== 房東資料表 =====
CREATE TABLE IF NOT EXISTS landlords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    rating_score REAL DEFAULT 0.0,
    review_count INTEGER DEFAULT 0
);

-- ===== 房源資料表 =====
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    address TEXT NOT NULL,
    district TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT '台北市',
    rent_price INTEGER NOT NULL,
    room_type TEXT NOT NULL,
    bedroom_count INTEGER NOT NULL DEFAULT 1,
    area_sqm REAL NOT NULL,
    floor INTEGER NOT NULL DEFAULT 1,
    total_floors INTEGER NOT NULL DEFAULT 5,
    is_tax_deductible INTEGER NOT NULL DEFAULT 0,
    is_subsidy_eligible INTEGER NOT NULL DEFAULT 0,
    is_available INTEGER NOT NULL DEFAULT 1,
    image_url TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(landlord_id) REFERENCES landlords(id)
);

-- ===== 法律問答資料表 =====
CREATE TABLE IF NOT EXISTS legal_faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    reference_law TEXT NOT NULL
);

-- ===== 數位點交紀錄資料表 =====
CREATE TABLE IF NOT EXISTS check_in_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,               -- 租客 ID (users.id)
    property_id INTEGER NOT NULL,           -- 房源 ID (properties.id)
    furniture_status TEXT,                  -- 家具狀況文字描述
    furniture_photo_path TEXT,              -- 家具照片路徑
    meter_value REAL NOT NULL,              -- 電表度數值
    meter_photo_path TEXT NOT NULL,         -- 電表照片路徑
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')), -- 後端自動生成時間戳記
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(property_id) REFERENCES properties(id)
);

-- ===== 爭議仲裁資料表 =====
CREATE TABLE IF NOT EXISTS disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lease_id INTEGER NOT NULL,
    initiator_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, reviewing, resolved
    admin_decision TEXT,
    admin_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    resolved_at TEXT,
    FOREIGN KEY(lease_id) REFERENCES leases(id),
    FOREIGN KEY(initiator_id) REFERENCES users(id)
);

-- ===== 爭議照片證據資料表 =====
CREATE TABLE IF NOT EXISTS dispute_evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispute_id INTEGER NOT NULL,
    uploader_id INTEGER NOT NULL,
    photo_type TEXT NOT NULL, -- move_in, move_out
    file_url TEXT NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(dispute_id) REFERENCES disputes(id),
    FOREIGN KEY(uploader_id) REFERENCES users(id)
);

-- ===== 報修紀錄資料表 =====
CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lease_id INTEGER NOT NULL,
    initiator_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, reviewing, resolved
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(lease_id) REFERENCES leases(id),
    FOREIGN KEY(initiator_id) REFERENCES users(id)
);

-- ===== 報修照片/影片證據資料表 =====
CREATE TABLE IF NOT EXISTS repair_evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    uploader_id INTEGER NOT NULL,
    evidence_type TEXT NOT NULL, -- original, broken
    file_url TEXT NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(repair_id) REFERENCES repairs(id),
    FOREIGN KEY(uploader_id) REFERENCES users(id)
);

-- ===== 報修溝通留言資料表 =====
CREATE TABLE IF NOT EXISTS repair_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(repair_id) REFERENCES repairs(id),
    FOREIGN KEY(sender_id) REFERENCES users(id)
);

