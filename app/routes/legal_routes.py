from flask import Blueprint, render_template, request, g
from app.models.db import get_db

legal_bp = Blueprint('legal', __name__)

@legal_bp.route('/legal')
def legal_faq():
    db = get_db()
    cursor = db.cursor()
    
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    query = "SELECT * FROM legal_faqs WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (question LIKE ? OR answer LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)
        
    cursor.execute(query, params)
    faqs = cursor.fetchall()
    
    # 取得所有分類供前端過濾器使用
    cursor.execute("SELECT DISTINCT category FROM legal_faqs")
    categories = [row['category'] for row in cursor.fetchall()]
    
    # Mock user for base.html rendering (consistent with other pages)
    cursor.execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()
    
    return render_template(
        'legal.html', 
        faqs=faqs, 
        categories=categories, 
        search_query=search_query, 
        category_filter=category_filter,
        user=user
    )
