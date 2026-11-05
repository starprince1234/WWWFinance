"""
跨平台众筹对比实证 - 统计比对与商业机制分析引擎 (Cross-Platform Comparator)
深度剖析 Kickstarter vs Indiegogo vs 摩点 的治理规则、成功率与平台商业生态
"""

import csv
from typing import Dict, List, Any

def load_cross_data(csv_path: str) -> List[Dict[str, Any]]:
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append({
                "project_id": r["project_id"],
                "platform": r["platform"],
                "category": r["category"],
                "funding_model": r["funding_model"],
                "goal_usd": float(r["goal_usd"]),
                "pledged_usd": float(r["pledged_usd"]),
                "backers_count": int(r["backers_count"]),
                "avg_pledge_usd": float(r["avg_pledge_usd"]),
                "duration_days": int(r["duration_days"]),
                "success": int(r["success"]),
                "funding_ratio": float(r["funding_ratio"]),
                "platform_fee_rate": float(r["platform_fee_rate"]),
                "payment_fee_rate": float(r["payment_fee_rate"])
            })
    return records

def analyze_cross_platform_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    platforms = ["Kickstarter", "Indiegogo", "Modian"]
    summary = {}

    for p in platforms:
        p_recs = [r for r in records if r["platform"] == p]
        n = len(p_recs)
        succ = [r for r in p_recs if r["success"] == 1]
        succ_rate = round(len(succ) / n * 100, 2)
        avg_goal = round(sum(r["goal_usd"] for r in p_recs) / n, 2)
        avg_pledged = round(sum(r["pledged_usd"] for r in p_recs) / n, 2)
        avg_backers = round(sum(r["backers_count"] for r in p_recs) / n, 1)
        avg_ticket = round(sum(r["avg_pledge_usd"] for r in p_recs) / n, 2)

        # 类别分布
        cat_counts = {}
        for r in p_recs:
            c = r["category"]
            cat_counts[c] = cat_counts.get(c, 0) + 1
        top_cat = max(cat_counts.items(), key=lambda x: x[1])

        # 费率计算
        p_fee = p_recs[0]["platform_fee_rate"] * 100
        pay_fee = p_recs[0]["payment_fee_rate"] * 100
        total_friction = p_fee + pay_fee

        summary[p] = {
            "sample_size": n,
            "success_rate_pct": succ_rate,
            "avg_goal_usd": avg_goal,
            "avg_pledged_usd": avg_pledged,
            "avg_backers": avg_backers,
            "avg_ticket_usd": avg_ticket,
            "top_category": f"{top_cat[0]} ({round(top_cat[1]/n*100, 1)}%)",
            "fee_structure": f"平台 {p_fee:.0f}% + 通道 {pay_fee:.1f}% = 综合摩擦 {total_friction:.1f}%"
        }

    # 机制对比: Fixed (All-or-Nothing) vs Flexible (Keep-it-All)
    fixed_recs = [r for r in records if r["funding_model"] == "Fixed"]
    flex_recs = [r for r in records if r["funding_model"] == "Flexible"]

    mechanism_comparison = {
        "Fixed_Funding_All_or_Nothing": {
            "count": len(fixed_recs),
            "success_rate_pct": round(sum(r["success"] for r in fixed_recs) / len(fixed_recs) * 100, 2),
            "avg_backers": round(sum(r["backers_count"] for r in fixed_recs) / len(fixed_recs), 1)
        },
        "Flexible_Funding_Keep_it_All": {
            "count": len(flex_recs),
            "success_rate_pct": round(sum(r["success"] for r in flex_recs) / len(flex_recs) * 100, 2),
            "avg_backers": round(sum(r["backers_count"] for r in flex_recs) / len(flex_recs), 1)
        }
    }

    return {
        "platform_summary": summary,
        "mechanism_comparison": mechanism_comparison
    }

