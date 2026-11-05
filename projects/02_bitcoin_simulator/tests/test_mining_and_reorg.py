"""
测试挖矿与最长链分叉重组机制 (Test Mining & Fork Reorganization)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.network import NetworkSimulator

def test_mining_and_reorg():
    print("=== 测试场景一：多节点竞争与分叉重组 (Reorg) ===")
    sim = NetworkSimulator(difficulty_zeros=2)
    res = sim.run_scenario_accidental_fork()
    print(f"[*] Alice Tip Hash  : {res['alice_tip']}")
    print(f"[*] Bob Tip Hash    : {res['bob_tip']}")
    print(f"[*] Charlie Tip Hash: {res['charlie_tip']}")
    print(f"[*] 全网账本一致性  : {res['consistent']}")
    print(f"[*] 最终链高度      : #{res['final_height']}")

    assert res['consistent'] is True, "全网节点未能在最长链上达成一致共识!"
    assert res['final_height'] == 2, "预期最终高度为 #2"
    print(">>> 竞争分叉自动重组测试通过 (PASS)!")

if __name__ == '__main__':
    test_mining_and_reorg()

