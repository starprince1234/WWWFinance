# 课题 01：需求与对照矩阵 (Requirements & Verification Matrix)

> **对应 Gitee 课题**：`#IKSCT7` [比特币的原始代码实践](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSCT7)  
> **指定参考仓库**：[trottier/original-bitcoin](https://github.com/trottier/original-bitcoin)  
> **审计日期**：2026-11-05  
> **运行环境**：macOS (Darwin 24.3.0, arm64) | Python 3.9.6 | Docker Client 29.8.2 (Daemon inactive)

---

## 一、 需求对照表

| 序号 | 老师 Issue 原文要求 | 对应官方/原始来源 | 本地实现与现状证据 | 运行/复现命令 | 实测结果与状态 | 局限性与外部阻碍说明 |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **REQ-1** | 在虚拟机或 Docker 容器中实践 | `https://github.com/trottier/original-bitcoin` (v0.1.3 ALPHA 源码与 32位 Windows 二进制) | 编写了专用历史容器化配置：`docker/Dockerfile` (基于 32位 Debian/Ubuntu 与 MinGW/GCC) | `docker build -t bitcoin-v01 docker/` | **[被阻碍 / 待宿主启动]** | **精确阻碍**：当前宿主机 macOS ARM64 上的 Docker 守护进程未运行 (`connect: dial unix /Users/adw/.orbstack/run/docker.sock: no such file or directory`)；且原版 C++ 依赖 2008 年 32位 x86 工具链（OpenSSL 0.9.8h, Berkeley DB 4.7.25, Boost 1.37, wxWidgets 2.8），现代 ARM64 裸机无法原生编译 32位 x86。 |
| **REQ-2** | 创造几个节点，相互交易和挖矿 | v0.1 源码 `src/net.cpp` (IRC 发现与节点通信) 与 `src/main.cpp` (挖矿循环) | 1. 原版多节点方案：编写了多节点隔离启动脚本 `docker/run_nodes.sh` (-connect 与 -datadir 配置)；<br>2. 教学机制复现：在 `src/` 中构建了纯 Python 的 P2P 发现与独立验证套件 | `python3 projects/01_bitcoin_original_code/tests/run_all_experiments.py` | **[已验证 √ (Python机制套件)]**<br>**[已实现未验证 (原版容器)]** | 原版 v0.1.0 客户端硬编码连接 IRC (`irc.oftc.net:6667`)，当年无 `-regtest` 模式（Bitcoin Core 0.9 才有）。在无独立内网 DNS/IRC 伪造下易直接泄露至公网或连通失败。Python 仿真套件已 100% 验证出块、交易与广播。 |
| **REQ-3** | 输出一份报告，最好 Markdown 格式可以直接上网 | Issue 文本明确要求 | 完成高规格技术研报：`report.md` | 查看 `projects/01_bitcoin_original_code/report.md` | **[已验证 √]** | 报告严格区分“原版 C++ 源码逆向剖析”与“本地 Python 教学算法复现”，绝不将 Python 模型冒充原版客户端执行结果。 |

---

## 二、 核心算法与独立测试向量验证

| 测试项 | 官方历史标准向量 | 本地算法实测值 | 验证状态 | 对应代码位置 |
| :--- | :--- | :--- | :---: | :--- |
| **创世区块时间戳** | `1231006505` (2009-01-03 18:15:05 UTC) | `1231006505` | PASS | `src/genesis.py#L32` |
| **Coinbase 创世留言** | `"The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"` | 完全一致（ASCII 解码验证） | PASS | `src/genesis.py#L22` |
| **创世 Merkle 根** | `4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b` | `4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b` | PASS | `tests/test_genesis.py#L18` |
| **创世区块哈希 (双SHA-256)** | `000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f` | `000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f` | PASS | `tests/test_genesis.py#L25` |
| **创世难度 Nonce** | `2083236893` (`0x7c2bac1d`) | `2083236893` | PASS | `src/genesis.py#L35` |
| **P2PKH 栈式脚本执行** | `scriptSig + scriptPubKey` 判定栈顶为 True | 单步堆栈跟踪返回 `PASS`，篡改签名返回 `FAIL` | PASS | `tests/test_script.py#L30-L75` |

