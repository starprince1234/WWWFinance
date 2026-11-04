# 课题 03：以太坊去中心化众筹 DAPP (EtherCrowd)

> **对应 Gitee 课题**：`#IKSCC2` 以太坊的众筹DAPP  
> **项目定位**：基于 Solidity 0.8.20 + Web3 前端构建的去中心化众筹应用，具备条件退款与里程碑 DAO 治理防卷款跑路机制  
> **环境要求**：支持主流现代浏览器，内置 EVM 仿真测试套件 (零环境配置障碍)

---

## 一、 系统创新与核心架构

传统众筹平台（如 Kickstarter、Indiegogo、国内摩点）存在高额平台抽成（5%~8%）、中心化资金托管风险以及“发起人达标后卷款跑路、项目延期烂尾”等信任顽疾。

本项目结合以太坊智能合约与去中心化自治组织（DAO）理念，设计了 **EtherCrowd DAPP**：
1. **智能合约原生托管 (`contracts/Crowdfunding.sol`)**
   - **All-or-Nothing 承诺模式**：仅当在规定时间截点前达到预设目标金额时，资金才允许被结算；若未达成，支持者可一键调用 `refund()` 提取全额本金；
   - **防重入攻击保护 (Checks-Effects-Interactions & nonReentrant Guard)**；
   - **Gas 优化**：使用 Solidity 0.8 自定义错误（Custom Errors）代替高昂的 `require` 字符串。
2. **里程碑治理防跑路机制 (Milestone DAO Governance)**
   - 筹资成功后，发起人不能一次性卷走资金；
   - 必须按研发阶段提交用款申请（描述、金额、供应商地址）；
   - 出资人按出资比例持有加权投票权，仅当**赞成票超过 50%** 时，智能合约才执行原子划拨。
3. **现代化 Web3 前端界面 (`frontend/`)**
   - 玻璃拟物化暗黑系现代 UI；
   - 支持 MetaMask 真实钱包与沙盒沙盘双模交互。
4. **全功能 EVM 测试仿真套件 (`src/evm_simulator.py`)**
   - 原生 Python 模拟智能合约状态转移与时间步进，便于评阅老师与无 Node.js 环境的学生一键验证。

---

## 二、 目录结构

```text
03_ethereum_crowdfunding_dapp/
├── README.md                      # 项目说明文档
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── contracts/
│   └── Crowdfunding.sol           # 生产级 Solidity 0.8.20 智能合约源码
├── frontend/
│   ├── index.html                 # Web3 交互式单页应用
│   ├── style.css                  # 现代化 UI 样式表
│   └── app.js                     # 钱包连接、合约交互与状态管理
├── src/
│   └── evm_simulator.py           # EVM 状态机模拟器 (Python 实现)
└── tests/
    ├── test_contracts.py          # 智能合约核心逻辑回归单测
    └── run_dapp_demo.py           # 综合演示与本地 Web 服务指引
```

---

## 三、 快速上手与运行

### 1. 运行智能合约核心测试
```bash
python3 projects/03_ethereum_crowdfunding_dapp/tests/run_dapp_demo.py
```

### 2. 打开前端 Web3 界面进行可视化操作
可在浏览器中直接访问本地静态页面：
```text
file:///Users/adw/Developer/projects/wwwfinance/projects/03_ethereum_crowdfunding_dapp/frontend/index.html
```
或者启动本地测试服务器：
```bash
python3 -m http.server --directory projects/03_ethereum_crowdfunding_dapp/frontend 8080
```
访问 `http://localhost:8080` 即可体验出资、撤资、退款与里程碑投票！

---

## 四、 技术报告

完整学术报告见配套文档：[期末技术报告：以太坊去中心化众筹智能合约设计与 DAO 治理实证 (report.md)](./report.md)。
