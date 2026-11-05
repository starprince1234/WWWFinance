# 课题 06：中美主流众筹平台对比研究 (Kickstarter vs Indiegogo vs 摩点)

> **对应 Gitee 课题**：`#IASP1B` 众筹 Kickstarter Indiegogo 摩点  
> **项目定位**：全球三大多元化众筹平台的制度设计、机制博弈（Fixed vs Flexible）、费率摩擦与 750 项目跨平台大数据实证研究  
> **环境要求**：Python 3.8+ (零外部依赖，纯原生标准库实现)

---

## 一、 研究背景与平台图谱

本课题针对全球最具代表性的三家奖励型众筹平台展开系统性对比：
1. **Kickstarter (美国)**：全球最大、最经典的众筹平台，严格贯彻 **All-or-Nothing (全有或全无)** 准则，科技硬件与先锋设计引领全球；
2. **Indiegogo (美国)**：开放 **Flexible Funding (Keep-it-All)** 与 InDemand 模式，允许项目即使未达标也能提现，成为晚期硬件预售的重要阵地；
3. **摩点 Modian (中国)**：依托中国文创、二次元 ACG、桌游与文化出版垂直生态，深度融入微信/支付宝移动支付基础设施，形成高粘性社群众筹典范。

---

## 二、 目录结构

```text
06_crowdfunding_cross_platform/
├── README.md                      # 项目说明与核心发现
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── data/
│   ├── cross_platform_dataset.csv # 750个项目跨平台标准化实证数据
│   └── platform_metrics_summary.json # 汇总指标明细
├── src/
│   ├── dataset_builder.py         # 多源数据标准化与汇率对齐构建器
│   └── comparator.py              # 跨平台机制比对与费率统计分析引擎
└── tests/
    └── run_cross_platform_analysis.py # 一键综合实证运行与分析报告导出
```

---

## 三、 快速上手与运行

直接运行跨平台综合实证套件：
```bash
python3 projects/06_crowdfunding_cross_platform/tests/run_cross_platform_analysis.py
```
你将看到：
- 三大平台的样本规模、成功达标率、平均目标、客单价与强势品类横向对比；
- Fixed (All-or-Nothing) 与 Flexible (Keep-it-All) 机制的达标率与支持者信任博弈数据；
- 中美众筹平台在底层支付费率与综合摩擦成本上的定量拆解。

---

## 四、 技术报告

完整学术实证研报见配套文档：[期末技术报告：中美众筹平台制度变迁、机制博弈与商业生态实证研究 (report.md)](./report.md)。

