# 课题 02：比特币网络与共识模拟器 (Bitcoin Simulator)

> **对应 Gitee 课题**：`#IAU35E` 比特币模拟器(实践)  
> **项目定位**：分布式加密货币网络全生命周期仿真器，支持 UTXO 状态机、P2P 广播、竞争分叉与 51% 双花攻防  
> **环境要求**：Python 3.8+ (纯原生标准库，零外部依赖)

---

## 一、 系统架构与仿真特性

本项目旨在构建一个高拟真度、事件驱动的比特币网络与共识博弈仿真环境，核心包含五大子系统：

1. **账户与 UTXO 状态引擎** (`transaction.py`, `crypto_util.py`)
   - 钱包公私钥生成、Base58Check 地址编码；
   - 支持常规转账交易与 Coinbase 铸币交易；
   - 严格的同源 UTXO 双花校验与矿工费结算。
2. **区块与默克尔树 (Merkle Tree)** (`block.py`)
   - 80 字节区块头封装，自底向上两两配对哈希的 Merkle Root 计算；
   - 可配置难度的 PoW 挖矿哈希寻优。
3. **分叉重组与最长链共识 (Chain Reorg)** (`blockchain.py`)
   - 维护多分支区块树（Block Tree）；
   - 最长链法则（Longest-Chain Rule）；
   - **自动识别共同祖先、孤块回滚、交易放回 Mempool、新分支正向生效**的完整 Reorganization 逻辑。
4. **P2P 节点与 Mempool 交易池** (`node.py`)
   - 每个节点拥有独立存储、独立 Mempool 与独立主链视图；
   - Gossip 协议全网泛洪广播交易与区块。
5. **高阶网络攻防与博弈场景** (`network.py`)
   - 模拟网络分区导致的自然竞争分叉与重组；
   - 模拟 51% 算力优势下的私有链双花覆写攻击（还原为什么需要 6 次确认）。

---

## 二、 目录结构

```text
02_bitcoin_simulator/
├── README.md                      # 项目说明与快速启动指引
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── src/
│   ├── crypto_util.py             # Hash256, Hash160, Base58Check 与地址衍生
│   ├── transaction.py             # TxIn, TxOut, Transaction 与 Coinbase 模型
│   ├── block.py                   # 区块头、默克尔树计算与 PoW 挖矿实现
│   ├── blockchain.py              # 全局账本状态、UTXO 集与分叉重组 (Reorg) 引擎
│   ├── node.py                    # 独立 P2P 节点、Mempool 交易池与矿工
│   └── network.py                 # 全网拓扑仿真与高阶攻防场景编排
└── tests/
    ├── test_mining_and_reorg.py   # 竞争分叉自动重组单测
    ├── test_double_spend.py       # 内存池双花拦截与 51% 算力攻击单测
    └── run_simulation.py          # 综合全景交互式仿真运行器
```

---

## 三、 快速上手与运行

### 1. 一键运行全景网络仿真与攻防演练
```bash
python3 projects/02_bitcoin_simulator/tests/run_simulation.py
```
演示四个连续演化阶段：
- **阶段一**：4 个节点 P2P 全连通组网与创世区块同步；
- **阶段二**：Alice 挖矿获取 50 BTC，转账给 David，Bob 打包出块，余额与 Mempool 动态变动；
- **阶段三**：Alice 与 Bob 产生网络分叉，Alice 率先延长分支，Bob 自动执行 Reorg 收敛至最长主链；
- **阶段四**：Mallory 实施 51% 算力双花攻击，成功抹去商家 Charlie 的 30 BTC 确认款项。

### 2. 独立运行单元测试
```bash
# 验证竞争分叉与最长链重组
python3 projects/02_bitcoin_simulator/tests/test_mining_and_reorg.py

# 验证双花防御与 51% 攻击
python3 projects/02_bitcoin_simulator/tests/test_double_spend.py
```

---

## 四、 技术报告

完整学术报告与机制建模见配套文档：[期末技术报告：比特币分布式网络模拟与最长链共识实证 (report.md)](./report.md)。

