import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
from app.models.models import db, User, LandlordVerification
from app.utils.watermark import add_watermark
from datetime import datetime

verification_bp = Blueprint('verification', __name__)

# Hardcoded IDs for testing purposes
MOCK_LANDLORD_ID = 3 # From init_mock_data.py
MOCK_ADMIN_ID = 2    # From init_mock_data.py

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@verification_bp.route('/verify/apply', methods=['GET', 'POST'])
def apply():
    # Use mock landlord user
    user = User.query.get(MOCK_LANDLORD_ID)
    if not user or user.role != 'landlord':
        flash('請以房東身分登入')
        return redirect(url_for('index'))
    
    # Check if already verified or pending
    existing = LandlordVerification.query.filter_by(landlord_id=user.id).order_by(LandlordVerification.submitted_at.desc()).first()
    if existing and existing.status in ['pending', 'approved']:
        flash('您已經有審核中或已通過的認證申請')
        return redirect(url_for('verification.status'))
    
    if request.method == 'POST':
        if 'id_card' not in request.files or 'property_cert' not in request.files:
            flash('請上傳身分證與房屋權狀')
            return redirect(request.url)
            
        id_card = request.files['id_card']
        property_cert = request.files['property_cert']
        
        if id_card.filename == '' or property_cert.filename == '':
            flash('未選擇檔案')
            return redirect(request.url)
            
        if id_card and allowed_file(id_card.filename) and property_cert and allowed_file(property_cert.filename):
            id_filename = secure_filename(id_card.filename)
            prop_filename = secure_filename(property_cert.filename)
            
            # Create timestamp to prevent overwriting
            ts = datetime.now().strftime('%Y%m%d%H%M%S')
            id_name = f"id_{ts}_{id_filename}"
            prop_name = f"prop_{ts}_{prop_filename}"
            
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'verifications')
            os.makedirs(upload_dir, exist_ok=True)
            
            id_path = os.path.join(upload_dir, id_name)
            prop_path = os.path.join(upload_dir, prop_name)
            
            id_card.save(id_path)
            property_cert.save(prop_path)
            
            # Apply watermark if image
            if id_path.endswith(('.png', '.jpg', '.jpeg')):
                add_watermark(id_path, id_path)
            if prop_path.endswith(('.png', '.jpg', '.jpeg')):
                add_watermark(prop_path, prop_path)
            
            # Save to database
            verification = LandlordVerification(
                landlord_id=user.id,
                id_card_url=f"uploads/verifications/{id_name}",
                property_cert_url=f"uploads/verifications/{prop_name}"
            )
            db.session.add(verification)
            db.session.commit()
            
            flash('認證資料已提交，請等待審核')
            return redirect(url_for('verification.status'))
        else:
            flash('僅支援 JPG, PNG, PDF 格式')
            
    return render_template('verify/apply.html', user=user)

@verification_bp.route('/verify/status')
def status():
    # Use mock landlord user
    user = User.query.get(MOCK_LANDLORD_ID)
    if not user:
        return redirect(url_for('index'))
        
    verification = LandlordVerification.query.filter_by(landlord_id=user.id).order_by(LandlordVerification.submitted_at.desc()).first()
    return render_template('verify/status.html', verification=verification, user=user)

@verification_bp.route('/admin/verifications')
def admin_list():
    # Admin view
    verifications = LandlordVerification.query.order_by(
        db.case(
            (LandlordVerification.status == 'pending', 1),
            (LandlordVerification.status == 'rejected', 2),
            (LandlordVerification.status == 'approved', 3)
        ),
        LandlordVerification.submitted_at.desc()
    ).all()
    return render_template('admin/verifications.html', verifications=verifications)

@verification_bp.route('/admin/verify/<int:id>')
def admin_detail(id):
    verification = LandlordVerification.query.get_or_404(id)
    return render_template('admin/verify_detail.html', verification=verification)

@verification_bp.route('/admin/verify/<int:id>/approve', methods=['POST'])
def admin_approve(id):
    verification = LandlordVerification.query.get_or_404(id)
    if verification.status == 'pending':
        verification.status = 'approved'
        verification.reviewed_at = datetime.utcnow()
        verification.reviewer_id = MOCK_ADMIN_ID
        
        # Update user's is_verified flag
        verification.landlord.is_verified = True
        
        db.session.commit()
        flash('已核准認證')
    return redirect(url_for('verification.admin_list'))

@verification_bp.route('/admin/verify/<int:id>/reject', methods=['POST'])
def admin_reject(id):
    verification = LandlordVerification.query.get_or_404(id)
    if verification.status == 'pending':
        reason = request.form.get('reason')
        if not reason:
            flash('退件必須填寫理由')
            return redirect(url_for('verification.admin_detail', id=id))
            
        verification.status = 'rejected'
        verification.rejection_reason = reason
        verification.reviewed_at = datetime.utcnow()
        verification.reviewer_id = MOCK_ADMIN_ID
        db.session.commit()
        flash('已退件')
    return redirect(url_for('verification.admin_list'))
