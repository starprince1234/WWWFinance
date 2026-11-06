# 课题 03：以太坊去中心化众筹 DAPP (Ethereum Crowdfunding DApp)

> **对应 Gitee 课题**：`#IKSCC2` [以太坊的众筹DAPP](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSCC2) (关联 issue `#IAUB4X`)  
> **指定参考项目**：[konicyQWQ/crowdfunding-dapp](https://github.com/konicyQWQ/crowdfunding-dapp) (浙江大学课程作业，Truffle + 众筹与资金使用投票)  
> **核心对照文档**：[需求与验证矩阵 (requirements_matrix.md)](./requirements_matrix.md) | [技术研报 (report.md)](./report.md)  
> **运行环境**：macOS (Darwin 24.3.0, arm64) | Node.js v24.22.0 | Ganache 7.9.2 | ethers 6.17.0 | solc 0.8.20 | Docker Client 29.8.2 (Daemon inactive)

---

## 一、 重要声明与原项目承接关系

1. **原指定项目 (konicyQWQ/crowdfunding-dapp)**：
   - 该项目为浙江大学区块链课程作业，基于早期的 Truffle 框架与 Solidity `<0.9.0` 构建，包含项目发起、支持者出资、资金使用申请（`Use`）及出资人投票表决的基础闭环。
2. **本实现的继承与现代工程升级**：
   - **智能合约重构**：采用现代生产级 **Solidity 0.8.20** 重新编写了 [`contracts/Crowdfunding.sol`](./contracts/Crowdfunding.sol)，引入自定义 Error 极致降低 Gas 消耗，增加 `ReentrancyGuard` 防重入攻击保护，并将资金使用表决升级为“按支持者出资权重进行 DAO 治理”（赞成权重超 50% 方准予执行拨付）；
   - **真实本地 EVM 闭环验证**：编写了原生 `solc` 编译器脚本与基于 **Ganache (ChainId: 1337) + ethers.js** 的端到端自动化测试，覆盖了项目创建、出资、时钟跃迁、DAO 投票、防重复刷票、里程碑划拨、流标退款与防重复退款的全生命周期，实测捕获真实交易哈希与 Gas 回执；
   - **前端真实性整改**：彻底修正了此前静态界面中盲目提示“交易已打包上链”的虚假描述，明确区分【离线沙盒演示模式】与【真实以太坊 Web3 模式】，修复了退款固定退 2 ETH 的模拟缺陷，依据用户真实出资账本进行精准退款；
   - **容器化支持**：在 [`docker/`](./docker/) 目录提供了 `Dockerfile` 与 `docker-compose.yml`，明确标注因宿主机 Docker 守护进程未启动，镜像构建处于待验证状态。

---

## 二、 目录结构

```text
03_ethereum_crowdfunding_dapp/
├── README.md                      # 项目快速使用与复现指南
├── requirements_matrix.md         # 详细需求对照表与真实 EVM 执行日志
├── report.md                      # 技术研报与智能合约安全审计
├── package.json                   # Node.js 依赖配置 (solc, ganache, ethers)
├── contracts/
│   └── Crowdfunding.sol           # Solidity 0.8.20 去中心化众筹与里程碑治理合约
├── scripts/
│   ├── compile.js                 # 原生 solc 编译脚本 (输出 build/Crowdfunding.json)
│   └── deploy_and_test_evm.js     # 真实本地 EVM (Ganache) 部署与合约交互测试套件
├── docker/
│   ├── Dockerfile                 # DApp 全栈容器化镜像构建文件
│   └── docker-compose.yml         # 多容器编排与健康检查配置
├── frontend/                      # 响应式 Web3 交互前端
│   ├── index.html                 # 前端视图 (包含沙盒/Web3运行模式横幅)
│   ├── app.js                     # 业务与交互逻辑 (无虚假上链提示，精准退款)
│   └── style.css                  # 现代化极光深色风格样式
├── src/
│   └── evm_simulator.py           # 教学扩展: 纯 Python 离散状态机仿真器
└── tests/
    ├── run_dapp_demo.py           # Python 状态机演示入口
    └── test_contracts.py          # Python 状态机断言测试
```

---

## 三、 快速复现与验证步骤

### 1. 编译智能合约 (真实 solc 0.8.20)
```bash
cd projects/03_ethereum_crowdfunding_dapp
node scripts/compile.js
```
**输出**：成功生成 `build/Crowdfunding.json`（包含 34 个 ABI 方法和 18,104 字符的 EVM 字节码）。

### 2. 运行真实本地 EVM 交互测试（推荐）
```bash
node scripts/deploy_and_test_evm.js
```
**实测结果说明**：
- 在本地测试链（ChainId: 1337）成功部署合约（地址: `0xE7c8BbC645eca103f45Efa86aDE64CBDadB92B0A`）；
- 成功执行项目创建（TxHash: `0x0b58...`, Gas: 210,614）；
- 支持者出资 6 ETH + 5 ETH 成功达成目标，合约留存 11 ETH；
- 快进 EVM 时钟 7 天，创建 4 ETH 采购里程碑，Backer 1 以 6 ETH 出资权重投票赞成（Gas: 73,777）；
- 再次投票被智能合约自动拦截（`AlreadyVoted()` 回滚，PASS）；
- 执行里程碑提款，供应商账户实收到账 4.0 ETH（TxHash: `0x4488...`）；
- 测试项目 #2 流标全额退款，Backer 3 成功取回 2.0 ETH，再次调用退款被拦截（`NothingToRefund()`，PASS）。

### 3. 打开前端交互页面
在浏览器中打开 [`frontend/index.html`](./frontend/index.html)。  
界面顶部明确显示当前为【离线沙盒演示模式】；若检测到并连接 MetaMask 插件，则切换为【真实 Web3 模式】。

### 4. 容器化镜像构建（若宿主机已启动 Docker）
```bash
docker compose -f projects/03_ethereum_crowdfunding_dapp/docker/docker-compose.yml build
docker compose -f projects/03_ethereum_crowdfunding_dapp/docker/docker-compose.yml up -d
```
*(注：若本地 Docker 守护进程未启动，该命令将无法连接套接字，需待宿主服务开启后运行。)*

---

## 四、 研报与学术分析

详细智能合约形式化安全设计与去中心化治理分析见配套研报：[`report.md`](./report.md)。
