import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.repair import RepairModel
from app.models.user import UserModel
from app.models.lease import LeaseModel
from datetime import datetime

repair_bp = Blueprint('repair', __name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@repair_bp.route('/repairs/')
def list_repairs():
    user = UserModel.get_user(g.user_id)
    repairs = RepairModel.get_all_by_user(g.user_id)
    return render_template('repairs/list.html', repairs=repairs, user=user)

@repair_bp.route('/repairs/create', methods=['GET', 'POST'])
def create_repair():
    user = UserModel.get_user(g.user_id)
    
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        
        lease = LeaseModel.get_lease_by_user(g.user_id)
            
        if not lease:
            flash("找不到相關租約", "error")
            return redirect(url_for('repair.list_repairs'))
            
        repair_id = RepairModel.create_repair(
            lease_id=lease['id'],
            initiator_id=g.user_id,
            item_name=item_name,
            description=description
        )
        
        # 建立安全上傳目錄 app/static/uploads
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 處理證據檔案上傳 (original & broken)
        for ev_type in ['original', 'broken']:
            files = request.files.getlist(ev_type)
            for file in files:
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{ev_type}_{filename}"
                        upload_path = os.path.join(upload_folder, unique_filename)
                        file.save(upload_path)
                        
                        file_url = f"/static/uploads/{unique_filename}"
                        RepairModel.add_evidence(repair_id, g.user_id, ev_type, file_url)
                    else:
                        flash(f'檔案 {file.filename} 格式不支援，僅允許圖片與影片格式')
                        
        flash('報修單已成功發起，並已上傳所有存證！')
        return redirect(url_for('repair.detail', repair_id=repair_id))
        
    return render_template('repairs/create.html', user=user)

@repair_bp.route('/repairs/<int:repair_id>', methods=['GET', 'POST'])
def detail(repair_id):
    user = UserModel.get_user(g.user_id)
    repair = RepairModel.get_by_id(repair_id)
    if not repair:
        flash("找不到該報修案件")
        return redirect(url_for('repair.list_repairs'))
        
    if request.method == 'POST':
        # 處理留言
        content = request.form.get('content')
        if content:
            RepairModel.add_message(repair_id, g.user_id, content)
            return redirect(url_for('repair.detail', repair_id=repair_id))
            
    # 取得證據並分類
    evidences = RepairModel.get_evidences(repair_id)
    original_evidences = [e for e in evidences if e['evidence_type'] == 'original']
    broken_evidences = [e for e in evidences if e['evidence_type'] == 'broken']
    
    # 取得留言
    messages = RepairModel.get_messages(repair_id)
    
    return render_template('repairs/detail.html', 
                           repair=repair, 
                           user=user,
                           original_evidences=original_evidences,
                           broken_evidences=broken_evidences,
                           messages=messages)
