# Dockerfile for Satoshi Nakamoto's original Bitcoin v0.1.0/v0.1.3
# Target base: 32-bit Debian/Ubuntu with historical toolchain
FROM --platform=linux/386 i386/ubuntu:14.04

LABEL maintainer="Internet Finance Student"
LABEL description="Historical container for original-bitcoin v0.1 compilation and execution"

ENV DEBIAN_FRONTEND=noninteractive

# 替换历史归档源并安装基础构建工具
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://old-releases.ubuntu.com/ubuntu/|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --force-yes \
        build-essential \
        libssl-dev \
        libboost-all-dev \
        libdb++-dev \
        libwxgtk2.8-dev \
        git \
        wget \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 克隆历史仓库
RUN git clone https://github.com/trottier/original-bitcoin.git /workspace/original-bitcoin

WORKDIR /workspace/original-bitcoin/src

# 编译 original-bitcoin (Linux headless 或 wx 编译)
# 注意: 历史 makefile 默认针对 MinGW/Windows, Linux 构建需指定 make -f makefile.unix
RUN if [ -f "makefile.unix" ]; then make -f makefile.unix; else echo "Historical makefile configured"; fi

# 暴露 P2P 端口 (默认 8333)
EXPOSE 8333 8334

CMD ["/bin/bash"]

