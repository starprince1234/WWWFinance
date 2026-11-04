"""
股权众筹实证分析 - 投资回报幂律分布与生存分析引擎 (Survival & Return Engine)
计算风险投资幂律收益集中度、破产存活率曲线与“领投人机制”的显著治理红利
"""

import csv
from typing import Dict, List, Any

def load_equity_dataset(csv_path: str) -> List[Dict[str, Any]]:
    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append({
                "deal_id": r["deal_id"],
                "company_name": r["company_name"],
                "sector": r["sector"],
                "valuation_pre_k_usd": float(r["valuation_pre_k_usd"]),
                "raise_target_k_usd": float(r["raise_target_k_usd"]),
                "actual_raised_k_usd": float(r["actual_raised_k_usd"]),
                "equity_offered_pct": float(r["equity_offered_pct"]),
                "backers_count": int(r["backers_count"]),
                "lead_investor_present": int(r["lead_investor_present"]),
                "founder_prior_exits": int(r["founder_prior_exits"]),
                "survival_years": float(r["survival_years"]),
                "exit_status": r["exit_status"],
                "realized_multiple": float(r["realized_multiple"]),
                "annualized_irr_pct": float(r["annualized_irr_pct"])
            })
    return records

def analyze_portfolio_returns_and_survival(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(records)

    # 1. 退出状态分布
    status_counts = {}
    for r in records:
        s = r["exit_status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    status_dist = {s: {"count": c, "pct": round(c / n * 100, 2)} for s, c in status_counts.items()}

    # 2. 投资组合真实综合回报 (Portfolio Economics)
    # 假设每笔投资等额投入 10,000 美元
    invest_per_deal = 10000.0
    total_invested = n * invest_per_deal
    total_returned = sum(invest_per_deal * r["realized_multiple"] for r in records)
    portfolio_multiple = round(total_returned / total_invested, 3)

    # 幂律分布检验 (Power Law Distribution): 前 5% 最成功项目贡献的收益占比
    sorted_by_ret = sorted(records, key=lambda x: x["realized_multiple"], reverse=True)
    top_5_pct_count = max(1, int(n * 0.05))
    top_5_returned = sum(invest_per_deal * r["realized_multiple"] for r in sorted_by_ret[:top_5_pct_count])
    top_5_share_pct = round(top_5_returned / total_returned * 100, 2)

    # 3. “领投人机制 (Lead Investor)” 效应检验
    lead_group = [r for r in records if r["lead_investor_present"] == 1]
    nolead_group = [r for r in records if r["lead_investor_present"] == 0]

    def _calc_group_stats(grp: List[Dict[str, Any]]) -> Dict[str, Any]:
        gn = len(grp)
        g_bankrupt = len([r for r in grp if r["exit_status"] == "Bankrupt/Shutdown"])
        g_positive_exit = len([r for r in grp if r["exit_status"] in ("Acquired", "IPO")])
        g_multiples = [r["realized_multiple"] for r in grp]
        g_total_ret = sum(invest_per_deal * m for m in g_multiples)
        g_portfolio_mult = round(g_total_ret / (gn * invest_per_deal), 3)

        return {
            "count": gn,
            "bankrupt_rate_pct": round(g_bankrupt / gn * 100, 2),
            "positive_exit_rate_pct": round(g_positive_exit / gn * 100, 2),
            "portfolio_multiple": g_portfolio_mult,
            "avg_survival_years": round(sum(r["survival_years"] for r in grp) / gn, 2)
        }

    lead_contrast = {
        "with_lead_investor": _calc_group_stats(lead_group),
        "without_lead_investor": _calc_group_stats(nolead_group)
    }

    # 4. 分行业分布
    sectors = sorted(set(r["sector"] for r in records))
    sector_summary = {}
    for s in sectors:
        s_recs = [r for r in records if r["sector"] == s]
        sn = len(s_recs)
        s_bankrupt = len([r for r in s_recs if r["exit_status"] == "Bankrupt/Shutdown"])
        s_pos = len([r for r in s_recs if r["exit_status"] in ("Acquired", "IPO")])
        s_mult = round(sum(r["realized_multiple"] for r in s_recs) / sn, 2)
        sector_summary[s] = {
            "count": sn,
            "bankrupt_rate_pct": round(s_bankrupt / sn * 100, 2),
            "positive_exit_pct": round(s_pos / sn * 100, 2),
            "avg_multiple": s_mult
        }

    return {
        "sample_size": n,
        "exit_status_distribution": status_dist,
        "portfolio_multiple": portfolio_multiple,
        "power_law_top_5_share_pct": top_5_share_pct,
        "lead_investor_contrast": lead_contrast,
        "sector_breakdown": sector_summary
    }
