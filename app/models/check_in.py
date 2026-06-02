from app.models.db import get_db

class CheckInModel:
    @staticmethod
    def create_record(user_id, property_id, furniture_status, furniture_photo_path, meter_value, meter_photo_path):
        """
        建立一筆新的點交紀錄。
        時間戳記 (created_at) 由 SQLite 資料庫自動生成。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO check_in_records (
                user_id, property_id, furniture_status, furniture_photo_path, meter_value, meter_photo_path
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, property_id, furniture_status, furniture_photo_path, meter_value, meter_photo_path)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_record_by_id(record_id):
        """
        透過紀錄 ID 取得特定的點交紀錄。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM check_in_records WHERE id = ?", (record_id,))
        return cursor.fetchone()

    @staticmethod
    def get_records_by_user(user_id):
        """
        取得特定租客的所有點交紀錄，依時間降序排列。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.*, p.title AS property_title, p.address AS property_address
            FROM check_in_records r
            JOIN properties p ON r.property_id = p.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
            """,
            (user_id,)
        )
        return cursor.fetchall()

    @staticmethod
    def get_records_by_property(property_id):
        """
        取得特定房源的所有點交紀錄，依時間降序排列。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.*, u.username, u.email
            FROM check_in_records r
            JOIN users u ON r.user_id = u.id
            WHERE r.property_id = ?
            ORDER BY r.created_at DESC
            """,
            (property_id,)
        )
        return cursor.fetchall()
