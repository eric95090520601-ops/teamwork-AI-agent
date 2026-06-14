from flask import Blueprint, session, redirect, url_for, request, flash
from app.models.user import UserModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/switch_role/<int:user_id>')
def switch_role(user_id):
    user = UserModel.get_user(user_id)
    if user:
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['username'] = user['username']
        flash(f"已成功切換身分為：{user['username']} ({user['role']})", "success")
    else:
        flash("找不到該使用者", "danger")
        
    # 回到上一頁，或預設回到首頁
    next_url = request.referrer or url_for('payment.index')
    return redirect(next_url)
