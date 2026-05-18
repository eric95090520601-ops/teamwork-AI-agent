from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False) # admin, landlord, tenant

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_address = db.Column(db.String(255), nullable=False)
    
    landlord = db.relationship('User', foreign_keys=[landlord_id])
    tenant = db.relationship('User', foreign_keys=[tenant_id])

class Dispute(db.Model):
    __tablename__ = 'disputes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') # pending, reviewing, resolved
    admin_decision = db.Column(db.Text, nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    contract = db.relationship('Contract')
    initiator = db.relationship('User', foreign_keys=[initiator_id])
    admin = db.relationship('User', foreign_keys=[admin_id])
    evidences = db.relationship('DisputeEvidence', backref='dispute', lazy=True)

class DisputeEvidence(db.Model):
    __tablename__ = 'dispute_evidences'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dispute_id = db.Column(db.Integer, db.ForeignKey('disputes.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    photo_type = db.Column(db.String(20), nullable=False) # move_in, move_out
    file_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploader = db.relationship('User')
