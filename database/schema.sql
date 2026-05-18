CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    property_address TEXT NOT NULL,
    FOREIGN KEY(landlord_id) REFERENCES users(id),
    FOREIGN KEY(tenant_id) REFERENCES users(id)
);

CREATE TABLE disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    initiator_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    admin_decision TEXT,
    admin_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY(contract_id) REFERENCES contracts(id),
    FOREIGN KEY(initiator_id) REFERENCES users(id),
    FOREIGN KEY(admin_id) REFERENCES users(id)
);

CREATE TABLE dispute_evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispute_id INTEGER NOT NULL,
    uploader_id INTEGER NOT NULL,
    photo_type TEXT NOT NULL,
    file_url TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dispute_id) REFERENCES disputes(id),
    FOREIGN KEY(uploader_id) REFERENCES users(id)
);
