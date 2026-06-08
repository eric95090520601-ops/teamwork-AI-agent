from app.models.db import get_db

class RepairModel:
    @staticmethod
    def create_repair(lease_id, initiator_id, item_name, description):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO repairs (lease_id, initiator_id, item_name, description, status)
            VALUES (?, ?, ?, ?, 'pending')
            """,
            (lease_id, initiator_id, item_name, description)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(repair_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.*, l.address AS lease_address, u.username AS initiator_name
            FROM repairs r
            JOIN leases l ON r.lease_id = l.id
            JOIN users u ON r.initiator_id = u.id
            WHERE r.id = ?
            """,
            (repair_id,)
        )
        return cursor.fetchone()

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.*, l.address AS lease_address
            FROM repairs r
            JOIN leases l ON r.lease_id = l.id
            WHERE r.initiator_id = ? OR l.user_id = ?
            ORDER BY r.created_at DESC
            """,
            (user_id, user_id)
        )
        return cursor.fetchall()

    @staticmethod
    def add_evidence(repair_id, uploader_id, evidence_type, file_url):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO repair_evidences (repair_id, uploader_id, evidence_type, file_url)
            VALUES (?, ?, ?, ?)
            """,
            (repair_id, uploader_id, evidence_type, file_url)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_evidences(repair_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM repair_evidences WHERE repair_id = ? ORDER BY uploaded_at ASC",
            (repair_id,)
        )
        return cursor.fetchall()

    @staticmethod
    def add_message(repair_id, sender_id, content):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO repair_messages (repair_id, sender_id, content)
            VALUES (?, ?, ?)
            """,
            (repair_id, sender_id, content)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_messages(repair_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT rm.*, u.username AS sender_name
            FROM repair_messages rm
            JOIN users u ON rm.sender_id = u.id
            WHERE rm.repair_id = ?
            ORDER BY rm.created_at ASC
            """,
            (repair_id,)
        )
        return cursor.fetchall()

    @staticmethod
    def update_status(repair_id, status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE repairs
            SET status = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (status, repair_id)
        )
        db.commit()
        return cursor.rowcount
