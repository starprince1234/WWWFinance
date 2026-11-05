"""
众筹书籍数据分析 - 计量经济学回归模型 (Econometric Modeling)
实现 Logistic 回归 (成功率几率比分析) 与多元 OLS 回归 (超额认购率影响因子分析)
"""

import math
from typing import List, Dict, Any, Tuple

def solve_ols(X: List[List[float]], y: List[float]) -> Tuple[List[float], float, List[float]]:
    """
    求解普通最小二乘法 (OLS): beta = (X^T X)^(-1) X^T y
    返回: (回归系数列表 beta, R-squared, t-stats)
    """
    n = len(y)
    k = len(X[0])

    # 计算 X^T X (k x k) 与 X^T y (k x 1)
    XtX = [[0.0] * k for _ in range(k)]
    Xty = [0.0] * k
    for row_idx in range(n):
        for i in range(k):
            Xty[i] += X[row_idx][i] * y[row_idx]
            for j in range(k):
                XtX[i][j] += X[row_idx][i] * X[row_idx][j]

    # 高斯-约旦消元法求逆矩阵 (XtX)^(-1)
    inv = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    A = [row[:] for row in XtX]

    for i in range(k):
        pivot = A[i][i]
        if abs(pivot) < 1e-12:
            pivot = 1e-6
        for j in range(k):
            A[i][j] /= pivot
            inv[i][j] /= pivot
        for r in range(k):
            if r != i:
                factor = A[r][i]
                for j in range(k):
                    A[r][j] -= factor * A[i][j]
                    inv[r][j] -= factor * inv[i][j]

    # beta = inv * Xty
    beta = [sum(inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]

    # 计算残差平方和与 R^2
    y_mean = sum(y) / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    residuals = [y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    ss_res = sum(e ** 2 for e in residuals)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # 标准误与 t-stats
    sigma2 = ss_res / (n - k)
    t_stats = []
    for i in range(k):
        se = math.sqrt(max(1e-12, sigma2 * inv[i][i]))
        t_stats.append(round(beta[i] / se, 3))

    return beta, round(r2, 4), t_stats


def fit_logit_model(X: List[List[float]], y: List[float], max_iter: int = 50, lr: float = 0.01) -> Dict[str, Any]:
    """
    拟合二元 Logistic 回归模型 (Newton-Raphson 梯度优化)
    """
    n = len(y)
    k = len(X[0])
    beta = [0.0] * k

    for _ in range(max_iter):
        grad = [0.0] * k
        for i in range(n):
            z = sum(X[i][j] * beta[j] for j in range(k))
            z = max(-15.0, min(15.0, z))
            p = 1.0 / (1.0 + math.exp(-z))
            err = y[i] - p
            for j in range(k):
                grad[j] += err * X[i][j]
        for j in range(k):
            beta[j] += lr * grad[j] / n

    # 计算预测准确率与对数几率比 (Odds Ratio)
    correct = 0
    for i in range(n):
        z = sum(X[i][j] * beta[j] for j in range(k))
        pred = 1 if z >= 0 else 0
        if pred == int(y[i]):
            correct += 1

    accuracy = round(correct / n * 100, 2)
    odds_ratios = [round(math.exp(b), 4) for b in beta]

    return {
        "beta": [round(b, 4) for b in beta],
        "odds_ratios": odds_ratios,
        "accuracy_pct": accuracy
    }


def run_econometric_models(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    feature_names = [
        "Intercept (截距项)",
        "ln(Goal) 筹资目标对数",
        "Duration 筹资天数",
        "Reward Tiers 回报档位数",
        "Word Count 文案字数(千字)",
        "Sentiment 文案积极情感分",
        "Has Video 宣传视频哑变量",
        "Creator History 发起人成功经验"
    ]

    X = []
    y_logit = []
    y_ols = []

    for r in records:
        row = [
            1.0,                                   # 常数项
            math.log(max(100.0, r["goal_cny"])),   # 目标金额对数
            r["duration_days"] / 10.0,             # 周期 (十天)
            r["reward_tiers_count"],               # 档位数
            r["pitch_word_count"] / 1000.0,        # 千字
            r["sentiment_score"],                  # 情感得分
            float(r["has_video"]),                 # 视频
            float(r["creator_past_projects"])      # 经验
        ]
        X.append(row)
        y_logit.append(float(r["success"]))
        y_ols.append(math.log(max(0.01, r["funding_ratio"])))

    # 1. 拟合 Logit 模型
    logit_res = fit_logit_model(X, y_logit)

    # 2. 拟合 OLS 模型
    beta_ols, r2, t_stats = solve_ols(X, y_ols)

    model_summary = []
    for i in range(len(feature_names)):
        model_summary.append({
            "variable": feature_names[i],
            "logit_coef": logit_res["beta"][i],
            "odds_ratio": logit_res["odds_ratios"][i],
            "ols_coef": round(beta_ols[i], 4),
            "ols_t_stat": t_stats[i]
        })

    return {
        "feature_names": feature_names,
        "logit_accuracy_pct": logit_res["accuracy_pct"],
        "ols_r_squared": r2,
        "parameters": model_summary
    }

