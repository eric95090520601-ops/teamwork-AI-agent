from app.models.db import get_db


class PropertyModel:

    @staticmethod
    def get_all(filters=None):
        """
        取得所有房源，支援進階篩選條件。
        filters: dict，可包含以下 key:
            - rent_min, rent_max (int)
            - room_types (list of str)
            - districts (list of str)
            - is_tax_deductible (bool)
            - is_subsidy_eligible (bool)
            - min_rating (float)
            - sort_by (str): 'rent_asc', 'rent_desc', 'rating_desc'
        """
        db = get_db()
        if filters is None:
            filters = {}

        query = """
            SELECT p.*, l.name AS landlord_name, l.rating_score, l.review_count
            FROM properties p
            JOIN landlords l ON p.landlord_id = l.id
            WHERE p.is_available = 1
        """
        params = []

        # 租金範圍篩選
        if filters.get('rent_min'):
            query += " AND p.rent_price >= ?"
            params.append(int(filters['rent_min']))
        if filters.get('rent_max'):
            query += " AND p.rent_price <= ?"
            params.append(int(filters['rent_max']))

        # 房型篩選
        if filters.get('room_types'):
            placeholders = ','.join('?' for _ in filters['room_types'])
            query += f" AND p.room_type IN ({placeholders})"
            params.extend(filters['room_types'])

        # 區域篩選
        if filters.get('districts'):
            placeholders = ','.join('?' for _ in filters['districts'])
            query += f" AND p.district IN ({placeholders})"
            params.extend(filters['districts'])

        # 可報稅篩選
        if filters.get('is_tax_deductible'):
            query += " AND p.is_tax_deductible = 1"

        # 可申請租屋補助篩選
        if filters.get('is_subsidy_eligible'):
            query += " AND p.is_subsidy_eligible = 1"

        # 房東評價最低分篩選
        if filters.get('min_rating'):
            query += " AND l.rating_score >= ?"
            params.append(float(filters['min_rating']))

        # 排序
        sort_by = filters.get('sort_by', 'default')
        if sort_by == 'rent_asc':
            query += " ORDER BY p.rent_price ASC"
        elif sort_by == 'rent_desc':
            query += " ORDER BY p.rent_price DESC"
        elif sort_by == 'rating_desc':
            query += " ORDER BY l.rating_score DESC"
        else:
            query += " ORDER BY p.id DESC"

        cursor = db.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def get_by_id(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.*, l.name AS landlord_name, l.rating_score, l.review_count
            FROM properties p
            JOIN landlords l ON p.landlord_id = l.id
            WHERE p.id = ?
        """, (property_id,))
        return cursor.fetchone()

    @staticmethod
    def get_all_districts():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT district FROM properties WHERE is_available = 1 ORDER BY district")
        return [row['district'] for row in cursor.fetchall()]

    @staticmethod
    def get_stats():
        """取得統計資料（總筆數、平均租金）"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT COUNT(*) AS total,
                   AVG(rent_price) AS avg_rent,
                   MIN(rent_price) AS min_rent,
                   MAX(rent_price) AS max_rent
            FROM properties WHERE is_available = 1
        """)
        return cursor.fetchone()

    @staticmethod
    def get_by_landlord(landlord_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.*, l.name AS landlord_name, l.rating_score, l.review_count
            FROM properties p
            JOIN landlords l ON p.landlord_id = l.id
            WHERE p.landlord_id = ?
            ORDER BY p.created_at DESC
        """, (landlord_id,))
        return cursor.fetchall()

    @staticmethod
    def create_property(landlord_id, title, description, address, district, rent_price, room_type, bedroom_count, area_sqm, floor, total_floors, is_tax_deductible, is_subsidy_eligible):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO properties
            (landlord_id, title, description, address, district, rent_price,
             room_type, bedroom_count, area_sqm, floor, total_floors,
             is_tax_deductible, is_subsidy_eligible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (landlord_id, title, description, address, district, rent_price, room_type, bedroom_count, area_sqm, floor, total_floors, is_tax_deductible, is_subsidy_eligible))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def toggle_availability(property_id, landlord_id):
        db = get_db()
        cursor = db.cursor()
        # 取得目前狀態
        cursor.execute("SELECT is_available FROM properties WHERE id = ? AND landlord_id = ?", (property_id, landlord_id))
        row = cursor.fetchone()
        if row:
            new_status = 0 if row['is_available'] == 1 else 1
            cursor.execute("UPDATE properties SET is_available = ? WHERE id = ? AND landlord_id = ?", (new_status, property_id, landlord_id))
            db.commit()
            return new_status
        return None
