from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.contract import (
    ILLEGAL_CLAUSES, analyze_text, analyze_checklist,
    count_by_risk, ContractModel
)

contract_bp = Blueprint('contract', __name__)

  # MVP：固定測試帳號


@contract_bp.route('/contract')
def contract_check():
    """主頁：雙模式（快速自檢 + 文字分析）"""
    # 依分類分組，供快速自檢使用
    categories = {}
    for clause in ILLEGAL_CLAUSES:
        cat = clause["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(clause)

    return render_template('contract_check.html', categories=categories, total_clauses=len(ILLEGAL_CLAUSES))


@contract_bp.route('/contract/analyze', methods=['POST'])
def analyze():
    """處理分析請求（兩種模式）"""
    mode = request.form.get('mode', 'checklist')

    if mode == 'checklist':
        checked_ids = request.form.getlist('clauses')
        if not checked_ids:
            flash("請至少勾選一個條款進行檢查。", "warning")
            return redirect(url_for('contract.contract_check'))
        issues = analyze_checklist(checked_ids)
        filename = "快速自檢"
        contract_text = "（快速勾選模式，共勾選 {} 項）".format(len(checked_ids))

    else:  # text mode
        contract_text = request.form.get('contract_text', '').strip()
        if len(contract_text) < 20:
            flash("請輸入合約內容（至少20個字）後再進行分析。", "warning")
            return redirect(url_for('contract.contract_check'))
        issues = analyze_text(contract_text)
        filename = "文字分析（{} 字）".format(len(contract_text))

    # 儲存到資料庫
    save = request.form.get('save_result') == 'yes'
    check_id = None
    if save:
        check_id = ContractModel.save_result(
            g.user_id, filename, contract_text, issues
        )
        flash("分析結果已儲存，可在歷史紀錄中查閱。", "success")

    counts = count_by_risk(issues)

    return render_template(
        'contract_result.html',
        issues=issues,
        counts=counts,
        mode=mode,
        filename=filename,
        check_id=check_id,
        saved=save
    )


@contract_bp.route('/contract/history')
def contract_history():
    """歷史紀錄頁面"""
    history = ContractModel.get_history(g.user_id)
    return render_template('contract_history.html', history=history)


@contract_bp.route('/contract/history/<int:check_id>')
def contract_history_detail(check_id):
    """查看某筆歷史紀錄詳情"""
    result = ContractModel.get_result_by_id(check_id, g.user_id)
    if not result:
        flash("找不到該筆紀錄。", "danger")
        return redirect(url_for('contract.contract_history'))

    counts = count_by_risk(result["issues"])
    return render_template(
        'contract_result.html',
        issues=result["issues"],
        counts=counts,
        mode="history",
        filename=result["filename"],
        check_id=check_id,
        saved=True,
        checked_at=result["checked_at"]
    )
