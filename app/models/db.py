import sqlite3
from flask import g
import os

# app/models/db.py
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATABASE = os.path.join(ROOT_DIR, 'instance', 'database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(ROOT_DIR, 'database', 'schema.sql')
        with open(schema_path, mode='r', encoding='utf-8') as f:
            db.cursor().executescript(f.read())
        db.commit()

        cursor = db.cursor()

        # ===== 租客 & 租約假資料 =====
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                ('王小明 (測試租客)', 'test@example.com')
            )
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO leases (user_id, address, monthly_rent, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                (user_id, '台北市信義區測試路一段1號5樓', 15000, '2026-01-01', '2026-12-31')
            )
            db.commit()

        # ===== 房東 & 房源假資料 =====
        cursor.execute("SELECT COUNT(*) FROM landlords")
        if cursor.fetchone()[0] == 0:
            landlords = [
                ('張大明', '0912-345-678', 4.8, 23),
                ('林小華', '0923-456-789', 4.5, 17),
                ('陳美玲', '0934-567-890', 3.9, 8),
                ('劉志成', '0945-678-901', 4.2, 31),
                ('黃淑芬', '0956-789-012', 5.0, 12),
                ('吳建宏', '0967-890-123', 3.5, 5),
                ('蔡宗翰', '0978-901-234', 4.7, 19),
                ('鄭雅婷', '0989-012-345', 4.1, 14),
            ]
            for name, phone, rating, reviews in landlords:
                cursor.execute(
                    "INSERT INTO landlords (name, phone, rating_score, review_count) VALUES (?, ?, ?, ?)",
                    (name, phone, rating, reviews)
                )
            db.commit()

            properties = [
                # (landlord_id, title, description, address, district, rent_price, room_type, bedroom_count, area_sqm, floor, total_floors, is_tax_deductible, is_subsidy_eligible)
                (1, '信義區精品套房，近捷運市政府站', '全新裝潢，獨立衛浴，家電齊全，採光極佳', '台北市信義區忠孝東路五段1號', '信義區', 18000, '套房', 1, 12.5, 5, 12, 1, 1),
                (2, '大安區溫馨雅房，近師大夜市', '共用廚房衛浴，交通便利，適合學生', '台北市大安區師大路88號', '大安區', 8500, '雅房', 1, 8.0, 3, 6, 0, 1),
                (3, '中山區兩房一廳，近百貨商圈', '空間寬敞，附停車位，住宅大樓安全管理', '台北市中山區南京東路二段50號', '中山區', 32000, '兩房一廳', 2, 28.0, 8, 14, 1, 0),
                (4, '內湖區整層住家，近科技園區', '三房兩廳，適合家庭，附車位，社區管理嚴謹', '台北市內湖區瑞光路200號', '內湖區', 45000, '整層住家', 3, 42.5, 6, 18, 1, 0),
                (5, '松山區精緻套房，近南京三民站', '全新設計師裝潢，採光良好，社區健身房', '台北市松山區南京東路四段100號', '松山區', 22000, '套房', 1, 15.0, 10, 20, 1, 1),
                (6, '萬華區平價雅房，生活機能優', '近西門町，交通便利，適合上班族', '台北市萬華區漢中街30號', '萬華區', 6500, '雅房', 1, 7.5, 2, 5, 0, 1),
                (7, '士林區一房一廳，近夜市', '附冷氣熱水器，樓梯公寓，生活機能佳', '台北市士林區文林路150號', '士林區', 16000, '一房一廳', 1, 18.0, 4, 5, 1, 1),
                (8, '北投區溫泉風套房，環境清幽', '近北投溫泉公園，採光通風良好，停車方便', '台北市北投區中山路20號', '北投區', 14000, '套房', 1, 13.0, 2, 7, 0, 1),
                (1, '大安區三房住家，近敦南誠品', '黃金地段，三房兩廳兩衛，電梯大廈，附管理員', '台北市大安區敦化南路一段200號', '大安區', 58000, '三房以上', 3, 55.0, 12, 25, 1, 0),
                (3, '文山區學區套房，近政大', '適合學生，近政治大學，交通方便，新裝潢', '台北市文山區指南路三段88號', '文山區', 11000, '套房', 1, 10.5, 3, 8, 0, 1),
                (5, '中正區商圈雅房，近台北車站', '近捷運台北車站，生活機能極佳，含水費', '台北市中正區忠孝西路一段50號', '中正區', 9000, '雅房', 1, 9.0, 4, 7, 1, 1),
                (7, '南港區科技套房，近南港展覽館', '鄰近南港軟體園區，電梯社區，附停車位', '台北市南港區經貿二路100號', '南港區', 20000, '套房', 1, 14.0, 7, 15, 1, 1),
                (2, '大同區老公寓整層，近大龍峒', '三房一廳，舊公寓，租金實惠，採光佳', '台北市大同區大龍街80號', '大同區', 25000, '整層住家', 3, 35.0, 3, 5, 0, 0),
                (4, '內湖區豪華兩房，附游泳池', '高級社區，泳池健身房，近捷運文湖線', '台北市內湖區成功路四段150號', '內湖區', 38000, '兩房一廳', 2, 32.0, 15, 22, 1, 0),
                (6, '松山區平價一房，近饒河夜市', '近捷運松山站，附基本家電，生活便利', '台北市松山區八德路四段200號', '松山區', 13000, '一房一廳', 1, 16.0, 2, 6, 0, 1),
            ]

            for prop in properties:
                cursor.execute("""
                    INSERT INTO properties
                    (landlord_id, title, description, address, district, rent_price,
                     room_type, bedroom_count, area_sqm, floor, total_floors,
                     is_tax_deductible, is_subsidy_eligible)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, prop)
            db.commit()
