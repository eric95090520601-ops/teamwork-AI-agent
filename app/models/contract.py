import json
from datetime import datetime
from app.models.db import get_db

# ============================================================
#  合約違法條款分析引擎
#  法律依據：民法、刑法、消費者保護法、租賃住宅市場發展及管理條例、
#            戶籍法、住宅法、所得稅法
# ============================================================

# ── 所有違法/高風險條款定義 ──────────────────────────────────
ILLEGAL_CLAUSES = [

    # ===== 押金類 =====
    {
        "id": "deposit_exceed",
        "category": "押金條款",
        "title": "押金超過兩個月租金",
        "description": "合約約定押金金額超過兩個月租金。",
        "keywords": ["押金三個月", "押金四個月", "押金五個月", "押金六個月",
                     "押金三個月份", "deposit 3 months", "押金超過"],
        "law": "租賃住宅市場發展及管理條例 第7條",
        "law_detail": "租賃住宅之押金，不得超過兩個月房屋租金之總額。超過部分，承租人得以抵付租金或請求返還。",
        "risk": "high",
        "suggestion": "要求房東將押金調整為不超過兩個月租金，超額部分可主張返還或抵扣租金。"
    },
    {
        "id": "deposit_no_receipt",
        "category": "押金條款",
        "title": "押金無書面收據或無退還條件",
        "description": "合約未載明押金退還條件或未提供書面收據。",
        "keywords": ["押金不退", "押金概不退還", "押金恕不退還", "押金不予退還"],
        "law": "民法 第259條、租賃住宅市場發展及管理條例 第7條",
        "law_detail": "租賃關係消滅時，房東應返還押金；押金之返還，得以書面約定之。",
        "risk": "high",
        "suggestion": "要求合約載明押金退還時程（通常為退租後30天內）及退還條件。"
    },

    # ===== 修繕責任類 =====
    {
        "id": "repair_all_tenant",
        "category": "修繕責任",
        "title": "所有修繕費用由租客負擔",
        "description": "合約將房屋所有修繕責任轉嫁給租客，包含非因租客使用造成的損壞。",
        "keywords": ["一切修繕", "所有修繕", "全部維修費用由承租人", "修繕費用自行負擔",
                     "維修費用由租客", "修繕費用由乙方", "一切維修費用"],
        "law": "民法 第429條",
        "law_detail": "租賃物之修繕，除契約另有訂定或另有習慣外，由出租人負擔。出租人為保存租賃物所為之必要行為，承租人不得拒絕。",
        "risk": "high",
        "suggestion": "此條款違反民法規定，房東有修繕義務。可主張該條款無效，要求房東負擔必要修繕費用。"
    },
    {
        "id": "repair_landlord_exempt",
        "category": "修繕責任",
        "title": "房東免除漏水、設備故障修繕責任",
        "description": "合約明定房東對漏水、冷氣、熱水器等設備故障不負修繕責任。",
        "keywords": ["漏水自行處理", "設備故障自行維修", "冷氣故障不負責",
                     "熱水器故障自理", "房東不負責修繕", "出租人不負修繕"],
        "law": "民法 第429條、第435條",
        "law_detail": "租賃物有瑕疵，致不能達租賃之目的者，承租人得終止契約。出租人應負擔必要修繕責任。",
        "risk": "high",
        "suggestion": "拍照存證設備現況，若房東不履行修繕義務，可向消費者保護官申訴或依民法主張損害賠償。"
    },

    # ===== 居住權保障類 =====
    {
        "id": "no_household_registration",
        "category": "居住權保障",
        "title": "禁止承租人設立戶籍",
        "description": "合約約定禁止租客在租屋處辦理戶籍登記。",
        "keywords": ["不得設籍", "禁止設籍", "不得辦理戶籍", "禁止辦理戶籍登記",
                     "不得遷入戶籍", "戶籍不得遷入"],
        "law": "戶籍法 第16條",
        "law_detail": "設有戶籍之人，應於現住地辦理戶籍登記。任何人不得以契約限制他人辦理戶籍之權利。",
        "risk": "high",
        "suggestion": "此條款違法，租客有權在居住地辦理戶籍登記，房東不得以契約加以限制。"
    },
    {
        "id": "no_subsidy",
        "category": "居住權保障",
        "title": "禁止申請政府租屋補助",
        "description": "合約約定租客不得申請政府租金補貼或其他居住補助。",
        "keywords": ["不得申請補助", "禁止申請補貼", "不得申請租屋補貼",
                     "禁止申請政府補助", "不可申請租金補助"],
        "law": "住宅法 第54條",
        "law_detail": "任何人不得以契約限制符合資格之承租人申請政府住宅補貼之權利。",
        "risk": "high",
        "suggestion": "此條款違法，租客有權申請符合資格的政府租屋補助，房東不得以合約加以剝奪。"
    },
    {
        "id": "no_tax_deduction",
        "category": "居住權保障",
        "title": "禁止申報租金所得稅扣除",
        "description": "合約約定租客不得申報租金支出於綜合所得稅特別扣除。",
        "keywords": ["不得報稅", "禁止報稅", "不得申報租金", "禁止申報扣除",
                     "不可報稅", "不得扣除租金"],
        "law": "所得稅法 第17條",
        "law_detail": "個人綜合所得稅計算，納稅義務人本人或配偶之租屋支出，在一定限額內得列舉扣除。任何契約不得限制此權利。",
        "risk": "high",
        "suggestion": "此條款違法，租客依法有權申報租金扣除額，可忽略此條款並照常申報。"
    },

    # ===== 合約終止類 =====
    {
        "id": "landlord_terminate_anytime",
        "category": "合約終止條款",
        "title": "房東可隨時要求租客搬遷",
        "description": "合約賦予房東在未給予合理期限下隨時終止租約、要求搬遷的權利。",
        "keywords": ["房東得隨時終止", "出租人得隨時解約", "隨時要求搬遷",
                     "房東可隨時收回", "隨時終止本契約", "立即搬離"],
        "law": "民法 第450條、第456條",
        "law_detail": "定期租賃，非有法定事由，不得提前終止。即使不定期租賃，出租人終止契約亦應給予租客合理之遷移期間。",
        "risk": "high",
        "suggestion": "要求合約載明終止通知期間（至少30天），並限縮房東終止事由為法定情形（如積欠租金、重大損壞等）。"
    },
    {
        "id": "no_tenant_termination",
        "category": "合約終止條款",
        "title": "禁止租客提前終止合約",
        "description": "合約完全剝奪租客提前終止合約的權利，或設定過苛的提前終止條件。",
        "keywords": ["承租人不得提前終止", "乙方不得解約", "不得提前退租",
                     "禁止提前解約", "租客不得中途退租"],
        "law": "民法 第450條、消費者保護法 第12條",
        "law_detail": "定型化契約中，完全剝奪消費者終止契約的權利，顯失公平，依消費者保護法第12條應屬無效。",
        "risk": "medium",
        "suggestion": "合理的提前終止條款應允許租客提前通知（如30天）並支付合理違約金（通常不超過一個月租金）。"
    },

    # ===== 違約金條款 =====
    {
        "id": "excessive_penalty",
        "category": "違約金條款",
        "title": "違約金過高（超過一個月租金）",
        "description": "合約約定的違約金金額明顯過高，超過一般合理範圍（通常以一至兩個月租金為限）。",
        "keywords": ["違約金三個月", "違約金四個月", "違約金五個月",
                     "賠償六個月", "賠償半年租金", "罰款三個月"],
        "law": "民法 第252條",
        "law_detail": "約定之違約金額過高者，法院得減至相當之數額。消費者保護法第12條亦規定，定型化契約顯失公平條款無效。",
        "risk": "medium",
        "suggestion": "可向法院聲請酌減違約金。建議在簽約前協商將違約金上限訂為一個月租金。"
    },

    # ===== 隱私與進入權類 =====
    {
        "id": "landlord_enter_anytime",
        "category": "隱私與進入權",
        "title": "房東可不事先通知進入房屋",
        "description": "合約賦予房東不需事先通知即可進入租屋處的權利。",
        "keywords": ["房東得隨時進入", "出租人得隨時進入", "房東可隨時進屋",
                     "不需通知進入", "無需預約進入", "隨時查看"],
        "law": "刑法 第306條、民法 第767條",
        "law_detail": "無故侵入他人住居，構成刑法第306條侵入住居罪。租客對租屋享有占有使用權，房東進入應事先告知。",
        "risk": "high",
        "suggestion": "要求合約載明房東進入需提前24至48小時通知，緊急情況除外。未經通知擅自進入可報警處理。"
    },

    # ===== 費用相關類 =====
    {
        "id": "utilities_overcharge",
        "category": "費用條款",
        "title": "水電費超過實際費率收取",
        "description": "合約約定水電費收費標準高於台電、自來水公司的實際費率。",
        "keywords": ["電費每度5元", "電費每度6元", "電費每度7元", "電費每度8元",
                     "電費每度9元", "電費每度10元", "自訂電費", "電費另計高於"],
        "law": "消費者保護法 第12條、電業法",
        "law_detail": "房東不得以轉供電力方式，向租客收取高於台電公告費率之電費。超收電費屬不當得利。",
        "risk": "medium",
        "suggestion": "台電住宅用電費率約為每度2.5至4.5元（依用電量累進）。若合約約定明顯偏高，可主張返還差額。"
    },
    {
        "id": "extra_hidden_fees",
        "category": "費用條款",
        "title": "約定不合理的額外費用",
        "description": "合約載有管理費、清潔費、服務費等名目不明或金額過高的額外收費。",
        "keywords": ["另收管理費", "額外服務費", "清潔費另計", "行政費另收",
                     "手續費另計", "雜費另計"],
        "law": "消費者保護法 第12條",
        "law_detail": "定型化契約中，對消費者不合理的額外收費條款，顯失公平者應屬無效。",
        "risk": "low",
        "suggestion": "要求房東在合約中明確列出所有費用項目及金額，避免日後產生爭議。"
    },

    # ===== 定型化契約類 =====
    {
        "id": "no_review_period",
        "category": "定型化契約",
        "title": "未提供合理審閱期",
        "description": "房東要求當場簽約，未給予租客合理的審閱期間（至少3天）。",
        "keywords": ["當場簽約", "立即簽署", "現場簽約有效", "不得要求審閱",
                     "簽約後不得反悔"],
        "law": "消費者保護法 第11條之1",
        "law_detail": "企業經營者與消費者訂立定型化契約前，應有30日以內之合理期間，供消費者審閱全部條款內容。",
        "risk": "medium",
        "suggestion": "租客有權要求至少3至5天的合約審閱期，拒絕當場簽約的壓力。"
    },
    {
        "id": "unilateral_change",
        "category": "定型化契約",
        "title": "房東得單方面變更合約條款",
        "description": "合約賦予房東不需租客同意即可單方面修改合約條款的權利。",
        "keywords": ["出租人得修改", "房東得變更", "條款得隨時調整", "房東保留修改權",
                     "得單方修改", "得片面變更"],
        "law": "消費者保護法 第12條",
        "law_detail": "定型化契約中，賦予一方得單方變更契約條款之條款，對消費者顯失公平，應屬無效。",
        "risk": "high",
        "suggestion": "任何合約變更均需雙方書面同意，房東不得單方修改已生效的合約條款。"
    },
]


def analyze_text(contract_text: str) -> list:
    """文字分析模式：關鍵字比對，找出潛在違法條款"""
    found_issues = []
    text_lower = contract_text.lower()

    for clause in ILLEGAL_CLAUSES:
        for keyword in clause["keywords"]:
            if keyword.lower() in text_lower or keyword in contract_text:
                found_issues.append({
                    "id": clause["id"],
                    "category": clause["category"],
                    "title": clause["title"],
                    "description": clause["description"],
                    "law": clause["law"],
                    "law_detail": clause["law_detail"],
                    "risk": clause["risk"],
                    "suggestion": clause["suggestion"],
                    "matched_keyword": keyword,
                    "mode": "text"
                })
                break  # 同一條款只計一次

    return found_issues


def analyze_checklist(checked_ids: list) -> list:
    """快速自檢模式：根據使用者勾選的項目產生分析結果"""
    found_issues = []
    clause_map = {c["id"]: c for c in ILLEGAL_CLAUSES}

    for cid in checked_ids:
        if cid in clause_map:
            clause = clause_map[cid]
            found_issues.append({
                "id": clause["id"],
                "category": clause["category"],
                "title": clause["title"],
                "description": clause["description"],
                "law": clause["law"],
                "law_detail": clause["law_detail"],
                "risk": clause["risk"],
                "suggestion": clause["suggestion"],
                "matched_keyword": None,
                "mode": "checklist"
            })

    return found_issues


def count_by_risk(issues: list) -> dict:
    return {
        "high": sum(1 for i in issues if i["risk"] == "high"),
        "medium": sum(1 for i in issues if i["risk"] == "medium"),
        "low": sum(1 for i in issues if i["risk"] == "low"),
        "total": len(issues)
    }


# ── 資料庫操作 ────────────────────────────────────────────────

class ContractModel:

    @staticmethod
    def save_result(user_id, filename, contract_text, issues):
        """儲存分析結果到資料庫"""
        db = get_db()
        counts = count_by_risk(issues)
        result_json = json.dumps(issues, ensure_ascii=False)
        checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO contract_checks
              (user_id, filename, contract_text, total_issues,
               high_risk, medium_risk, low_risk, result_json, checked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, filename, contract_text,
            counts["total"], counts["high"], counts["medium"], counts["low"],
            result_json, checked_at
        ))
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_history(user_id):
        """取得使用者過去所有分析紀錄"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, filename, total_issues, high_risk, medium_risk,
                   low_risk, checked_at
            FROM contract_checks
            WHERE user_id = ?
            ORDER BY checked_at DESC
        """, (user_id,))
        return cursor.fetchall()

    @staticmethod
    def get_result_by_id(check_id, user_id):
        """取得特定分析紀錄（含完整結果）"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT * FROM contract_checks
            WHERE id = ? AND user_id = ?
        """, (check_id, user_id))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["issues"] = json.loads(result["result_json"])
            return result
        return None
