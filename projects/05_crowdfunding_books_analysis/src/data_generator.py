"""
众筹书籍数据分析 - 数据集生成与预处理模块 (Data Synthesizer & Pipeline)
以 Kickstarter Publishing 与国内摩点图书类目为原型，生成具备真实计量经济学特征的高质量众筹书籍数据集
"""

import os
import random
import math
import csv

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CSV_PATH = os.path.join(DATA_DIR, "book_crowdfunding_dataset.csv")

def generate_book_crowdfunding_data(n_samples: int = 600, random_seed: int = 42) -> str:
    """生成具备真实经济学特征的出版类众筹数据集"""
    random.seed(random_seed)
    os.makedirs(DATA_DIR, exist_ok=True)

    genres = ['Sci-Fi/Fantasy', 'Academic/Tech', 'Art/Comics', 'Fiction', 'Children']
    genre_weights = [0.28, 0.22, 0.25, 0.15, 0.10]

    title_prefixes = [
        "《区块链", "《赛博朋克", "《深空漫游", "《算法与", "《金融科技",
        "《手绘四川", "《古籍复刻：", "《童话秘境：", "《人工智能", "《奇幻大陆"
    ]
    title_suffixes = [
        "实录》", "全彩画集》", "通识指南》", "编年史》", "立体精装书》",
        "沉浸式绘本》", "密码学解析》", "特别珍藏本》", "思想史》", "手札》"
    ]

    fieldnames = [
        "project_id", "title", "genre", "goal_cny", "pledged_cny",
        "backers_count", "duration_days", "reward_tiers_count",
        "pitch_word_count", "sentiment_score", "has_video",
        "creator_past_projects", "state", "success", "funding_ratio"
    ]

    records = []
    for i in range(1, n_samples + 1):
        pid = f"BOOK_{i:04d}"
        genre = random.choices(genres, weights=genre_weights)[0]
        title = random.choice(title_prefixes) + random.choice(title_suffixes)

        # 1. 目标筹资额：对数正态分布 (多数在 1万~5万，少数数十万)
        log_goal = random.gauss(9.8, 0.9) # exp(9.8) ≈ 18000
        goal = round(math.exp(log_goal) / 100) * 100
        goal = max(3000.0, min(500000.0, goal))

        # 2. 众筹周期 (天)：通常集中在 20 ~ 45 天
        duration = random.choice([20, 25, 30, 35, 40, 45, 60])

        # 3. 回报档位数
        reward_tiers = random.randint(2, 7)

        # 4. 文案字数与情感倾向
        word_count = int(random.gauss(1200, 400))
        word_count = max(300, min(3500, word_count))
        sentiment = round(random.gauss(0.45, 0.25), 3) # 多数偏积极正面
        sentiment = max(-0.2, min(0.95, sentiment))

        # 5. 视频与发起人历史经验
        has_video = 1 if random.random() < 0.65 else 0
        past_projects = random.choices([0, 1, 2, 3, 4], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]

        # 6. 成功概率 Logit 模型潜在得分 (Latent Utility Model)
        # 负向影响：目标金额过高、周期过长(往往缺乏紧迫感)
        # 正向影响：回报档位丰富、文案详实、积极情感、宣传视频、过往信誉
        z = (
            - 0.85 * math.log(goal / 10000.0)
            - 0.015 * (duration - 30)
            + 0.18 * (reward_tiers - 4)
            + 0.0004 * (word_count - 1000)
            + 1.25 * (sentiment - 0.4)
            + 0.65 * has_video
            + 0.45 * past_projects
            + (0.35 if genre in ['Art/Comics', 'Academic/Tech'] else -0.1)
            + random.gauss(0, 0.75) # 未观测异质性扰动项
        )

        prob = 1.0 / (1.0 + math.exp(-z))
        is_success = 1 if random.random() < prob else 0

        if is_success:
            ratio = random.uniform(1.02, 3.5) if random.random() < 0.85 else random.uniform(3.5, 12.0)
            state = "successful"
        else:
            ratio = random.uniform(0.05, 0.95)
            state = "failed"

        pledged = round(goal * ratio, 2)
        avg_price = random.uniform(45.0, 150.0)
        backers = max(1, int(pledged / avg_price))

        records.append({
            "project_id": pid,
            "title": title,
            "genre": genre,
            "goal_cny": goal,
            "pledged_cny": pledged,
            "backers_count": backers,
            "duration_days": duration,
            "reward_tiers_count": reward_tiers,
            "pitch_word_count": word_count,
            "sentiment_score": sentiment,
            "has_video": has_video,
            "creator_past_projects": past_projects,
            "state": state,
            "success": is_success,
            "funding_ratio": round(ratio, 4)
        })

    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return CSV_PATH

if __name__ == '__main__':
    path = generate_book_crowdfunding_data()
    print(f">>> 众筹书籍实证数据集已生成: {path}")
