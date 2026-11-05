"""
课题04：开发众筹平台(工作量大) - 综合演示与服务启动引导 (Master Platform Runner)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_api import test_full_crowdfunding_lifecycle
from src.app import run_server

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def main():
    print("=" * 70)
    print("   《互联网金融》课题04：开发众筹平台（工作量大）(CloudFund Platform)")
    print("   Sichuan University (SCU) - Internet Finance Research Project")
    print("=" * 70)

    # 1. 运行核心业务与清结算测试
    print_header("阶段一：全栈金融业务、ACID 事务与清结算核心引擎回归测试")
    test_full_crowdfunding_lifecycle()

    # 2. 启动或提示启动全栈 Web 服务
    print_header("阶段二：全栈众筹平台 Web 服务指引")
    print("[*] 数据库已自动就绪 (SQLite: crowdfunding.db)")
    print("[*] RESTful API 与响应式前端 SPA 服务开箱即用。")
    print("[*] 启动命令:")
    print("    python3 projects/04_crowdfunding_platform/src/app.py 8081")
    print("[*] 访问地址: http://localhost:8081")
    print("    内置测试账户:")
    print("    - 发起人: tech_maker / 123456 (余额 ¥20,000)")
    print("    - 投资人: backer_alice / 123456 (余额 ¥50,000)")
    print("=" * 70)

if __name__ == '__main__':
    main()

