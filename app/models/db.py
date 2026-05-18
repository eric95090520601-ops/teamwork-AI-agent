import sqlite3
from flask import g
import os

# app/models/db.py
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATABASE = os.path.join(ROOT_DIR, 'instance', 'database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # 確保 instance 目錄存在
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    # 建立表格
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(ROOT_DIR, 'database', 'schema.sql')
        with open(schema_path, mode='r', encoding='utf-8') as f:
            db.cursor().executescript(f.read())
        db.commit()

        # 插入假資料供開發展示用
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ('王小明 (測試租客)', 'test@example.com'))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO leases (user_id, address, monthly_rent, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                           (user_id, '台北市信義區測試路一段1號5樓', 15000, '2026-01-01', '2026-12-31'))
            db.commit()
