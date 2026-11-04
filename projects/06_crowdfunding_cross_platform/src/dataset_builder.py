"""
跨平台众筹对比实证 - 多源数据集生成与标准化构建 (Cross-Platform Dataset Builder)
对比分析 Kickstarter (美国经典), Indiegogo (美国混合模式), 摩点 Modian (中国文创新锐)
"""

import os
import random
import csv
import json

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CSV_FILE = os.path.join(DATA_DIR, "cross_platform_dataset.csv")

def build_cross_platform_data(n_per_platform: int = 250, seed: int = 2026) -> str:
    random.seed(seed)
    os.makedirs(DATA_DIR, exist_ok=True)

    platforms = ["Kickstarter", "Indiegogo", "Modian"]
    categories = ["Tech/Hardware", "Games/Tabletop", "Design/Art", "Publishing/Comics"]

    records = []
    pid_counter = 1

    for platform in platforms:
        for _ in range(n_per_platform):
            pid = f"{platform[:2].upper()}_{pid_counter:04d}"
            pid_counter += 1

            # 类别权重分布
            if platform == "Kickstarter":
                cat = random.choices(categories, weights=[0.40, 0.30, 0.20, 0.10])[0]
                funding_model = "Fixed" # KS 仅支持 All-or-Nothing
                goal = round(random.gauss(25000, 15000) / 500) * 500
                goal = max(2000.0, min(200000.0, goal))
                # KS 基础成功率约 40%~45%
                is_success = 1 if random.random() < 0.43 else 0
                avg_pledge = random.uniform(65.0, 180.0)

            elif platform == "Indiegogo":
                cat = random.choices(categories, weights=[0.55, 0.20, 0.15, 0.10])[0]
                # Indiegogo 拥有 Flexible (Keep-it-All) 和 Fixed 两种模式
                funding_model = "Flexible" if random.random() < 0.68 else "Fixed"
                goal = round(random.gauss(35000, 20000) / 500) * 500
                goal = max(3000.0, min(300000.0, goal))
                # Flexible 模式下无论是否达标发起人都能拿钱，导致虚标目标严重，达标率反而低 (~28%)
                is_success = 1 if random.random() < (0.35 if funding_model == "Fixed" else 0.26) else 0
                avg_pledge = random.uniform(80.0, 250.0)

            else: # Modian 摩点 (以桌游、二次元、国风文化与出版为主)
                cat = random.choices(categories, weights=[0.10, 0.45, 0.25, 0.20])[0]
                funding_model = "Fixed" # 摩点严格实行达标发货、未达标全额退款
                # 换算成美元 (汇率约 7.2)
                goal_rmb = round(random.gauss(30000, 18000) / 1000) * 1000
                goal_rmb = max(5000.0, min(300000.0, goal_rmb))
                goal = round(goal_rmb / 7.2, 2)
                # 摩点垂直粉丝黏性极高，达标率高 (~62%)
                is_success = 1 if random.random() < 0.62 else 0
                avg_pledge_rmb = random.uniform(120.0, 450.0)
                avg_pledge = round(avg_pledge_rmb / 7.2, 2)

            if is_success:
                ratio = random.uniform(1.05, 4.0) if random.random() < 0.85 else random.uniform(4.0, 15.0)
            else:
                ratio = random.uniform(0.05, 0.95)

            pledged = round(goal * ratio, 2)
            backers = max(1, int(pledged / avg_pledge))
            duration = random.choice([21, 30, 35, 45, 60])

            records.append({
                "project_id": pid,
                "platform": platform,
                "category": cat,
                "funding_model": funding_model,
                "goal_usd": goal,
                "pledged_usd": pledged,
                "backers_count": backers,
                "avg_pledge_usd": round(avg_pledge, 2),
                "duration_days": duration,
                "success": is_success,
                "funding_ratio": round(ratio, 4),
                "platform_fee_rate": 0.05,
                "payment_fee_rate": 0.01 if platform == "Modian" else 0.03
            })

    fieldnames = list(records[0].keys())
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return CSV_FILE

if __name__ == '__main__':
    p = build_cross_platform_data()
    print(f">>> 跨平台众筹对比数据集构建成功: {p}")
