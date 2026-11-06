# 课题 02：需求与对照矩阵 (Requirements & Verification Matrix)

> **对应 Gitee 课题**：`#IAU35E` [比特币模拟器（实践）](https://gitee.com/NIMUESCU/WWWFinance/issues/IAU35E)  
> **指定原项目**：[arthurgervais/Bitcoin-Simulator](https://github.com/arthurgervais/Bitcoin-Simulator) (ACM CCS 2016 论文) | [官网指南](https://arthurgervais.github.io/Bitcoin-Simulator/)  
> **审计日期**：2026-11-05  
> **运行环境**：macOS (Darwin 24.3.0, arm64) | Python 3.9.6 | Docker Client 29.8.2 (Daemon inactive)

---

## 一、 需求对照表

| 序号 | 老师 Issue 原文要求 | 对应官方/原始来源 | 本地实现与现状证据 | 运行/复现命令 | 实测结果与状态 | 局限性与外部阻碍说明 |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **REQ-1** | 实践 Arthur Gervais 的 Bitcoin-Simulator (基于 ns-3 网络模拟器) | `https://github.com/arthurgervais/Bitcoin-Simulator`<br>论文: *On the Security and Performance of Proof of Work Blockchains* (CCS'16) | 编写了专用 Ubuntu 16.04 构建配置：`docker/Dockerfile` (基于 ns-3.25 与 RapidJSON) | `docker build -t bitcoin-sim-ns3 docker/` | **[被阻碍 / 待宿主环境验证]** | **精确阻碍**：当前宿主机为 Apple Silicon ARM64，且 Docker 守护进程处于关闭状态；ns-3.25 构建工具 `waf` 强依赖 Python 2.7 语法及旧版 GCC 4.8-5，在现代 ARM64 macOS 原生环境编译会遭遇 Python 3 不兼容与 Clang C++ 废弃语法报错。 |
| **REQ-2** | 尝试完成一份报告 | Issue 文本明确要求 | 完成高规格技术报告：`report.md` | 查看 `projects/02_bitcoin_simulator/report.md` | **[已验证 √]** | 报告系统对比了 ns-3 离散事件网络模拟器与 Python 状态机模拟器的模型边界、参数设定与实验结论，绝不将 Python 结果冒充 ns-3 输出。 |
| **REQ-3** | (独立工程扩展) 多节点 P2P 账本与最长链分叉重组实验 | 本地自建 Python 离散状态机模拟器 | `src/node.py`、`src/blockchain.py`、`src/network.py` | `python3 projects/02_bitcoin_simulator/tests/run_simulation.py` | **[已验证 √]** | 采用纯原生 Python 构建事件驱动的 P2P 仿真，已实际验证常规出块、Mempool 双花拦截、LCA 孤儿块重组与 51% 算力攻击。 |

---

## 二、 两个模拟器的模型与结论范围对比

| 维度 | 原版论文工具 (Arthur Gervais ns-3 Bitcoin-Simulator) | 本地教学扩展 (Python Educational State Machine) |
| :--- | :--- | :--- |
| **定位与目标** | 数据包级离散事件网络仿真，研究网络传播延迟对区块链孤块率（Orphan Rate）与安全性的量化影响 | 算法与状态机级事件驱动仿真，研究 UTXO 校验、Mempool 冲突、最长链分支重组（Reorg）与 51% 攻击博弈 |
| **底层核心依赖** | C++11, Network Simulator 3 (ns-3.25), RapidJSON, Python 2 Waf | Python 3 原生标准库 (`hashlib`, `time`, `copy`, `typing`) |
| **网络层建模** | 精确建模 TCP 三次握手、丢包率、跨洲海底光缆传输时延与地理分布节点连接度（Coinscope 数据） | 内存对象式消息路由，使用动态时钟和拓扑字典模拟点对点 Gossip 广播 |
| **区块与交易** | 抽象消息负载（不执行完整椭圆曲线解密，仅传输区块大小与哈希元数据以降低计算量） | 真实构建 UTXO 输入输出、交易哈希计算与工作量证明 Nonce 试算 |
| **核心输出指标** | 孤块率 (Stale Block Rate)、出块间隔对安全确认数（Confirmation Number）的权衡曲线 | 账户余额一致性、最长链收敛高度、双花欺诈成功率与 LCA 回滚深度 |

