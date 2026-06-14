import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.dispute import DisputeModel
from app.models.user import UserModel
from app.models.lease import LeaseModel
from datetime import datetime
import uuid
from app.utils.watermark import add_watermark

dispute_bp = Blueprint('dispute', __name__)

# 為了與主要模組整合，假設固定操作 user_id = 1

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dispute_bp.route('/disputes/create/<int:lease_id>', methods=['GET', 'POST'])
def create_dispute(lease_id):
    user = UserModel.get_user(g.user_id)
    if request.method == 'POST':
        reason = request.form.get('reason')
        initiator_id = g.user_id
        
        if not reason:
            flash('請填寫爭議原因')
            return redirect(request.url)
            
        dispute_id = DisputeModel.create_dispute(lease_id=lease_id, initiator_id=initiator_id, reason=reason)
        
        # 建立安全上傳目錄 app/static/uploads
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 處理入住點交照片批次上傳
        move_in_files = request.files.getlist('move_in_photos')
        for file in move_in_files:
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}_movein_{filename}"
                    upload_path = os.path.join(upload_folder, unique_filename)
                    file.save(upload_path)
                    add_watermark(upload_path)
                    
                    file_url = f"/static/uploads/{unique_filename}"
                    DisputeModel.add_evidence(dispute_id, initiator_id, 'move_in', file_url)
                else:
                    flash(f'檔案 {file.filename} 格式不支援，僅允許 png, jpg, jpeg, gif')
        
        # 處理退租屋況照片批次上傳
        move_out_files = request.files.getlist('move_out_photos')
        for file in move_out_files:
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}_moveout_{filename}"
                    upload_path = os.path.join(upload_folder, unique_filename)
                    file.save(upload_path)
                    add_watermark(upload_path)
                    
                    file_url = f"/static/uploads/{unique_filename}"
                    DisputeModel.add_evidence(dispute_id, initiator_id, 'move_out', file_url)
                else:
                    flash(f'檔案 {file.filename} 格式不支援，僅允許 png, jpg, jpeg, gif')
                    
        flash('爭議已成功發起，並已上傳所有證據照片！')
        return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))
        
    return render_template('disputes/create.html', lease_id=lease_id, user=user)

@dispute_bp.route('/disputes/<int:dispute_id>/add_evidence', methods=['POST'])
def add_dispute_evidence(dispute_id):
    dispute = DisputeModel.get_by_id(dispute_id)
    if not dispute:
        flash('找不到該案件')
        return redirect(url_for('payment.index'))
        
    if dispute['status'] == 'resolved':
        flash('此案件已裁決，無法追加證據照片。')
        return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))
        
    photo = request.files.get('photo')
    photo_type = request.form.get('photo_type')
    uploader_id = g.user_id
    
    if photo and photo.filename != '':
        if allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}_{photo_type}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, unique_filename)
            photo.save(upload_path)
            add_watermark(upload_path)
            
            file_url = f"/static/uploads/{unique_filename}"
            DisputeModel.add_evidence(dispute_id, uploader_id, photo_type, file_url)
            
            flash('追加照片上傳成功！')
        else:
            flash('照片格式不支援，僅允許 png, jpg, jpeg, gif')
    else:
        flash('請選擇檔案')
        
    return redirect(url_for('dispute.view_dispute', dispute_id=dispute_id))

@dispute_bp.route('/disputes/<int:dispute_id>', methods=['GET'])
def view_dispute(dispute_id):
    user = UserModel.get_user(g.user_id)
    dispute = DisputeModel.get_by_id(dispute_id)
    if not dispute:
        flash('找不到該案件')
        return redirect(url_for('payment.index'))
        
    evidences = DisputeModel.get_evidences(dispute_id)
    
    move_in_photos = [e for e in evidences if e['photo_type'] == 'move_in']
    move_out_photos = [e for e in evidences if e['photo_type'] == 'move_out']
    
    return render_template('disputes/result.html', 
                           dispute=dispute, 
                           move_in_photos=move_in_photos, 
                           move_out_photos=move_out_photos,
                           user=user)

@dispute_bp.route('/admin/disputes', methods=['GET'])
def admin_dispute_list():
    user = UserModel.get_user(g.user_id)
    disputes = DisputeModel.get_all()
    return render_template('disputes/admin_list.html', disputes=disputes, user=user)

@dispute_bp.route('/admin/disputes/<int:dispute_id>', methods=['GET'])
def admin_dispute_detail(dispute_id):
    user = UserModel.get_user(g.user_id)
    dispute = DisputeModel.get_by_id(dispute_id)
    if not dispute:
        flash('找不到該案件')
        return redirect(url_for('dispute.admin_dispute_list'))
        
    evidences = DisputeModel.get_evidences(dispute_id)
    
    move_in_photos = [e for e in evidences if e['photo_type'] == 'move_in']
    move_out_photos = [e for e in evidences if e['photo_type'] == 'move_out']
    
    return render_template('disputes/admin_detail.html', 
                           dispute=dispute, 
                           move_in_photos=move_in_photos, 
                           move_out_photos=move_out_photos,
                           user=user)

@dispute_bp.route('/admin/disputes/<int:dispute_id>/decide', methods=['POST'])
def admin_dispute_decide(dispute_id):
    admin_decision = request.form.get('admin_decision')
    
    if admin_decision:
        DisputeModel.update_decision(dispute_id, admin_decision, admin_id=2) # 2 代表模擬的管理員 ID
        flash('已送出裁決結果')
    else:
        flash('請填寫裁決結果說明')
        
    return redirect(url_for('dispute.admin_dispute_list'))
