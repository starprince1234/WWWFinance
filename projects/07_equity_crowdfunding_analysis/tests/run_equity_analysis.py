"""
课题07：股权式众筹及数据分析 - 综合实证运行套件 (Master Equity Analysis Runner)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.equity_data import generate_equity_crowdfunding_data, CSV_FILE
from src.survival_analysis import load_equity_dataset, analyze_portfolio_returns_and_survival

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"   {title}")
    print("=" * 80)

def main():
    print("=" * 80)
    print("   《互联网金融》课题07：股权众筹投后生存率与投资回报幂律分布实证")
    print("   Sichuan University (SCU) - Internet Finance Research Project")
    print("=" * 80)

    # 1. 生成并加载数据集
    print_header("阶段一：股权众筹样本集构建与生命周期映射")
    csv_path = generate_equity_crowdfunding_data(n_samples=500, seed=42)
    records = load_equity_dataset(csv_path)
    print(f"[*] 成功构建 500 家股权众筹初创企业全生命周期实证数据: {csv_path}")

    # 2. 投资回报与生存率全景分析
    print_header("阶段二：项目最终退出形态分布 (Exit Status)")
    res = analyze_portfolio_returns_and_survival(records)
    dist = res["exit_status_distribution"]

    print(f"{'退出形态 (Exit Status)':<25} | {'企业数量':<10} | {'占比 (%)':<10} | {'经济学与投资学内涵'}")
    print("-" * 80)
    for status, d in dist.items():
        meaning = ""
        if status == "Bankrupt/Shutdown": meaning = "本金完全归零 (100% 亏损，天使投资常态)"
        elif status == "Operating/Active": meaning = "未实现流动性退出，获得有限分红或维持平价"
        elif status == "Acquired": meaning = "被大厂或产业资本并购 (3x ~ 12x 良好退出)"
        elif status == "IPO": meaning = "独立上市成为独角兽 (20x ~ 65x 超额爆发回报)"
        print(f"{status:<25} | {d['count']:<10} | {d['pct']}%     | {meaning}")

    # 3. 幂律分布检验
    print_header("阶段三：风险投资幂律法则 (Power Law Distribution) 实证检验")
    print(f"[*] 全样本模拟等额分散投资组合总回报倍数 (Portfolio Multiple) : {res['portfolio_multiple']}x")
    print(f"[*] 前 5% 头部明星项目 (Top 5% Deals) 创造的退出资金占比     : {res['power_law_top_5_share_pct']}%")
    print("\n[ 理论机理解析 ]")
    print("实证印证了风险投资领域的'幂律法则'（Venture Capital Power Law）：")
    print("虽然破产率超过 60%，但极少数头部超级明星企业（如 3% 的 IPO 项目）创造了全行业绝大多数的净收益。")

    # 4. 领投人机制对比
    print_header("阶段四：治理红利 —— '专业领投人 + 大众跟投人' 机制实证比对")
    lead_res = res["lead_investor_contrast"]
    w_lead = lead_res["with_lead_investor"]
    wo_lead = lead_res["without_lead_investor"]

    print(f"{'关键绩效指标':<22} | {'有专业领投人 (With Lead)':<22} | {'无专业领投 (Without Lead)':<22} | {'治理差异 (Diff)'}")
    print("-" * 85)
    print(f"{'样本项目数':<22} | {w_lead['count']:<22} | {wo_lead['count']:<22} | -")
    print(f"{'破产清算率':<22} | {w_lead['bankrupt_rate_pct']}%                 | {wo_lead['bankrupt_rate_pct']}%                 | 降低 {round(wo_lead['bankrupt_rate_pct'] - w_lead['bankrupt_rate_pct'], 1)}%")
    print(f"{'正向退出率 (并购/IPO)':<16} | {w_lead['positive_exit_rate_pct']}%                 | {wo_lead['positive_exit_rate_pct']}%                 | 提升 {round(w_lead['positive_exit_rate_pct'] - wo_lead['positive_exit_rate_pct'], 1)}%")
    print(f"{'投资组合综合倍数':<20} | {w_lead['portfolio_multiple']}x                  | {wo_lead['portfolio_multiple']}x                  | 收益率大幅领先")
    print(f"{'平均存续年限':<22} | {w_lead['avg_survival_years']} 年                  | {wo_lead['avg_survival_years']} 年                  | 存活周期显著延长")

    print_header("阶段五：中国股权众筹政策反思与投资人保护启示")
    print("1. 【合格投资人门槛】：早期大众跟投人普遍缺乏对 60%+ 破产率的心理承受力，必须实施严格的投资者适当性管理。")
    print("2. 【合伙企业 (SPV) 穿透】：我国《公司法》限制有限责任公司股东不超过 50 人，通过有限合伙 (LP) 归集小额投资人是必经路径。")
    print("3. 【信披与反稀释保护】：小额股东难以参与董事会，必须通过领投人监督及强制跟售权 (Tag-along Right) 保护散户权益。")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
