# 课题 06：众筹跨平台对比研究 (Kickstarter vs Indiegogo vs 摩点)

> **对应 Gitee 课题**：`#IASP1B` [众筹 Kickstarter Indiegogo 摩点](https://gitee.com/NIMUESCU/WWWFinance/issues/IASP1B)  
> **核心研究对象**：[Kickstarter](https://www.kickstarter.com/) (美), [Indiegogo](https://www.indiegogo.com/) (美), [摩点 Modian](https://www.modian.com/) (中)  
> **核心对照文档**：[需求与验证矩阵 (requirements_matrix.md)](./requirements_matrix.md) | [技术研报 (report.md)](./report.md)  
> **运行环境**：macOS (Darwin 24.3.0, arm64) | Python 3.9.6 | pandas 2.3.3

---

## 一、 老师 Issue 核心问题直面解答

### 1. 为什么“众筹是一种融资方式，不是平台的盈利模式”？
- **众筹本身是项目发起人（创作者/企业）的一种直接融资手段**：通过互联网向广泛公众汇聚小额资金以启动项目，替代传统银行借贷或风险投资；
- **平台的盈利模式是作为中介机构的商业变现架构**：平台不占有项目本金，其盈利来自交易撮合的服务费佣金（5%–6%）、支付结算返点以及增值服务费（代运营推广、众筹后转电商零售供应链等）。绝不能将平台经营性收入与项目募集的资本混同。

### 2. “众筹项目一定要有回报吗？”
- **不一定**。这取决于众筹的具体模式分类：
  - **捐赠众筹 (Donation)**：如腾讯公益、GoFundMe，提供的是**非经济性/象征性回报**（电子感谢信、救助反馈、利他心理满足感），无实质物质或经济对价；
  - **奖励众筹 (Reward)**：如 Kickstarter、摩点，提供的是实物产品或特权衍生对价；
  - **借贷众筹 (Lending)**：提供的是还本付息的固定收益；
  - **股权众筹 (Equity)**：提供的是初创企业的所有权份额与未来分红。

---

## 二、 三大主流平台现行规则与费率全景对比 (2026 最新官方核验)

| 平台名称 | 筹资模式机制 | 平台服务费 | 支付处理与清算通道费 | 是否达标才扣款？ |
| :--- | :--- | :---: | :--- | :--- |
| **Kickstarter** | **纯 All-or-Nothing (全有或全无)** | 5% | Stripe: 3% + $0.20 / 笔 | **是**。未达标不收平台费，支持者零扣款。 |
| **Indiegogo** | **双轨制 (Fixed 或 Flexible)** | 5% | 2.9% + $0.30 / 笔 | Fixed 达标才扣；**Flexible 无论是否达标均扣款划拨**。 |
| **摩点 (Modian)** | **全有或全无 (为主)** | 6% 综合服务费 | 微信支付 / 支付宝直接集成 | **是**。未达标系统自动原路全额退还支持者。 |

---

## 三、 目录结构与快速复现

```text
06_crowdfunding_cross_platform/
├── README.md                      # 项目快速使用与复现指南
├── requirements_matrix.md         # 详细问题直答、官方规则核验与数据说明
├── report.md                      # 技术研报与中美众筹制度比较
├── data/
│   └── cross_platform_dataset.csv # 跨平台机制教学模拟数据集 (750条)
├── src/
│   ├── dataset_builder.py         # 跨平台机制模拟数据构建器 (明确标注为教学仿真)
│   └── comparator.py              # 机制对比与费用摩擦测算引擎
└── tests/
    └── run_cross_platform_analysis.py # 综合比较演示入口
```

### 快速运行机制对比模拟
```bash
python3 projects/06_crowdfunding_cross_platform/tests/run_cross_platform_analysis.py
```
*(注：该脚本基于 750 条算法模拟样本演示固定筹资 vs 灵活筹资的协调博弈，以及国内移动支付 ~1% 对比欧美 Stripe ~3% 的支付基础设施红利。)*
