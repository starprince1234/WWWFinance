# Dockerfile for Arthur Gervais et al. Bitcoin-Simulator (ACM CCS 2016)
# Target environment: Ubuntu 16.04 LTS (x86_64) with GCC 5 and Python 2.7
FROM --platform=linux/amd64 ubuntu:16.04

LABEL maintainer="Internet Finance Student"
LABEL description="Containerized environment for ns-3 based Bitcoin-Simulator"

ENV DEBIAN_FRONTEND=noninteractive

# 安装 ns-3.25 所需依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python \
    python-dev \
    git \
    wget \
    tar \
    bzip2 \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 1. 下载 ns-allinone-3.25
RUN wget https://www.nsnam.org/release/ns-allinone-3.25.tar.bz2 && \
    tar xjf ns-allinone-3.25.tar.bz2 && \
    rm ns-allinone-3.25.tar.bz2

# 2. 获取 RapidJSON
RUN git clone https://github.com/Tencent/rapidjson.git && \
    mkdir -p /workspace/ns-allinone-3.25/ns-3.25/rapidjson && \
    cp -r rapidjson/include/rapidjson /workspace/ns-allinone-3.25/ns-3.25/rapidjson/

# 3. 克隆 Bitcoin-Simulator 并拷贝代码至 ns-3
RUN git clone https://github.com/arthurgervais/Bitcoin-Simulator.git && \
    cp -r Bitcoin-Simulator/src/applications/* /workspace/ns-allinone-3.25/ns-3.25/src/applications/

WORKDIR /workspace/ns-allinone-3.25/ns-3.25

# 4. 配置与构建 (通过 waf 构建 ns-3)
# RUN ./waf configure --enable-examples --enable-tests && ./waf

CMD ["/bin/bash"]

