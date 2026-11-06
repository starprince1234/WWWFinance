# Dockerfile for Ethereum Crowdfunding DApp
FROM node:20-alpine

LABEL maintainer="Internet Finance Student"
LABEL description="Containerized local EVM node, contract deployer, and DApp frontend server"

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制源码与前端
COPY . .

# 编译合约
RUN node scripts/compile.js

# 暴露前端 HTTP 服务端口 (8080) 与 Ganache RPC 端口 (8545)
EXPOSE 8080 8545

# 启动脚本
CMD ["sh", "-c", "npx ganache --host 0.0.0.0 --port 8545 & npx http-server frontend -p 8080"]

