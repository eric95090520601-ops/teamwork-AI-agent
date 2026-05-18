from app import create_app
from app.models.models import db, User, Contract
import os

app = create_app()
with app.app_context():
    # 建立所有資料表
    db.create_all()
    
    # 清空現有資料 (避免重複)
    User.query.delete()
    Contract.query.delete()
    
    # 建立 mock users
    u1 = User(username='房客A', role='tenant')
    u2 = User(username='管理員', role='admin')
    u3 = User(username='房東B', role='landlord')
    db.session.add_all([u1, u2, u3])
    db.session.commit()
    
    # 建立 mock contract
    c1 = Contract(tenant_id=u1.id, landlord_id=u3.id, property_address='台北市信義區測試路1號')
    db.session.add(c1)
    db.session.commit()
    
    print("Mock 資料已成功初始化！")
