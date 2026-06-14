from flask import Flask
from app.models.db import init_db, close_connection
from app.routes.payment_routes import payment_bp
from app.routes.property_routes import property_bp
from app.routes.contract_routes import contract_bp
from app.routes.legal_routes import legal_bp
from app.routes.check_in_routes import check_in_bp
from app.routes.dispute_routes import dispute_bp
from app.routes.repair_routes import repair_bp
from app.routes.auth_routes import auth_bp
from flask import g, session
from app.models.user import UserModel
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

app.secret_key = 'super_secret_anti_scam_key'

app.register_blueprint(payment_bp)
app.register_blueprint(property_bp)
app.register_blueprint(contract_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(check_in_bp)
app.register_blueprint(dispute_bp)
app.register_blueprint(repair_bp)
app.register_blueprint(auth_bp)

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        # 預設為租客 1
        session['user_id'] = 1
        session['role'] = 'tenant'
        session['username'] = '王小明 (測試租客)'
        user_id = 1
        
    g.user_id = user_id
    g.user = UserModel.get_user(user_id)
    g.role = session.get('role', 'tenant')

@app.context_processor
def inject_user():
    return dict(user=g.user, current_role=g.role)

app.teardown_appcontext(close_connection)

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, port=5000)
