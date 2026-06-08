import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.dispute import DisputeModel, DisputeEvidenceModel
from app.models.lease import LeaseModel
from datetime import datetime

dispute_bp = Blueprint('dispute', __name__)

# 模擬當前使用者 (房客)
def get_current_user_id():
    return 1

# 模擬管理員
def get_admin_user_id():
    return 2

@dispute_bp.route('/disputes/create', methods=['GET', 'POST'])
def create_dispute():
    # 改為取得目前使用者的租約
    user_id = get_current_user_id()
    lease = LeaseModel.get_lease_by_user(user_id)
    
    if not lease:
        flash('找不到您的租約資料。', 'danger')
        return redirect(url_for('payment.index'))

    if request.method == 'POST':
        reason = request.form.get('reason')
        
        if not reason:
            flash('請填寫爭議原因', 'danger')
            return redirect(request.url)
            
        dispute_id = DisputeModel.create_dispute(lease['id'], user_id, reason)
        return redirect(url_for('dispute.upload_evidence', dispute_id=dispute_id))
        
    return render_template('disputes/create.html', lease_id=lease['id'])

@dispute_bp.route('/disputes/<int:dispute_id>/upload', methods=['GET', 'POST'])
def upload_evidence(dispute_id):
    dispute = DisputeModel.get_by_id(dispute_id)
    if not dispute:
        return "Dispute not found", 404
    
    if request.method == 'POST':
        photo = request.files.get('photo')
        photo_type = request.form.get('photo_type')
        uploader_id = get_current_user_id()
        
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            
            uploads_dir = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            upload_path = os.path.join(uploads_dir, unique_filename)
            photo.save(upload_path)
            
            file_url = f"/static/uploads/{unique_filename}"
            DisputeEvidenceModel.create_evidence(dispute_id, uploader_id, photo_type, file_url)
            
            flash('照片上傳成功！', 'success')
            return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))
        else:
            flash('請選擇檔案', 'danger')
            
    return render_template('disputes/upload.html', dispute=dispute)

@dispute_bp.route('/disputes/<int:dispute_id>', methods=['GET'])
def view_dispute(dispute_id):
    dispute = DisputeModel.get_by_id(dispute_id)
    if not dispute:
        return "Dispute not found", 404
        
    evidences = DisputeEvidenceModel.get_by_dispute(dispute_id)
    return render_template('disputes/result.html', dispute=dispute, evidences=evidences)

@dispute_bp.route('/admin/disputes', methods=['GET'])
def admin_dispute_list():
    disputes = DisputeModel.get_all()
    return render_template('disputes/admin_list.html', disputes=disputes)

@dispute_bp.route('/admin/disputes/<int:dispute_id>', methods=['GET'])
def admin_dispute_detail(dispute_id):
    dispute = DisputeModel.get_by_id(dispute_id)
    if not dispute:
        return "Dispute not found", 404
        
    evidences = DisputeEvidenceModel.get_by_dispute(dispute_id)
    
    # Sqlite Row is dict-like
    move_in_photos = [e for e in evidences if e['photo_type'] == 'move_in']
    move_out_photos = [e for e in evidences if e['photo_type'] == 'move_out']
    
    return render_template('disputes/admin_detail.html', dispute=dispute, move_in_photos=move_in_photos, move_out_photos=move_out_photos)

@dispute_bp.route('/admin/disputes/<int:dispute_id>/decide', methods=['POST'])
def admin_dispute_decide(dispute_id):
    admin_decision = request.form.get('admin_decision')
    
    if admin_decision:
        admin_id = get_admin_user_id()
        DisputeModel.resolve_dispute(dispute_id, admin_decision, admin_id)
        flash('已送出裁決結果！', 'success')
    else:
        flash('請填寫裁決說明', 'danger')
        
    return redirect(url_for('dispute.admin_dispute_list'))
