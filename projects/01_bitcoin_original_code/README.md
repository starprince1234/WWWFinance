# 课题 01：比特币原始代码实践 (Bitcoin v0.1.0 Practice)

> **对应 Gitee 课题**：`#IKSCT7` [比特币的原始代码实践](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSCT7)  
> **指定参考仓库**：[trottier/original-bitcoin](https://github.com/trottier/original-bitcoin)  
> **核心对照文档**：[需求与验证矩阵 (requirements_matrix.md)](./requirements_matrix.md) | [技术研报 (report.md)](./report.md)  
> **当前宿主环境**：macOS (Darwin 24.3.0, arm64) | Python 3.9.6 | Docker Client 29.8.2 (Daemon inactive)

---

## 一、 重要声明与实施范畴界定

依据严肃的学术与工程原则，在此明确区分**原版 C++ 客户端**与**本地 Python 机制复现套件**的实施边界：

1. **原版 C++ 客户端 (Satoshi v0.1.0/v0.1.3)**：
   - 原项目发布于 2009 年，包含 32 位 Windows 可执行文件（`bitcoin.exe`）及基于 MinGW/GCC 3.4/4.x、OpenSSL 0.9.8、Berkeley DB 4.7、wxWidgets 2.8 的源码；
   - **环境限制与阻碍**：当前宿主机为 Apple Silicon ARM64 架构，且本地 Docker 守护进程未处于运行状态。原版 32 位 x86 C++ 代码无法在现代 ARM64 裸机上原生编译。为此，我们在 [`docker/`](./docker/) 目录中提供了完整的 32 位 Linux 历史容器化构建方案（`Dockerfile` 与 `run_nodes.sh`），但**如实记录其处于“已实现待宿主环境验证”状态，绝不伪造容器运行日志**。
2. **本地 Python 机制复现套件 (Educational Mechanism Reproduction)**：
   - 采用纯 Python 3 原生标准库，对中本聪原始客户端中的**创世区块全量参数、PoW 紧凑难度换算、Forth 栈式脚本引擎与 2009 IRC 节点发现**四大支柱进行了算法级 1:1 逆向重构；
   - 包含完备的独立单元测试套件，使用官方历史数据向量（如真实创世哈希与 Coinbase 交易）进行严格等价性比对。

---

## 二、 目录结构

```text
01_bitcoin_original_code/
├── README.md                      # 项目快速使用与复现指南
├── requirements_matrix.md         # 详细需求对照表与验证状态
├── report.md                      # 技术研报与中本聪架构深度解析
├── docker/                        # 原版 C++ 历史容器化方案 (待验证)
│   ├── Dockerfile                 # 32位 i386 Ubuntu 构建配置
│   └── run_nodes.sh               # 隔离节点启动脚本
├── src/                           # Python 核心机制算法复现
│   ├── crypto.py                  # SHA256, Hash160, secp256k1 ECDSA
│   ├── genesis.py                 # 创世区块与 Coinbase 交易精确重构模块
│   ├── pow_target.py              # nBits 紧凑格式转换、PoW 挖矿与难度自适应
│   ├── script_engine.py           # Forth 风格堆栈式脚本虚拟机与单步跟踪器
│   ├── transaction.py             # 交易序列化、反序列化与 SIGHASH 计算
│   └── irc_discovery_sim.py       # 2009 年 IRC 频道节点网络发现仿真
└── tests/
    ├── test_genesis.py            # 创世区块全等性单元测试
    ├── test_script.py             # 脚本引擎操作符与 P2PKH 签名验证测试
    └── run_all_experiments.py     # 综合集成演示套件 (一键跑通 4 项核心实验)
```

---

## 三、 快速复现与验证步骤

### 1. 一键运行 Python 算法验证套件（推荐）
在项目根目录执行：
```bash
python3 projects/01_bitcoin_original_code/tests/run_all_experiments.py
```
**实测结果说明**：
- 创世区块哈希计算值：`000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f`（与官方预期 100% 吻合，PASS）；
- 创世 Merkle 根：`4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b`（PASS）；
- 紧凑难度 `0x1d00ffff` 转换目标值展开与挖矿难度模拟成功；
- Forth 堆栈脚本单步跟踪：完整执行 `OP_DUP`、`OP_HASH160`、`OP_EQUALVERIFY`、`OP_CHECKSIG`，返回 True；
- 2009 IRC 协议节点编码（十六进制 IP）与邻居对等发现模拟成功。

### 2. 独立单元测试
```bash
# 验证创世区块与参考向量
python3 projects/01_bitcoin_original_code/tests/test_genesis.py

# 验证脚本引擎及防伪造签名拦截
python3 projects/01_bitcoin_original_code/tests/test_script.py
```

### 3. 原版容器化方案构建（若宿主机已启动 Docker）
```bash
# 构建 32 位容器
docker build -t bitcoin-v01 projects/01_bitcoin_original_code/docker/

# 运行容器
docker run -it --rm bitcoin-v01 /bin/bash
```
*(注：若本地 Docker 守护进程未启动，此命令将报错，需等待宿主 Docker 服务开启后复验。)*

---

## 四、 研报与学术分析

详细源码分析、架构图解与中本聪设计哲学请参阅配套研报：[`report.md`](./report.md)。
