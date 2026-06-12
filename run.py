from flask import Flask
from app.models.db import init_db, close_connection
from app.routes.payment_routes import payment_bp
from app.routes.property_routes import property_bp
from app.routes.contract_routes import contract_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

app.secret_key = 'super_secret_anti_scam_key'

app.register_blueprint(payment_bp)
app.register_blueprint(property_bp)
app.register_blueprint(contract_bp)

app.teardown_appcontext(close_connection)

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True, port=5000)
