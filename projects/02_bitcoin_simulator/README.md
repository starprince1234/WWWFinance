# 课题 02：比特币模拟器实践 (Bitcoin Simulator Practice)

> **对应 Gitee 课题**：`#IAU35E` [比特币模拟器（实践）](https://gitee.com/NIMUESCU/WWWFinance/issues/IAU35E)  
> **指定原项目**：[arthurgervais/Bitcoin-Simulator](https://github.com/arthurgervais/Bitcoin-Simulator) (ACM CCS 2016 论文) | [官网指南](https://arthurgervais.github.io/Bitcoin-Simulator/)  
> **核心对照文档**：[需求与验证矩阵 (requirements_matrix.md)](./requirements_matrix.md) | [技术研报 (report.md)](./report.md)  
> **当前宿主环境**：macOS (Darwin 24.3.0, arm64) | Python 3.9.6 | Docker Client 29.8.2 (Daemon inactive)

---

## 一、 重要声明与实施边界界定

1. **原论文指定工具 (Arthur Gervais et al. ns-3 Bitcoin-Simulator)**：
   - 该项目为发表于 ACM CCS 2016 的权威学术论文 *On the Security and Performance of Proof of Work Blockchains* 的开源仿真框架，基于 Network Simulator 3 (ns-3.25) 与 RapidJSON；
   - **环境限制与阻碍**：ns-3.25 的构建依赖 Python 2.7 与旧版 GCC 4.8/5.x。当前宿主机为 Apple Silicon ARM64 架构且 Docker 守护进程未启动。我们在 [`docker/Dockerfile`](./docker/Dockerfile) 中提供了基于 x86_64 Ubuntu 16.04 的容器化复现配方，如实标记为“待宿主环境支持后验证”，绝不将自建 Python 结果冒充 ns-3 数据包级模拟输出。
2. **本地 Python 算法状态机模拟器 (Python Educational State Machine Simulator)**：
   - 采用纯 Python 原生标准库，专注于比特币**共识层与账本状态机逻辑**的微观复现：包括基于 UTXO 模型的双花交易拦截、多节点竞争出块、基于最近公共祖先 (LCA) 的最长链分叉自动回滚与重组，以及 51% 算力私有链双花反转。

---

## 二、 目录结构

```text
02_bitcoin_simulator/
├── README.md                      # 项目快速使用与复现指南
├── requirements_matrix.md         # 详细需求对照表与验证状态
├── report.md                      # 技术研报与 ns-3 vs Python 对比分析
├── docker/                        # ns-3 原版模拟器 Docker 构建配方
│   └── Dockerfile                 # 基于 Ubuntu 16.04 x86_64 的容器化环境
├── src/                           # Python 事件驱动状态机与共识核心
│   ├── block.py                   # 区块结构定义、区块头序列化与 Merkle 计算
│   ├── blockchain.py              # 区块链账本状态维护、最长链选择与 LCA 重组逻辑
│   ├── crypto_util.py             # 双 SHA-256 哈希工具
│   ├── network.py                 # P2P 网络拓扑、消息路由与广播队列
│   ├── node.py                    # 独立节点行为建模 (挖矿、交易池维护、区块校验)
│   └── transaction.py             # UTXO 交易输入输出结构与验证
└── tests/
    ├── run_simulation.py          # 综合仿真集成演示 (常规出块、分叉重组与51%攻击)
    ├── test_double_spend.py       # 内存池及 51% 双花拦截测试
    └── test_mining_and_reorg.py   # 链分叉自动重组与账本一致性测试
```

---

## 三、 快速复现与验证步骤

### 1. 一键运行 Python 模拟器实验（推荐）
在项目根目录执行：
```bash
python3 projects/02_bitcoin_simulator/tests/run_simulation.py
```
**实测结果说明**：
- **阶段一（组网）**：成功组建 4 节点 P2P 网络（Alice, Bob, Charlie, David），创世区块高度对齐为 #0；
- **阶段二（交易与出块）**：Alice 获得 50 BTC 挖矿奖励后向 David 转账 15 BTC（找零 35 BTC），Bob 打包出块，David 确认到账 15 BTC，系统总货币恒等量守恒（100 BTC）；
- **阶段三（分叉重组）**：Alice 与 Bob 天然竞争分叉各自出块 #3A 与 #3B，随后 Alice 率先挖出更高高度 #4A 并广播，Bob 节点成功检测到长链分支，触发 LCA 回滚孤儿块并对齐 Alice 主链；
- **阶段四（51% 攻击）**：攻击者拥有 51% 算力私下构造秘密长链，在商家 Charlie 确认 30 BTC 货款后突然广播私有链，全网主链被覆写，Charlie 账户货款蒸发，双花攻击成功复现。

### 2. 独立单元测试
```bash
# 验证 Mempool 与 51% 双花拦截
python3 projects/02_bitcoin_simulator/tests/test_double_spend.py

# 验证多节点竞争出块与最长链分叉重组
python3 projects/02_bitcoin_simulator/tests/test_mining_and_reorg.py
```

### 3. ns-3 原版模拟器构建（若宿主机已启动 Docker）
```bash
docker build -t bitcoin-sim-ns3 projects/02_bitcoin_simulator/docker/
docker run -it --rm bitcoin-sim-ns3 /bin/bash
```
*(注：若本地 Docker 守护进程未启动，此命令将报错，需等待宿主 Docker 服务开启后复验。)*

---

## 四、 研报与学术分析

详细系统设计与两代模拟器的学术深度对比见配套研报：[`report.md`](./report.md)。
