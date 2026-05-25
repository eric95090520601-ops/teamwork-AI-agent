import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.models import db, Dispute, DisputeEvidence, Contract, User
from datetime import datetime

dispute_bp = Blueprint('dispute', __name__)

# Note: We mock current user as user 1 for MVP testing.
def get_current_user_id():
    return 1 # Hardcoded for now. 

@dispute_bp.route('/disputes/create/<int:contract_id>', methods=['GET', 'POST'])
def create_dispute(contract_id):
    if request.method == 'POST':
        reason = request.form.get('reason')
        initiator_id = get_current_user_id()
        
        if not reason:
            flash('請填寫爭議原因')
            return redirect(request.url)
            
        dispute = Dispute(contract_id=contract_id, initiator_id=initiator_id, reason=reason)
        db.session.add(dispute)
        db.session.commit()
        return redirect(url_for('dispute.upload_evidence', dispute_id=dispute.id))
        
    return render_template('disputes/create.html', contract_id=contract_id)

@dispute_bp.route('/disputes/<int:dispute_id>/upload', methods=['GET', 'POST'])
def upload_evidence(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    
    if request.method == 'POST':
        photo = request.files.get('photo')
        photo_type = request.form.get('photo_type')
        uploader_id = get_current_user_id()
        
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            upload_path = os.path.join(current_app.root_path, 'static/uploads', unique_filename)
            photo.save(upload_path)
            
            file_url = f"/static/uploads/{unique_filename}"
            evidence = DisputeEvidence(dispute_id=dispute_id, uploader_id=uploader_id, photo_type=photo_type, file_url=file_url)
            db.session.add(evidence)
            db.session.commit()
            
            flash('照片上傳成功！')
            return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))
        else:
            flash('請選擇檔案')
            
    return render_template('disputes/upload.html', dispute=dispute)

@dispute_bp.route('/disputes/<int:dispute_id>', methods=['GET'])
def view_dispute(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    evidences = DisputeEvidence.query.filter_by(dispute_id=dispute_id).all()
    return render_template('disputes/result.html', dispute=dispute, evidences=evidences)

@dispute_bp.route('/admin/disputes', methods=['GET'])
def admin_dispute_list():
    disputes = Dispute.query.order_by(Dispute.created_at.desc()).all()
    return render_template('disputes/admin_list.html', disputes=disputes)

@dispute_bp.route('/admin/disputes/<int:dispute_id>', methods=['GET'])
def admin_dispute_detail(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    evidences = DisputeEvidence.query.filter_by(dispute_id=dispute_id).all()
    
    move_in_photos = [e for e in evidences if e.photo_type == 'move_in']
    move_out_photos = [e for e in evidences if e.photo_type == 'move_out']
    
    return render_template('disputes/admin_detail.html', dispute=dispute, move_in_photos=move_in_photos, move_out_photos=move_out_photos)

@dispute_bp.route('/admin/disputes/<int:dispute_id>/decide', methods=['POST'])
def admin_dispute_decide(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    admin_decision = request.form.get('admin_decision')
    
    if admin_decision:
        dispute.admin_decision = admin_decision
        dispute.status = 'resolved'
        dispute.resolved_at = datetime.utcnow()
        dispute.admin_id = 2 # Mock admin user id
        db.session.commit()
        flash('已送出裁決結果')
    else:
        flash('請填寫裁決結果說明')
        
    return redirect(url_for('dispute.admin_dispute_list'))
