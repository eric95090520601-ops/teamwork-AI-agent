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
