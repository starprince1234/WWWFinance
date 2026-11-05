"""
课题03：以太坊众筹 DAPP - 综合验证与本地服务启动器 (Master DApp Runner)
运行 EVM 智能合约核心逻辑验证，并一键启动前端可视化体验服务
"""

import sys
import os
import http.server
import socketserver
import webbrowser
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_contracts import (
    test_campaign_pledge_and_unpledge,
    test_failed_campaign_full_refund,
    test_milestone_dao_governance
)

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def run_evm_tests():
    print_header("阶段一：Solidity 智能合约 EVM 逻辑全量回归测试")
    test_campaign_pledge_and_unpledge()
    test_failed_campaign_full_refund()
    test_milestone_dao_governance()
    print("\n[√] 智能合约核心状态机所有逻辑验证 100% 通过！")

def main():
    print("=" * 70)
    print("   《互联网金融》课题03：以太坊去中心化众筹 DAPP (EtherCrowd)")
    print("   Sichuan University (SCU) - Internet Finance Research Project")
    print("=" * 70)

    run_evm_tests()

    print_header("阶段二：前端 Web3 DAPP 交互服务指引")
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    index_file = os.path.join(frontend_dir, 'index.html')
    print(f"[*] 前端静态工程已就绪: {frontend_dir}")
    print(f"[*] 可直接双击在浏览器打开:")
    print(f"    file://{index_file}")
    print(f"[*] 或在本地运行轻量 Web 服务器: python3 -m http.server --directory {frontend_dir} 8080")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()

