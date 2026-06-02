from app.models.db import get_db

class LeaseModel:
    @staticmethod
    def get_lease_by_user(user_id):
        db = get_db()
        cursor = db.cursor()
        # 假設一個 user 在這裡只有一個租約
        cursor.execute("SELECT * FROM leases WHERE user_id = ? LIMIT 1", (user_id,))
        return cursor.fetchone()

class UserModel:
    @staticmethod
    def get_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
