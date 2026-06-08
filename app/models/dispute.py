from app.models.db import get_db

class DisputeModel:
    @staticmethod
    def create_dispute(lease_id, initiator_id, reason):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO disputes (lease_id, initiator_id, reason)
            VALUES (?, ?, ?)
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
            SELECT d.*, u.username as initiator_name
            FROM disputes d
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
            SELECT d.*, u.username as initiator_name
            FROM disputes d
            JOIN users u ON d.initiator_id = u.id
            ORDER BY d.created_at DESC
            """
        )
        return cursor.fetchall()

    @staticmethod
    def resolve_dispute(dispute_id, admin_decision, admin_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE disputes
            SET status = 'resolved', admin_decision = ?, admin_id = ?, resolved_at = datetime('now')
            WHERE id = ?
            """,
            (admin_decision, admin_id, dispute_id)
        )
        db.commit()


class DisputeEvidenceModel:
    @staticmethod
    def create_evidence(dispute_id, uploader_id, photo_type, file_url):
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
    def get_by_dispute(dispute_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT e.*, u.username as uploader_name
            FROM dispute_evidences e
            JOIN users u ON e.uploader_id = u.id
            WHERE e.dispute_id = ?
            ORDER BY e.uploaded_at ASC
            """,
            (dispute_id,)
        )
        return cursor.fetchall()
