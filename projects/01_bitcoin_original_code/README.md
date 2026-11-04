# 课题 01：比特币原始代码实践 (Bitcoin v0.1.0 Practice)

> **对应 Gitee 课题**：`#IKSCT7` 比特币的原始代码实践  
> **项目定位**：中本聪 2009 年原始客户端核心机制的现代 Python 深度复现与实验验证  
> **环境要求**：Python 3.8+ (纯原生标准库实现，零外部第三方依赖)

---

## 一、 项目背景与目标

2009 年 1 月 3 日，中本聪（Satoshi Nakamoto）发布了比特币第一版客户端（v0.1.0）。该版本奠定了现代加密货币与分布式账本的基础构架。本项目针对中本聪原始 C++ 源码中的四大核心支柱进行工程化解构与现代高保真复现：

1. **创世区块 (Genesis Block) 原生复现**：精确重构包含《泰晤士报》头条创世留言的 Coinbase 交易、Merkle 根与区块头哈希，全等验证中本聪历史参数；
2. **工作量证明 (PoW) 与动态难度调整**：复现 `nBits` 紧凑浮点编码向 256 位大整数的目标转换公式、2016 区块难度自适应算法与本地 `ScanHash` 挖矿循环；
3. **基于栈的 Forth 风格脚本引擎 (Script Engine)**：实现非图灵完备虚拟机，提供单步堆栈调试日志，完整支持 P2PK、P2PKH 签名验证以及数学/逻辑操作符；
4. **历史 IRC 节点发现协议仿真**：解构并仿真 2009 年比特币借助 `irc.oftc.net` 聊天室进行对等网络节点发现的经典机制。

---

## 二、 目录结构

```text
01_bitcoin_original_code/
├── README.md                      # 项目快速使用与技术说明文档
├── report.md                      # 期末考核标准技术报告 (Tech Report)
├── src/
│   ├── crypto.py                  # 基础密码学 (Hash256, Hash160, pure-python secp256k1 ECDSA)
│   ├── genesis.py                 # 创世区块与 Coinbase 交易精确重构模块
│   ├── pow_target.py              # nBits 紧凑格式转换、PoW 挖矿与 2016 区块难度自适应
│   ├── script_engine.py           # Forth 风格堆栈式脚本虚拟机与单步跟踪器
│   ├── transaction.py             # 交易序列化、反序列化与 SIGHASH 计算
│   └── irc_discovery_sim.py       # 2009 年 IRC 频道节点网络发现仿真
└── tests/
    ├── test_genesis.py            # 创世区块全等性单元测试
    ├── test_script.py             # 脚本引擎操作符与 P2PKH 签名验证测试
    └── run_all_experiments.py     # 综合集成演示套件 (一键跑通 4 项核心实验)
```

---

## 三、 快速上手与运行

本项目采用纯 Python 标准库编写，无需额外 `pip install` 任何包，直接在终端运行即可：

### 1. 一键运行综合集成实验（推荐）
```bash
python3 projects/01_bitcoin_original_code/tests/run_all_experiments.py
```
你将看到：
- 创世区块哈希 `000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f` 验证比对；
- 本地 PoW 挖矿寻找有效 Nonce，计算本地实时 Hash/s；
- 脚本虚拟机单步展示 `OP_DUP`、`OP_HASH160`、`OP_EQUALVERIFY`、`OP_CHECKSIG` 堆栈进出栈过程；
- IRC 网络节点 IP 编解码与邻居发现仿真。

### 2. 独立运行单元测试
```bash
# 验证创世区块
python3 projects/01_bitcoin_original_code/tests/test_genesis.py

# 验证脚本引擎与签名
python3 projects/01_bitcoin_original_code/tests/test_script.py
```

---

## 四、 技术报告

完整学术与工程技术分析见配套文档：[期末技术报告：比特币原始代码实践与机理解析 (report.md)](./report.md)。

