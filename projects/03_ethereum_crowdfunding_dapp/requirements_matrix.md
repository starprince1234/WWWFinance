# 课题 03：需求与对照矩阵 (Requirements & Verification Matrix)

> **对应 Gitee 课题**：`#IKSCC2` [以太坊的众筹DAPP](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSCC2) (关联 issue `#IAUB4X`)  
> **指定原项目**：[konicyQWQ/crowdfunding-dapp](https://github.com/konicyQWQ/crowdfunding-dapp) (浙大作业，Truffle + Solidity 众筹与资金使用请求投票架构)  
> **审计日期**：2026-11-05  
> **运行环境**：macOS (Darwin 24.3.0, arm64) | Node.js v24.22.0 | Ganache 7.9.2 | ethers 6.17.0 | solc 0.8.20 | Docker Client 29.8.2 (Daemon inactive)

---

## 一、 需求对照表

| 序号 | 老师 Issue 原文要求 | 对应官方/原始来源 | 本地实现与现状证据 | 运行/复现命令 | 实测结果与状态 | 局限性与外部阻碍说明 |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **REQ-1** | 在仿真环境上运行 | `https://github.com/konicyQWQ/crowdfunding-dapp`<br>(原作业基于 Truffle + Ganache 仿真链) | 1. `contracts/Crowdfunding.sol`: 采用现代化 Solidity 0.8.20 编写去中心化众筹合约；<br>2. `scripts/compile.js`: 原生 solc 编译生成 ABI 与 Bytecode；<br>3. `scripts/deploy_and_test_evm.js`: 基于 Ganache 真实本地 EVM 完成发布、出资、里程碑DAO投票、划拨与退款全生命周期测试；<br>4. 保留 `src/evm_simulator.py` 作为纯 Python 教学状态机扩展 | `cd projects/03_ethereum_crowdfunding_dapp && node scripts/deploy_and_test_evm.js` | **[已验证 √ (真实本地EVM链交互通过)]** | 严格采用真实 EVM (Ganache ChainId 1337) 提交交易并捕获真实交易哈希与 Gas 回执；Python 状态机仅作为离线教学扩展，不在报告中冒充 EVM。 |
| **REQ-2** | 打包成 Docker 镜像 | Issue 文本明确要求 | 编写了完整的容器化配置：`docker/Dockerfile` 与 `docker/docker-compose.yml` (打包 Node.js 20、Ganache 节点、合约编译与 HTTP 前端服务，包含健康检查) | `docker compose -f projects/03_ethereum_crowdfunding_dapp/docker/docker-compose.yml build` | **[已实现未验证 (待宿主启动Docker)]** | **精确阻碍**：当前宿主机 macOS ARM64 上的 Docker 守护进程未启动；配置已完备就绪，但如实标记镜像处于“未在当前无 Docker 环境的宿主机上执行构建验证”，严禁虚构 Docker 运行证据。 |
| **REQ-3** | 如果有想法，自行修改 | Issue 文本明确要求 | 1. **里程碑治理防卷款跑路机制**：将原版简单的赞成票升级为按支持者出资额加权投票（出资权重超过 50% 多数同意才准予提款）；<br>2. **ReentrancyGuard 防重入锁**与自定义 Error Gas 优化；<br>3. **前端沙盒与 Web3 双模式彻底解耦**：彻底撤销了原先静态 localStorage 模拟中的虚假“交易打包上链”提示，明确标注“离线沙盒模式”，真实计算用户已出资额并在流标时精准原路全额退还。 | 打开 `frontend/index.html` 浏览器预览交互 | **[已验证 √]** | 前端界面增加了醒目的沙盒/真实模式横幅状态条，消除了固定加 2 ETH 的硬编码退款错误。 |

---

## 二、 核心业务关键路径真实 EVM 验证证据

| 业务场景 | 交易发起方 | EVM 动作与验证断言 | 实测交易哈希 / 状态 | Gas Used | 验证状态 |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **合约部署** | Deployer (`0xC12c...`) | 部署 `DecentralizedCrowdfund` | 合约地址: `0x08529933Ca57D8bD3c72D7F84e4814A5c7Ab823E` | 1,842,501 | PASS |
| **创建众筹项目** | Creator (`0x3341...`) | 发起项目 #1（目标 10 ETH，时长 7 天） | Tx: `0xee7f8c65b7823ead6b7021be8f0b905c4af497d0abbb7040075e26815501b244` | 210,614 | PASS |
| **支持者出资 1** | Backer 1 (`0xA95C...`) | 出资 6.0 ETH | Tx: `0x50227a1146d5f3901670763f4982da448be3766f7747f1103231543fd0062bdb` | 118,058 | PASS |
| **支持者出资 2** | Backer 2 (`0x5B7d...`) | 出资 5.0 ETH（项目累计 11 ETH，达成目标） | Tx: `0x1d6f0970f59a7ed6f990685f19e4ae8d76ba8f166efcfd7092207e577e2e16bd` | 66,758 | PASS |
| **提交里程碑 1** | Creator | 申请向供应商采购 4.0 ETH | Tx: `0x9badf06c69514f9a49ea186006a7f43c92ace644e4608a8db9126196ca5b3374` | 176,652 | PASS |
| **里程碑加权投票** | Backer 1 | 投赞成票（出资权重 6.0 ETH，占比 54.5% > 50%） | Tx: `0xbec64d1aae29679e26bd30e21bb4d0e0a3b1a2bd33bdbbec1f41bd22601f909c` | 73,777 | PASS |
| **防重复投票拦截** | Backer 1 | 再次尝试对同一里程碑投票 | 合约抛出 `AlreadyVoted()` 错误，交易被 EVM 强力回滚 | 0 (Reverted) | PASS |
| **里程碑拨款执行** | Creator | 触发划拨 4.0 ETH 至供应商 Vendor | Tx: `0x44887489b8391b13e7e904de6c1daf078a11bb3cb3baee27c3f9d1c9fa181ab2` | 48,210 | PASS |
| **流标退款** | Backer 3 | 项目 #2 筹集 2 ETH 未达 10 ETH 门槛，截止后申请全额退款 | Tx: `0x22d93cb8fe9ce1f125cfa607717e806af5c9a5a492be5ea18195a41e45006b91` | 42,372 | PASS |
| **防重复退款拦截** | Backer 3 | 再次尝试调用退款 | 合约抛出 `NothingToRefund()` 错误，交易被 EVM 回滚 | 0 (Reverted) | PASS |

