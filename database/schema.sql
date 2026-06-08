CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
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

-- ===== 爭議單資料表 =====
CREATE TABLE IF NOT EXISTS disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lease_id INTEGER NOT NULL,
    initiator_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    admin_decision TEXT,
    admin_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT,
    FOREIGN KEY(lease_id) REFERENCES leases(id),
    FOREIGN KEY(initiator_id) REFERENCES users(id),
    FOREIGN KEY(admin_id) REFERENCES users(id)
);

-- ===== 爭議證據資料表 =====
CREATE TABLE IF NOT EXISTS dispute_evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispute_id INTEGER NOT NULL,
    uploader_id INTEGER NOT NULL,
    photo_type TEXT NOT NULL,
    file_url TEXT NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(dispute_id) REFERENCES disputes(id),
    FOREIGN KEY(uploader_id) REFERENCES users(id)
);
