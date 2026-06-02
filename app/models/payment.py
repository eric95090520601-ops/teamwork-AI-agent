from app.models.db import get_db

class PaymentModel:
    @staticmethod
    def create_payment(user_id, lease_id, amount, payment_date, payment_method, status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO payments (user_id, lease_id, amount, payment_date, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, lease_id, amount, payment_date, payment_method, status)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT p.*, l.address 
            FROM payments p
            JOIN leases l ON p.lease_id = l.id
            WHERE p.user_id = ?
            ORDER BY p.payment_date DESC
            """,
            (user_id,)
        )
        return cursor.fetchall()
