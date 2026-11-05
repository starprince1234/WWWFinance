"""
课题02：比特币模拟器(实践) - 综合网络仿真与攻防演示 (Master Simulator Runner)
提供可视化全景交互，演练交易生命周期、PoW多节点挖矿、竞争分叉重组及 51% 双花攻防
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.network import NetworkSimulator

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def main():
    print("=" * 70)
    print("   《互联网金融》课题02：比特币网络与共识模拟器 (Bitcoin Simulator)")
    print("   Sichuan University (SCU) - Internet Finance Research Project")
    print("=" * 70)

    # 1. 初始化仿真网络
    print_header("阶段一：P2P 全连通网络初始化与创世账本同步")
    sim = NetworkSimulator(difficulty_zeros=2)
    alice = sim.add_node("Miner_Alice")
    bob = sim.add_node("Miner_Bob")
    charlie = sim.add_node("Merchant_Charlie")
    david = sim.add_node("User_David")
    sim.build_full_mesh()

    print(f"[*] 成功组网 4 个独立节点: Alice, Bob, Charlie, David")
    print(f"[*] 创世区块已同步，全网初始链高度均为 #0")
    sim.print_network_status()

    # 2. 模拟常规转账与出块
    print_header("阶段二：交易生命周期与常规出块流程")
    print("[*] 1. 矿工 Alice 挖出区块 #1，获得 50 BTC 铸币奖励 (Coinbase)...")
    b1 = alice.mine_block(broadcast=True)
    sim.print_network_status()

    print("[*] 2. Alice 组装交易: 向普通用户 David 转账 15 BTC (含找零 35 BTC)...")
    tx_a2d = alice.create_transaction(david.address, amount=15 * 100000000)
    print(f"    交易已广播入池，TxID: {tx_a2d.txid[:16]}...")
    print(f"    当前各节点 Mempool 待处理交易数: {len(alice.mempool)}")

    print("[*] 3. 矿工 Bob 打包 Alice 的转账交易并挖出区块 #2...")
    b2 = bob.mine_block(broadcast=True)
    print(f"    区块 #{b2.height} 已被 Bob 成功上链并全网广播!")
    sim.print_network_status()

    # 3. 模拟竞争分叉与最长链自动重组
    print_header("阶段三：天然竞争分叉与最长链重组 (Chain Reorganization) 模拟")
    print("[*] 模拟网络隔离场景：Alice 与 Bob 同时基于高度 #2 挖出不同的区块 #3A 和 #3B...")
    b3_alice = alice.mine_block(broadcast=False)
    b3_bob = bob.mine_block(broadcast=False)
    print(f"    Alice 孤立块 #3A 哈希: {b3_alice.hash[:16]}...")
    print(f"    Bob 孤立块   #3B 哈希: {b3_bob.hash[:16]}...")

    print("[*] 随后 Alice 抢先挖出更高区块 #4A，并向 Bob 全网同步...")
    b4_alice = alice.mine_block(broadcast=False)
    
    print("[*] Bob 接收 Alice 的长链分支 (#3A 与 #4A)...")
    bob.receive_block(b3_alice, broadcast=False)
    bob.receive_block(b4_alice, broadcast=False)

    print(f"[*] 分叉结算结果:")
    print(f"    Alice Tip: {alice.blockchain.tip_hash[:16]}... (高度 #{alice.blockchain.current_height})")
    print(f"    Bob Tip:   {bob.blockchain.tip_hash[:16]}... (高度 #{bob.blockchain.current_height})")
    assert alice.blockchain.tip_hash == bob.blockchain.tip_hash, "最长链收敛失败"
    print("    [√] Bob 成功执行 Reorg，放弃本地孤块 #3B，自动对齐 Alice 最长主链！")

    # 4. 模拟 51% 算力双花攻击
    print_header("阶段四：高阶攻防实验 —— 51% 算力优势下的双花欺诈攻击")
    print("[*] 运行独立的 51% 双花攻防场景仿真...")
    attack_res = sim.run_scenario_double_spend_attack()
    print(f"    攻击前商家 Charlie 账户确认收讫 : {attack_res['charlie_bal_before']:.1f} BTC")
    print(f"    攻击重组后 Charlie 实际账面余额 : {attack_res['charlie_bal_after']:.1f} BTC")
    print(f"    双花攻击状态                     : {'[√] 成功覆写历史交易并撤回付款' if attack_res['attack_successful'] else '[x] 失败'}")
    print(f"    网络共识最高区块高度             : #{attack_res['final_height']}")

    print_header("全部四大仿真实验演示完毕！")
    print("本模拟器完整再现了比特币网络底层共识博弈与分叉解决全过程。\n")

if __name__ == '__main__':
    main()

