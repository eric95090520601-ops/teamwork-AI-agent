from flask import Flask
from app.models.models import db
from app.routes.dispute_routes import dispute_bp
from app.routes.verification_routes import verification_bp
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev_secret_key'
    
    # Ensure instance directory exists for SQLite
    os.makedirs(os.path.join(app.root_path, '../instance'), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, '../instance/database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Uploads directory
    os.makedirs(os.path.join(app.root_path, 'static/uploads'), exist_ok=True)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all() # Creates tables based on models if they don't exist
        
    app.register_blueprint(dispute_bp)
    app.register_blueprint(verification_bp)
    
    @app.route('/')
    def index():
        return '''
        <h1>歡迎來到租屋網站！</h1>
        <ul>
            <li><a href="/disputes/create/1">房客/房東：發起爭議 (測試合約ID=1)</a></li>
            <li><a href="/admin/disputes">管理員：進入爭議案件列表</a></li>
            <li><a href="/verify/apply">房東：申請真房東認證</a></li>
            <li><a href="/verify/status">房東：查看認證狀態</a></li>
            <li><a href="/admin/verifications">管理員：審核真房東申請</a></li>
        </ul>
        '''
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
