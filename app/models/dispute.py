from app.models.db import get_db
from datetime import datetime

class DisputeModel:
    @staticmethod
    def create_dispute(lease_id, initiator_id, reason):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO disputes (lease_id, initiator_id, reason, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (lease_id, initiator_id, reason)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(dispute_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT d.*, l.address AS lease_address, l.monthly_rent, l.start_date, l.end_date, u.username AS initiator_name
            FROM disputes d
            JOIN leases l ON d.lease_id = l.id
            JOIN users u ON d.initiator_id = u.id
            WHERE d.id = ?
            """,
            (dispute_id,)
        )
        return cursor.fetchone()

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT d.*, l.address AS lease_address, u.username AS initiator_name
            FROM disputes d
            JOIN leases l ON d.lease_id = l.id
            JOIN users u ON d.initiator_id = u.id
            ORDER BY d.created_at DESC
            """
        )
        return cursor.fetchall()

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT d.*, l.address AS lease_address, u.username AS initiator_name
            FROM disputes d
            JOIN leases l ON d.lease_id = l.id
            JOIN users u ON d.initiator_id = u.id
            WHERE d.initiator_id = ?
            ORDER BY d.created_at DESC
            """,
            (user_id,)
        )
        return cursor.fetchall()

    @staticmethod
    def add_evidence(dispute_id, uploader_id, photo_type, file_url):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO dispute_evidences (dispute_id, uploader_id, photo_type, file_url)
            VALUES (?, ?, ?, ?)
            """,
            (dispute_id, uploader_id, photo_type, file_url)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_evidences(dispute_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM dispute_evidences WHERE dispute_id = ? ORDER BY uploaded_at ASC",
            (dispute_id,)
        )
        return cursor.fetchall()

    @staticmethod
    def update_decision(dispute_id, admin_decision, admin_id):
        db = get_db()
        cursor = db.cursor()
        resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            UPDATE disputes
            SET status = 'resolved', admin_decision = ?, admin_id = ?, resolved_at = ?
            WHERE id = ?
            """,
            (admin_decision, admin_id, resolved_at, dispute_id)
        )
        db.commit()
        return cursor.rowcount
