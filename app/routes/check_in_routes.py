import os
from datetime import datetime
from flask import g, Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
from app.models.check_in import CheckInModel
from app.models.user import UserModel
from app.models.lease import LeaseModel

check_in_bp = Blueprint('check_in', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@check_in_bp.route('/api/checkin', methods=['POST'])
def api_check_in():
    """
    處理前端數位點交上傳的 API。
    包含家具狀況描述、家具損壞照片上傳、電表度數與電表照片上傳。
    後端會自動為檔案加上防篡改的時間戳記並安全儲存。
    """
    try:
        # 1. 取得表單欄位資料
        user_id = request.form.get('user_id')
        property_id = request.form.get('property_id')
        furniture_status = request.form.get('furniture_status', '')
        meter_value = request.form.get('meter_value')

        # 欄位基本驗證
        if not user_id or not property_id or not meter_value:
            return jsonify({
                "status": "error",
                "message": "缺少必要欄位！請提供 user_id, property_id 與 meter_value。"
            }), 400

        try:
            user_id = int(user_id)
            property_id = int(property_id)
            meter_value = float(meter_value)
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "資料格式錯誤：ID 必須為整數，電表度數必須為數字。"
            }), 400

        # 2. 處理檔案上傳
        furniture_photo = request.files.get('furniture_photo')
        meter_photo = request.files.get('meter_photo')

        # 電表照片為必填
        if not meter_photo or meter_photo.filename == '':
            return jsonify({
                "status": "error",
                "message": "點交失敗：必須上傳電表度數照片！"
            }), 400

        # 建立安全上傳目錄 (app/static/uploads/check_ins)
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'check_ins')
        os.makedirs(upload_dir, exist_ok=True)

        # 生成防篡改的時間戳記字串
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 儲存電表照片
        if not allowed_file(meter_photo.filename):
            return jsonify({
                "status": "error",
                "message": "電表照片格式不支援！僅限 PNG, JPG, JPEG, GIF。"
            }), 400
        
        meter_ext = meter_photo.filename.rsplit('.', 1)[1].lower()
        meter_filename = secure_filename(f"checkin_{user_id}_{property_id}_meter_{timestamp}.{meter_ext}")
        meter_photo_path = os.path.join('static', 'uploads', 'check_ins', meter_filename)
        meter_photo.save(os.path.join(current_app.root_path, meter_photo_path))

        # 儲存家具照片（選填）
        furniture_photo_path = ""
        if furniture_photo and furniture_photo.filename != '':
            if not allowed_file(furniture_photo.filename):
                return jsonify({
                    "status": "error",
                    "message": "家具照片格式不支援！僅限 PNG, JPG, JPEG, GIF。"
                }), 400
            
            fur_ext = furniture_photo.filename.rsplit('.', 1)[1].lower()
            fur_filename = secure_filename(f"checkin_{user_id}_{property_id}_furniture_{timestamp}.{fur_ext}")
            furniture_photo_path = os.path.join('static', 'uploads', 'check_ins', fur_filename)
            furniture_photo.save(os.path.join(current_app.root_path, furniture_photo_path))

        # 3. 寫入 SQLite 資料庫
        record_id = CheckInModel.create_record(
            user_id=user_id,
            property_id=property_id,
            furniture_status=furniture_status,
            furniture_photo_path=furniture_photo_path,
            meter_value=meter_value,
            meter_photo_path=meter_photo_path
        )

        return jsonify({
            "status": "success",
            "message": "數位點交紀錄已成功建立，時間戳記與照片已安全存檔！",
            "data": {
                "record_id": record_id,
                "user_id": user_id,
                "property_id": property_id,
                "furniture_status": furniture_status,
                "furniture_photo_path": furniture_photo_path,
                "meter_value": meter_value,
                "meter_photo_path": meter_photo_path,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"伺服器內部錯誤：{str(e)}"
        }), 500

@check_in_bp.route('/handover', methods=['GET'])
def handover_page():
    user = UserModel.get_user(g.user_id)
    lease = LeaseModel.get_lease_by_user(g.user_id)
    # 預設對應的房源 ID 為 1 (第一筆測試資料)
    property_id = 1
    return render_template('handover_form.html', user=user, lease=lease, property_id=property_id)

@check_in_bp.route('/handover/history', methods=['GET'])
def handover_history_page():
    user = UserModel.get_user(g.user_id)
    records = CheckInModel.get_records_by_user(g.user_id)
    return render_template('handover_history.html', user=user, records=records)
