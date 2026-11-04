# 课题 07：股权式众筹及数据分析 (Equity Crowdfunding Empirical Research)

> **对应 Gitee 课题**：`#I8K09K` 股权式众筹及数据分析  
> **项目定位**：股权众筹投后生存率、退出回报幂律分布与“领投人+跟投人”治理机制的 500 初创样本大数据实证  
> **环境要求**：Python 3.8+ (零外部依赖，纯原生标准库数学计算)

---

## 一、 研究背景与核心问题

与基于商品的奖励型众筹不同，股权众筹（Equity Crowdfunding）涉及真实公司的未上市公司股权、未来股份认购权（SAFE）或可转债。股权众筹在美国（JOBS Act Title III / Reg CF，如 AngelList、Republic、Wefunder）蓬勃发展，而在中国经历了 2014~2016 年的试点高潮后，因非法集资风险、信息不对称、股东人数超限与二级流动性缺失进入严监管整顿期。

本项目围绕股权众筹的四大核心金融经济学命题展开实证：
1. **退出形态与高死亡率实证**：破产清算、低回报存续、并购退出与 IPO 的真实概率分布；
2. **风险投资幂律法则 (Power Law)**：检验极少数头部明星项目（Top 5%）对整体投资组合超额回报的决定性驱动；
3. **“专业领投人+大众跟投人”机制红利**：定量检验专业领投人入场对降低破产率、提升投资倍数的显著治理效应；
4. **中国法律与制度适应性**：分析《公司法》有限责任公司 50 人股东上限、有限合伙 SPV 代持及合格投资者（Accredited Investors）保护制度。

---

## 二、 目录结构

```text
07_equity_crowdfunding_analysis/
├── README.md                      # 项目说明与实证摘要
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── data/
│   ├── equity_crowdfunding_dataset.csv # 500家初创企业完整实证数据
│   └── data_dictionary.md         # 变量与指标说明
├── src/
│   ├── equity_data.py             # 股权众筹生命周期与幂律收益发生器
│   └── survival_analysis.py       # 投资组合收益率与领投人对比分析引擎
└── tests/
    └── run_equity_analysis.py     # 一键综合实证运行与报告导出
```

---

## 三、 快速上手与运行

直接运行综合实证套件：
```bash
python3 projects/07_equity_crowdfunding_analysis/tests/run_equity_analysis.py
```
你将看到：
- 500 个股权众筹样本在破产、存续、并购、IPO 四大维度的占比分布；
- 模拟等额组合总倍数与前 5% 头部项目收益集中度检验；
- “有领投人” vs “无领投人”在破产率（14.6% vs 26.1%）与回报倍数（11.1x vs 4.5x）上的悬殊差异；
- 对中国股权众筹制度变迁与散户投资者保护的深度启示。

---

## 四、 技术报告

完整学术实证研报见配套文档：[期末技术报告：股权众筹投后生存率、幂律回报特征与投资者保护机制研究 (report.md)](./report.md)。
