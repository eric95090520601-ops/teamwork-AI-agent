from flask import Flask
from app.models.db import init_db, close_connection
from app.routes.payment_routes import payment_bp
from app.routes.property_routes import property_bp
from app.routes.legal_routes import legal_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# 設定 Secret Key
app.secret_key = 'super_secret_anti_scam_key'

# 註冊 Blueprint 路由
app.register_blueprint(payment_bp)
app.register_blueprint(property_bp)
app.register_blueprint(legal_bp)

# 在應用程式結束時關閉資料庫連線
app.teardown_appcontext(close_connection)

if __name__ == '__main__':
    # 啟動時初始化資料庫與假資料
    init_db(app)
    app.run(debug=True, port=5000)
