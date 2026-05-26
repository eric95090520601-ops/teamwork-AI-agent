import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.models import db, Dispute, DisputeEvidence, Contract, User
from datetime import datetime

dispute_bp = Blueprint('dispute', __name__)

# Note: We mock current user as user 1 for MVP testing.
def get_current_user_id():
    return 1 # Hardcoded for now. 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        # 處理入住點交照片批次上傳
        move_in_files = request.files.getlist('move_in_photos')
        for file in move_in_files:
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_movein_{filename}"
                    upload_path = os.path.join(current_app.root_path, 'static/uploads', unique_filename)
                    file.save(upload_path)
                    
                    file_url = f"/static/uploads/{unique_filename}"
                    evidence = DisputeEvidence(dispute_id=dispute.id, uploader_id=initiator_id, photo_type='move_in', file_url=file_url)
                    db.session.add(evidence)
                else:
                    flash(f'檔案 {file.filename} 格式不支援，僅允許 png, jpg, jpeg, gif')
        
        # 處理退租屋況照片批次上傳
        move_out_files = request.files.getlist('move_out_photos')
        for file in move_out_files:
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_moveout_{filename}"
                    upload_path = os.path.join(current_app.root_path, 'static/uploads', unique_filename)
                    file.save(upload_path)
                    
                    file_url = f"/static/uploads/{unique_filename}"
                    evidence = DisputeEvidence(dispute_id=dispute.id, uploader_id=initiator_id, photo_type='move_out', file_url=file_url)
                    db.session.add(evidence)
                else:
                    flash(f'檔案 {file.filename} 格式不支援，僅允許 png, jpg, jpeg, gif')
                    
        db.session.commit()
        flash('爭議已成功發起，並已上傳所有證據照片！')
        return redirect(url_for('dispute.view_dispute', dispute_id=dispute.id))
        
    return render_template('disputes/create.html', contract_id=contract_id)

@dispute_bp.route('/disputes/<int:dispute_id>/add_evidence', methods=['POST'])
def add_dispute_evidence(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    if dispute.status == 'resolved':
        flash('此案件已裁決，無法追加證據照片。')
        return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))
        
    photo = request.files.get('photo')
    photo_type = request.form.get('photo_type')
    uploader_id = get_current_user_id()
    
    if photo and photo.filename != '':
        if allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_type}_{filename}"
            upload_path = os.path.join(current_app.root_path, 'static/uploads', unique_filename)
            photo.save(upload_path)
            
            file_url = f"/static/uploads/{unique_filename}"
            evidence = DisputeEvidence(dispute_id=dispute_id, uploader_id=uploader_id, photo_type=photo_type, file_url=file_url)
            db.session.add(evidence)
            db.session.commit()
            
            flash('追加照片上傳成功！')
        else:
            flash('照片格式不支援，僅允許 png, jpg, jpeg, gif')
    else:
        flash('請選擇檔案')
        
    return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))

@dispute_bp.route('/disputes/<int:dispute_id>', methods=['GET'])
def view_dispute(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    evidences = DisputeEvidence.query.filter_by(dispute_id=dispute_id).all()
    
    move_in_photos = [e for e in evidences if e.photo_type == 'move_in']
    move_out_photos = [e for e in evidences if e.photo_type == 'move_out']
    
    return render_template('disputes/result.html', 
                           dispute=dispute, 
                           move_in_photos=move_in_photos, 
                           move_out_photos=move_out_photos)

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
