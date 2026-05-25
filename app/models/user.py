from app.models.db import get_db

class UserModel:
    @staticmethod
    def get_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
