import os
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models.models import db, Repair, RepairEvidence, Message, User, Contract
from datetime import datetime

bp = Blueprint('repair', __name__, url_prefix='/repairs')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def list_repairs():
    # 假設使用 user_id = 1 (房客A) 來測試，實務上應從 session 取得
    user_id = 1
    user = User.query.get(user_id)
    
    if user.role == 'tenant':
        # 房客看自己發起或與自己合約相關的報修
        contracts = Contract.query.filter_by(tenant_id=user.id).all()
        contract_ids = [c.id for c in contracts]
        repairs = Repair.query.filter(Repair.contract_id.in_(contract_ids)).all()
    elif user.role == 'landlord':
        # 房東看自己出租的合約報修
        contracts = Contract.query.filter_by(landlord_id=user.id).all()
        contract_ids = [c.id for c in contracts]
        repairs = Repair.query.filter(Repair.contract_id.in_(contract_ids)).all()
    else:
        repairs = Repair.query.all()
        
    return render_template('repairs/list.html', repairs=repairs, user=user)

@bp.route('/create', methods=['GET', 'POST'])
def create_repair():
    user_id = 1 # 測試用
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        
        # 尋找第一筆相關合約
        if user.role == 'tenant':
            contract = Contract.query.filter_by(tenant_id=user.id).first()
        else:
            contract = Contract.query.filter_by(landlord_id=user.id).first()
            
        if not contract:
            flash("找不到相關租約", "error")
            return redirect(url_for('repair.list_repairs'))
            
        repair = Repair(
            contract_id=contract.id,
            initiator_id=user.id,
            item_name=item_name,
            description=description,
            status='pending'
        )
        db.session.add(repair)
        db.session.commit()
        
        # 處理證據檔案上傳 (original & broken)
        for ev_type in ['original', 'broken']:
            files = request.files.getlist(ev_type)
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    
                    evidence = RepairEvidence(
                        repair_id=repair.id,
                        uploader_id=user.id,
                        evidence_type=ev_type,
                        file_url=f"uploads/{filename}"
                    )
                    db.session.add(evidence)
                    
        db.session.commit()
        return redirect(url_for('repair.detail', repair_id=repair.id))
        
    return render_template('repairs/create.html', user=user)

@bp.route('/<int:repair_id>', methods=['GET', 'POST'])
def detail(repair_id):
    user_id = 1 # 測試用
    user = User.query.get(user_id)
    repair = Repair.query.get_or_404(repair_id)
    
    if request.method == 'POST':
        # 處理留言
        content = request.form.get('content')
        if content:
            msg = Message(
                repair_id=repair.id,
                sender_id=user.id,
                content=content
            )
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('repair.detail', repair_id=repair.id))
            
    # 取得證據並分類
    original_evidences = [e for e in repair.evidences if e.evidence_type == 'original']
    broken_evidences = [e for e in repair.evidences if e.evidence_type == 'broken']
    
    return render_template('repairs/detail.html', 
                           repair=repair, 
                           user=user,
                           original_evidences=original_evidences,
                           broken_evidences=broken_evidences)
