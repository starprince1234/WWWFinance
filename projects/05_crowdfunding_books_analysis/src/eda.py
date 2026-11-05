"""
众筹书籍数据分析 - 探索性数据分析与描述性统计 (EDA Module)
计算全样本与分类别的成功率、均值分布、显著性差异与皮尔逊相关性矩阵
"""

import csv
import math
from typing import Dict, List, Any

def load_data(csv_path: str) -> List[Dict[str, Any]]:
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "project_id": row["project_id"],
                "title": row["title"],
                "genre": row["genre"],
                "goal_cny": float(row["goal_cny"]),
                "pledged_cny": float(row["pledged_cny"]),
                "backers_count": int(row["backers_count"]),
                "duration_days": int(row["duration_days"]),
                "reward_tiers_count": int(row["reward_tiers_count"]),
                "pitch_word_count": int(row["pitch_word_count"]),
                "sentiment_score": float(row["sentiment_score"]),
                "has_video": int(row["has_video"]),
                "creator_past_projects": int(row["creator_past_projects"]),
                "state": row["state"],
                "success": int(row["success"]),
                "funding_ratio": float(row["funding_ratio"])
            })
    return records

def _calc_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {}
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)
    sorted_v = sorted(values)
    median = sorted_v[n // 2]
    return {
        "count": n,
        "mean": round(mean, 2),
        "std": round(std, 2),
        "median": round(median, 2),
        "min": round(sorted_v[0], 2),
        "max": round(sorted_v[-1], 2)
    }

def run_descriptive_analysis(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(records)
    successes = [r for r in records if r["success"] == 1]
    fails = [r for r in records if r["success"] == 0]
    overall_success_rate = round(len(successes) / n * 100, 2)

    # 1. 分题材分类统计
    genres = set(r["genre"] for r in records)
    genre_summary = {}
    for g in sorted(genres):
        g_recs = [r for r in records if r["genre"] == g]
        g_succ = [r for r in g_recs if r["success"] == 1]
        genre_summary[g] = {
            "total_count": len(g_recs),
            "success_count": len(g_succ),
            "success_rate_pct": round(len(g_succ) / len(g_recs) * 100, 2),
            "avg_goal": round(sum(r["goal_cny"] for r in g_recs) / len(g_recs), 2),
            "avg_pledged": round(sum(r["pledged_cny"] for r in g_recs) / len(g_recs), 2),
            "avg_backers": round(sum(r["backers_count"] for r in g_recs) / len(g_recs), 1)
        }

    # 2. 成功组 vs 失败组关键指标对比 (均值对照)
    keys_to_compare = [
        "goal_cny", "duration_days", "reward_tiers_count",
        "pitch_word_count", "sentiment_score", "has_video", "creator_past_projects"
    ]
    group_contrast = {}
    for k in keys_to_compare:
        succ_vals = [r[k] for r in successes]
        fail_vals = [r[k] for r in fails]
        group_contrast[k] = {
            "success_mean": round(sum(succ_vals) / len(succ_vals), 3),
            "failed_mean": round(sum(fail_vals) / len(fail_vals), 3),
            "diff": round(sum(succ_vals) / len(succ_vals) - sum(fail_vals) / len(fail_vals), 3)
        }

    return {
        "total_samples": n,
        "success_rate_pct": overall_success_rate,
        "genre_breakdown": genre_summary,
        "group_contrast": group_contrast
    }

