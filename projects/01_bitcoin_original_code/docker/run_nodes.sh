#!/usr/bin/env bash
# 启动多节点隔离挖矿与交易脚本 (需在 Docker 容器或 Linux VM 中执行)
set -e

echo "=== 正在初始化 2 个隔离节点环境 ==="
mkdir -p /tmp/node1 /tmp/node2

cat << 'EOF' > /tmp/node1/bitcoin.conf
server=1
daemon=1
rpcuser=scufinance
rpcpassword=localpass
port=8333
listen=1
EOF

cat << 'EOF' > /tmp/node2/bitcoin.conf
server=1
daemon=1
rpcuser=scufinance
rpcpassword=localpass
port=8334
connect=127.0.0.1:8333
EOF

echo "节点配置就绪。"
echo "提示: original-bitcoin v0.1 无 -regtest 命令，需通过配置文件 -connect 建立单向连接。"

