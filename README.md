# 互联网金融 （Internet Finance）

## 简介

- 学分：2分
- 学时：16
- 形式：考查，期末报告

金融是管理与研究钱和投资的学问。互联网金融是互联网技术与金融技术的结合。

互联网金融是指以依托于支付、云计算、社交网络以及搜索引擎等互联网工具，实现资金融通、支付和信息中介等业务的一种新兴金融。

本课程以互联网技术为导向，在此基础上讲述资金融通，支付，投资和信息服务等新型金融业务模式，涉及第三方支付，数字货币，区块链，大数据金融等。

**附：** 互联网金融专业开设课程（大致列举）：《金融学》《互联网金融学》《国际金融学》《证券投资学》《大数据金融》《公司金融》《互联网金融风险控制》《“互联网＋”思维与应用》《电子支付与网络银行》《互联网技术》《商业银行业务与经营》《个人理财》《金融工程学》《互联网金融营销》《互联网金融法律与实务》等。

## Introduction

- Score: 2
- Period: 16
- Eval: Tech Report

Finance is a term for the management, creation, and study of money and investments. 

Internet finance is a new type of financial business model. The main business models of internet finance include internet payment, online lending, equity crowdfunding, internet fund sales, internet insurance, internet trust, and internet consumer finance.

Internet finance refers to the new business model of utilizing the Internet and information communication technologies to accomplish a wide range of financial activities, such as third-party payment, online lending, direct sales of funds, crowdfunding, online insurance, and banking.

---

## 实践项目研发矩阵 (Research & Project Matrix)

本项目库针对课程 8 大核心课题展开逐一攻坚与学术诚信整改，包含可复现工程、独立测试套件、详尽需求矩阵与期末学术技术报告：

| 编号 | 课题名称 | Gitee Issue | 模块目录 | 核心成果与整改核验 | 状态 |
| :---: | :--- | :--- :---: | :--- | :--- | :---: |
| **01** | **比特币的原始代码实践** | `#IKSCT7` | [`01_bitcoin_original_code`](./projects/01_bitcoin_original_code/) | 官方原版 32 位 C++ 容器配方 + Python 原理复现引擎 + 创世块与脚本单步验证 | **[已验证 √]** |
| **02** | **比特币模拟器 (实践)** | `#IAU35E` | [`02_bitcoin_simulator`](./projects/02_bitcoin_simulator/) | Arthur Gervais 原版 ns-3 容器方案 + Python 状态机仿真器 (LCA重组/双花/51%攻击) | **[已验证 √]** |
| **03** | **以太坊的众筹 DAPP** | `#IKSCC2` | [`03_ethereum_crowdfunding_dapp`](./projects/03_ethereum_crowdfunding_dapp/) | 真实本地 EVM (Ganache+Ethers.js) 链上交易部署测试 + 前端沙盒/Web3双模式 + Docker | **[已验证 √]** |
| **04** | **开发众筹平台 (工作量大)** | `#IKSC4Z` | [`04_crowdfunding_platform`](./projects/04_crowdfunding_platform/) | Sahem 原著学位论文 UML 对照 + 事务原子性清结算 + 幂等性与资金守恒测试 | **[已验证 √]** |
| **05** | **众筹书籍的数据分析** | `#IKSANG` | [`05_crowdfunding_books_analysis`](./projects/05_crowdfunding_books_analysis/) | 原著 1,000 教学样本独立重算与勘误 (修复DIV/0) + 12区间目标统计 + 600参数化计量回测 | **[已验证 √]** |
| **06** | **众筹 Kickstarter Indiegogo 摩点** | `#IASP1B` | [`06_crowdfunding_cross_platform`](./projects/06_crowdfunding_cross_platform/) | 教师两问深析 (融资方式vs盈利模式/回报界定) + 750 参数化机制博弈 + 官方费率基建核验 | **[已验证 √]** |
| **07** | **股权式众筹及数据分析** | `#I8K09K` | [`07_equity_crowdfunding_analysis`](./projects/07_equity_crowdfunding_analysis/) | Zenodo 2026 合成数据集比对 + 500参数化生存模拟 (纠正循环论证) + 新公司法42条制度剖析 | **[已验证 √]** |
| **08** | **众筹叙事的专业合规性 (难)** | `#IKSBTX` | [`08_crowdfunding_compliance`](./projects/08_crowdfunding_compliance/) | LREC 2026 论文 LegitimNarrate 解构 + 最高法非吸四要件信号初筛 + 黄金叙事解答 | **[已验证 √]** |

---

## 快速复现与验证 (Quick Start)

所有 8 个攻坚项目均配有独立的自动化测试套件与可溯源数据，均可在本地环境独立运行复现：

```bash
# 1. 验证中本聪 v0.1 创世区块哈希计算、Forth 脚本逆向与 IRC 节点发现
python3 projects/01_bitcoin_original_code/tests/run_all_experiments.py

# 2. 验证比特币状态机仿真器、最长链分叉重组与 51% 双花攻击
python3 projects/02_bitcoin_simulator/tests/run_simulation.py
python3 projects/02_bitcoin_simulator/tests/test_double_spend.py
python3 projects/02_bitcoin_simulator/tests/test_mining_and_reorg.py

# 3. 验证以太坊众筹智能合约在真实 EVM (Ganache) 上的部署、出资、里程碑投票与退款
node projects/03_ethereum_crowdfunding_dapp/scripts/deploy_and_test_evm.js

# 4. 验证众筹平台业务接口、事务原子性清结算、双重结算幂等性与资金守恒
python3 projects/04_crowdfunding_platform/tests/test_api.py

# 5. 验证原版 1,000 教学样本 Excel 勘误统计与 600 样本参数化计量回归
python3 projects/05_crowdfunding_books_analysis/src/analyze_original_workbook.py
python3 projects/05_crowdfunding_books_analysis/tests/run_analysis.py

# 6. 验证 Kickstarter vs Indiegogo vs 摩点跨平台机制博弈与费率模拟
python3 projects/06_crowdfunding_cross_platform/tests/run_cross_platform_analysis.py

# 7. 验证股权众筹 500 轮样本退出形态、幂律收益集中度与领投人机制参数化推演
python3 projects/07_equity_crowdfunding_analysis/tests/run_equity_analysis.py

# 8. 验证众筹文案合规初筛信号引擎、司法案例模拟与文案重构
python3 projects/08_crowdfunding_compliance/tests/test_compliance.py
python3 projects/08_crowdfunding_compliance/tests/run_compliance_audit.py
```

---

## 课程前沿演进与反向建议 (Course Evolution & Proverse Proposals)

> 响应胡老师关于**“如果有个人想法内容，看到有趣的东西，可以反向给我建议”**的教学倡议，结合 2024–2026 年金融科技（FinTech）学术界与工业界的前沿演进，本仓库提出以下 4 个拓展方向建议：

### 1. 预测市场与信息金融（Prediction Markets & Information Finance）
- **学术内涵**：从“众筹资金”跨越至“众筹真相（Crowdsourcing Truth）”。以 Polymarket 为代表的预测市场通过市场化定价机制汇聚分布式私人信息。
- **实验设计**：对比恒定乘积做市商（CPMM）与对数市场评分规则（LMSR）在二元期权价格发现中的流动性深度；分析乐观预言机（UMA）在博弈论仲裁中的谢林点（Schelling Point）稳健性。

### 2. AI Agent 金融自主经济体与微支付（Autonomous Economic Agents & ERC-4337）
- **学术内涵**：将大模型从“编码辅助工具”升级为“金融市场博弈参与者”。
- **实验设计**：依托 ERC-4337 账户抽象赋予 AI Agent 独立链上钱包，模拟在流动性极端枯竭下多 Agent 的跨协议套利与动态清算；探索基于 HTTP 402（Payment Required）与闪电网络的机器对机器（M2M）毫秒级微支付流结算。

### 3. 真实世界资产代币化与合规 STO（Real-World Assets & Regulatory STO）
- **学术内涵**：破解传统股权众筹的 50 人股东上限与流动性匮乏困境，同时规避非法集资刑事红线。
- **实验设计**：对接香港虚拟资产新规与内地数智资产收益权凭证，设计带有 KYC/AML 白名单限制的合规代币化合约（ERC-3643）；模拟破产隔离 SPV 架构下绿色新能源电站资产未来现金流的自动穿透式分红。

### 4. 零知识证明在隐私金融与信用评级中的应用（Privacy-Preserving FICO）
- **学术内涵**：破解金融大数据风控中“数据要素融通与个人隐私保护”的二律背反。
- **实验设计**：基于 zk-SNARKs 构建链上信用凭证，实现“在不泄露个人具体银行流水与资产明细的前提下，向出借方数学化证明借款人具备充分偿债能力（如年收入 > 50 万且无违约记录）”。


