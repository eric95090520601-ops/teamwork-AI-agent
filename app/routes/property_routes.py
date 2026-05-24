from flask import Blueprint, render_template, request
from app.models.property import PropertyModel

property_bp = Blueprint('property', __name__)

# 所有支援的區域列表（台中市各行政區）
ALL_DISTRICTS = [
    '中區', '東區', '南區', '西區', '北區',
    '北屯區', '西屯區', '南屯區', '太平區', '大里區',
    '豐原區', '烏日區'
]

# 所有房型
ALL_ROOM_TYPES = [
    ('套房', '套房（獨立衛浴）'),
    ('雅房', '雅房（共用衛浴）'),
    ('整層住家', '整層住家'),
    ('一房一廳', '1 房 1 廳'),
    ('兩房一廳', '2 房 1 廳'),
    ('三房以上', '3 房以上'),
]

# 租金區間選項
RENT_RANGES = [
    ('', '', '不限'),
    ('0', '5000', '5,000 元以下'),
    ('5000', '10000', '5,000 – 10,000 元'),
    ('10000', '15000', '10,000 – 15,000 元'),
    ('15000', '20000', '15,000 – 20,000 元'),
    ('20000', '30000', '20,000 – 30,000 元'),
    ('30000', '', '30,000 元以上'),
]


@property_bp.route('/properties')
def property_list():
    """房源搜尋與篩選主頁"""
    # 從 Query String 取得篩選條件
    rent_min = request.args.get('rent_min', '')
    rent_max = request.args.get('rent_max', '')
    room_types = request.args.getlist('room_type')
    districts = request.args.getlist('district')
    is_tax_deductible = 'is_tax_deductible' in request.args
    is_subsidy_eligible = 'is_subsidy_eligible' in request.args
    min_rating = request.args.get('min_rating', '')
    sort_by = request.args.get('sort_by', 'default')

    # 組合篩選條件
    filters = {
        'rent_min': rent_min or None,
        'rent_max': rent_max or None,
        'room_types': room_types or None,
        'districts': districts or None,
        'is_tax_deductible': is_tax_deductible,
        'is_subsidy_eligible': is_subsidy_eligible,
        'min_rating': min_rating or None,
        'sort_by': sort_by,
    }

    properties = PropertyModel.get_all(filters)
    stats = PropertyModel.get_stats()

    # 將目前選取的租金區間標籤找出來
    selected_rent_label = '不限'
    for r_min, r_max, label in RENT_RANGES:
        if r_min == rent_min and r_max == rent_max:
            selected_rent_label = label
            break

    return render_template(
        'properties.html',
        properties=properties,
        stats=stats,
        all_districts=ALL_DISTRICTS,
        all_room_types=ALL_ROOM_TYPES,
        rent_ranges=RENT_RANGES,
        # 回傳目前選取的篩選值，方便前端維持狀態
        selected_rent_min=rent_min,
        selected_rent_max=rent_max,
        selected_room_types=room_types,
        selected_districts=districts,
        is_tax_deductible=is_tax_deductible,
        is_subsidy_eligible=is_subsidy_eligible,
        selected_min_rating=min_rating,
        selected_sort_by=sort_by,
        selected_rent_label=selected_rent_label,
    )
