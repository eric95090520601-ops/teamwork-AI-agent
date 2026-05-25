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
                (user_id, '台中市西屯區台灣大道三段1號5樓', 15000, '2026-01-01', '2026-12-31')
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

            # 台中市房源假資料
            properties = [
                # (landlord_id, title, description, address, district, rent_price, room_type, bedroom_count, area_sqm, floor, total_floors, is_tax_deductible, is_subsidy_eligible)
                (1, '西屯區精品套房，近捷運香榭站', '全新裝潢，獨立衛浴，家電齊全，採光極佳', '台中市西屯區台灣大道三段1號', '西屯區', 16000, '套房', 1, 12.5, 5, 12, 1, 1),
                (2, '北區溫馨雅房，近中興大學', '共用廚房衛浴，交通便利，適合學生', '台中市北區平等路88號', '北區', 7500, '雅房', 1, 8.0, 3, 6, 0, 1),
                (3, '西區兩房一廳，近中友百貨', '空間寬敞，附停車位，住宅大樓安全管理', '台中市西區與興北路50號', '西區', 28000, '兩房一廳', 2, 28.0, 8, 14, 1, 0),
                (4, '大里區整層住家，客廳寬敞', '三房兩廳，適合家庭，附車位，社區管理嚴謹', '台中市大里區吉峰路200號', '大里區', 38000, '整層住家', 3, 42.5, 6, 18, 1, 0),
                (5, '北屯區精緻套房，近大奇百貨', '全新設計師裝潢，採光良好，社區健身房', '台中市北屯區周濱北路100號', '北屯區', 19000, '套房', 1, 15.0, 10, 20, 1, 1),
                (6, '南區平價雅房，生活機能優', '近中華夜市，交通便利，適合上班族', '台中市南區建國路30號', '南區', 6000, '雅房', 1, 7.5, 2, 5, 0, 1),
                (7, '南屯區一房一廳，近興大夜市', '附冷氣熱水器，樓梯公寓，生活機能佳', '台中市南屯區大墩山路150號', '南屯區', 14000, '一房一廳', 1, 18.0, 4, 5, 1, 1),
                (8, '豐原區基地套房，環境清幽', '近豐原火車站，採光通風良好，停車方便', '台中市豐原區中山路20號', '豐原區', 12000, '套房', 1, 13.0, 2, 7, 0, 1),
                (1, '中區三房住家，近謝廣商圈', '黃金地段，三房兩廳兩衛，電梯大廈，附管理員', '台中市中區自由路200號', '中區', 50000, '三房以上', 3, 55.0, 12, 25, 1, 0),
                (3, '東區學區套房，近逢甲大學', '適合學生，近逢甲大學，交通方便，新裝潢', '台中市東區貢獻路88號', '東區', 10000, '套房', 1, 10.5, 3, 8, 0, 1),
                (5, '北區商圈雅房，近台中火車站', '近台中火車站，生活機能極佳，含水費', '台中市北區台灣大道一段50號', '北區', 8500, '雅房', 1, 9.0, 4, 7, 1, 1),
                (7, '南屯區科技套房，近軟體園區', '鄰近台中軟體園區，電梯社區，附停車位', '台中市南屯區興大路100號', '南屯區', 18000, '套房', 1, 14.0, 7, 15, 1, 1),
                (2, '西區公寓整層，近舉道夜市', '三房一廳，舊公寓，租金實惠，採光佳', '台中市西區中港路80號', '西區', 22000, '整層住家', 3, 35.0, 3, 5, 0, 0),
                (4, '烏日區豪華兩房，交通便利', '優質社區，近台中高鐵烏日站，生活機能完善', '台中市烏日區中山路150號', '烏日區', 32000, '兩房一廳', 2, 32.0, 15, 22, 1, 0),
                (6, '北屯區平價一房，生活便利', '近北屯夜市，附基本家電，生活便利', '台中市北屯區文山路200號', '北屯區', 11500, '一房一廳', 1, 16.0, 2, 6, 0, 1),
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

        # ===== 法律問答假資料 =====
        cursor.execute("SELECT COUNT(*) FROM legal_faqs")
        if cursor.fetchone()[0] == 0:
            faqs = [
                ('押金問題', '押金最高可以收幾個月？', '依據法規規定，住宅租賃之押金，最高不得超過二個月的租金總額。若超過部分，承租人可以要求抵充租金。', '租賃住宅市場發展及管理條例第 7 條'),
                ('押金問題', '退租時房東遲遲不退還押金怎麼辦？', '若點交無誤且無欠費，房東應即時退還押金。若房東拒絕，承租人可發存證信函催告，甚至向鄉鎮市區調解委員會申請調解。', '民法第 421 條及一般租賃契約慣例'),
                ('修繕責任', '租屋處的冷氣壞了，應該由誰負責修繕？', '除租賃契約另有約定（例如合約明定由房客負責）或因房客故意/重大過失損壞外，房屋及附屬設備（如冷氣、熱水器）的自然損壞均應由房東負責修繕。', '民法第 429 條第 1 項'),
                ('修繕責任', '房東一直不來修繕，我可以自己修再扣租金嗎？', '可以。若房東經催告後仍不修繕，房客可自行雇工修繕，並憑收據從次月租金中扣除該修繕費用。', '民法第 430 條'),
                ('提前解約', '租約未到期，我可以提前解約嗎？', '須看合約是否約定「得任意終止租約」。若有約定，通常需提前一個月通知；若未約定，除有法定事由（如房屋危及安全）外，提前解約可能面臨最高一個月租金的違約金。', '租賃住宅市場發展及管理條例第 11 條'),
                ('費用分攤', '房屋稅、地價稅跟管理費應該誰繳？', '房屋稅、地價稅依法由所有權人（房東）繳納，不得轉嫁給房客。管理費則視雙方租賃契約的約定，未約定者通常由房東負擔，但實務上常約定由房客負擔。', '房屋稅條例第 4 條 / 契約自由原則')
            ]
            for faq in faqs:
                cursor.execute(
                    "INSERT INTO legal_faqs (category, question, answer, reference_law) VALUES (?, ?, ?, ?)",
                    faq
                )
            db.commit()
