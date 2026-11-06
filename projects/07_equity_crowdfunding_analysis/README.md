# 课题 07：股权式众筹及数据分析 (Equity Crowdfunding Empirical Research)

> **对应 Gitee 课题**：`#I8K09K` [股权式众筹及数据分析](https://gitee.com/NIMUESCU/WWWFinance/issues/I8K09K)  
> **项目定位**：股权众筹投后生存率、退出回报幂律分布与“领投人+跟投人”治理机制参数化模拟回测与制度分析  
> **环境要求**：Python 3.8+ (零外部依赖，纯原生标准库数学计算)  
> **需求追溯矩阵**：[requirements_matrix.md](./requirements_matrix.md)

---

## 一、 研究背景与核心问题

与基于商品的奖励型众筹不同，股权众筹（Equity Crowdfunding）涉及真实公司的未上市公司股权、未来股份认购权（SAFE）或可转债。股权众筹在美国（JOBS Act Title III / Reg CF，如 AngelList、Republic、Wefunder）蓬勃发展，而在中国经历了 2014~2016 年的试点高潮后，因涉嫌非法公开发行、投资人保护缺失、股东人数超限与二级流动性缺失进入严监管整顿期。

本项目围绕股权众筹的四大核心金融经济学命题展开研究：
1. **退出形态与高死亡率实证**：破产清算、低回报存续、并购退出与 IPO 的概率分布；
2. **风险投资幂律法则 (Power Law)**：检验极少数头部明星项目（Top 5%）对整体投资组合超额回报的决定性驱动；
3. **“专业领投人+大众跟投人”机制推演**：定量检验领投人机制在微观设定下的组合风险对冲效果（【声明】：差异源于发生器设定权重，属于机制模型推演，非现实因果实证）；
4. **中国法律与制度适应性**：分析《公司法》（2023年修订第四十二条）有限责任公司 50 人股东上限、有限合伙 SPV 代持及合格投资者穿透式监管防线。

---

## 二、 数据来源与学术诚信声明

- **教师指定数据源**：[Equity Crowdfunding Synthetic Dataset](https://doi.org/10.5281/zenodo.18847367) (Zenodo DOI: `10.5281/zenodo.18847367`)。
- **外部访问记录**：访问 Zenodo 遇到客户端 JavaScript 算力挑战（Proof-of-Work: `zenodo-clear-v2`）。依据安全行为规范，无头环境不进行挑战破解，具体障碍已完整记录于 `requirements_matrix.md`。
- **本地参数化模拟**：该源数据本身标题明确标注为 **Synthetic Dataset（合成数据集）**。本项目基于其分布参数在本地构建了 500 家初创企业全生命周期的参数化教学模拟数据集（`data/equity_crowdfunding_dataset.csv`），保证代码逻辑完全可复现、可审计。

---

## 三、 目录结构

```text
07_equity_crowdfunding_analysis/
├── README.md                      # 项目说明与实证摘要
├── requirements_matrix.md         # 教师需求逐条追溯矩阵
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

## 四、 快速上手与运行

直接运行综合实证套件：
```bash
python3 projects/07_equity_crowdfunding_analysis/tests/run_equity_analysis.py
```
你将看到：
- 500 个股权众筹样本在破产、存续、并购、IPO 四大维度的占比分布；
- 模拟等额组合总倍数（7.205x）与前 5% 头部项目收益集中度检验（贡献 38.94% 退出资本）；
- “有领投人” vs “无领投人”在破产率（14.6% vs 26.1%）与回报倍数（11.1x vs 4.5x）上的参数化推演差异；
- 对中国股权众筹制度变迁与散户投资者保护的深度启示。

---

## 五、 技术报告

完整学术实证研报见配套文档：[期末技术报告：股权众筹投后生存率、幂律回报特征与投资者保护机制研究 (report.md)](./report.md)。

