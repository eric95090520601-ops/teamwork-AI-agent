from flask import g, Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.models.user import UserModel
from app.models.lease import LeaseModel
from app.models.payment import PaymentModel

payment_bp = Blueprint('payment', __name__)

# 為了方便測試，假設我們固定操作 user_id = 1

@payment_bp.route('/')
def index():
    user = UserModel.get_user(g.user_id)
    lease = LeaseModel.get_lease_by_user(g.user_id)
    
    if not user or not lease:
        return "系統錯誤：找不到測試使用者或租約，請確認資料庫是否初始化。", 500
        
    return render_template('index.html', user=user, lease=lease)

@payment_bp.route('/payments/new', methods=['GET', 'POST'])
def new_payment():
    user = UserModel.get_user(g.user_id)
    lease = LeaseModel.get_lease_by_user(g.user_id)

    if request.method == 'POST':
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method', 'Credit Card')
        
        # 取得當下時間
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 寫入資料庫
        PaymentModel.create_payment(
            user_id=g.user_id,
            lease_id=lease['id'],
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            status='Completed'
        )
        
        flash("繳款成功！您的資金已受到平台安全保障。", "success")
        return redirect(url_for('payment.payment_history'))
        
    return render_template('payment_form.html', user=user, lease=lease)

@payment_bp.route('/payments/history')
def payment_history():
    user = UserModel.get_user(g.user_id)
    payments = PaymentModel.get_all_by_user(g.user_id)
    return render_template('payment_history.html', user=user, payments=payments)
