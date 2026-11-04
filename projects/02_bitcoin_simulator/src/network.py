"""
比特币模拟器 - 网络仿真环境与高阶攻防场景 (Network Simulation & Attack Scenarios)
模拟全网广播、网络延迟、天然竞争分叉及 51% 双花攻击全过程
"""

from typing import List, Dict, Tuple
from .node import Node
from .transaction import Transaction
from .block import Block

class NetworkSimulator:
    def __init__(self, difficulty_zeros: int = 3):
        self.difficulty_zeros = difficulty_zeros
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node_id: str) -> Node:
        node = Node(node_id, difficulty_zeros=self.difficulty_zeros)
        self.nodes[node_id] = node
        return node

    def build_full_mesh(self):
        """将当前网络中的所有节点两两互联成全连通网状拓扑 (Full Mesh)"""
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                node_list[i].connect(node_list[j])

    def print_network_status(self):
        print("\n" + "=" * 65)
        print(f"{'节点 ID':<18} | {'主链高度':<8} | {'余额 (BTC)':<12} | {'Mempool 大小':<12}")
        print("-" * 65)
        for node in self.nodes.values():
            btc_bal = node.get_balance() / 100000000.0
            print(f"{node.node_id:<18} | #{node.blockchain.current_height:<7} | {btc_bal:<12.4f} | {len(node.mempool):<12}")
        print("=" * 65 + "\n")

    def run_scenario_accidental_fork(self) -> Dict:
        """
        场景一：天然网络竞争分叉与最长链自动重组实验
        1. 矿工 Alice 与 矿工 Bob 同时基于高度 #0 挖出高度 #1 的两个不同区块
        2. 网络产生对等竞争分叉 (Chain A vs Chain B)
        3. 随后 Alice 又率先挖出高度 #2
        4. Bob 与全网其他节点监测到更高链，自动触发【分叉重组 (Reorg)】，收敛至 Alice 主链
        """
        sim = NetworkSimulator(difficulty_zeros=self.difficulty_zeros)
        alice = sim.add_node("Miner_Alice")
        bob = sim.add_node("Miner_Bob")
        charlie = sim.add_node("Observer_Charlie")
        
        sim.build_full_mesh()

        # 1. 模拟隔离状态下分别挖矿生成分叉
        b_alice = alice.mine_block(broadcast=False)
        b_bob = bob.mine_block(broadcast=False)

        # Charlie 此时先收到 Bob 的块
        charlie.receive_block(b_bob, broadcast=False)

        # 2. Alice 继续抢跑，挖出下一个块 #2
        b_alice_2 = alice.mine_block(broadcast=False)

        # 3. Alice 将自己的更长分支 (#1 和 #2) 广播给 Bob 和 Charlie
        bob.receive_block(b_alice, broadcast=False)
        bob_reorg = bob.receive_block(b_alice_2, broadcast=False)

        charlie.receive_block(b_alice, broadcast=False)
        charlie_reorg = charlie.receive_block(b_alice_2, broadcast=False)

        return {
            "alice_tip": alice.blockchain.tip_hash,
            "bob_tip": bob.blockchain.tip_hash,
            "charlie_tip": charlie.blockchain.tip_hash,
            "consistent": (alice.blockchain.tip_hash == bob.blockchain.tip_hash == charlie.blockchain.tip_hash),
            "final_height": alice.blockchain.current_height
        }

    def run_scenario_double_spend_attack(self) -> Dict:
        """
        场景二：51% 算力优势下的双花攻击 (Double-Spending Attack)
        1. 诚实矿工 Alice 挖出高度 #1，获得 50 BTC 创世奖励
        2. 攻击者 Mallory 准备用 30 BTC 购买商家 Charlie 的昂贵资产
        3. Mallory 正常向 Charlie 支付 30 BTC，Alice 打包进公开区块 #2
        4. 商家 Charlie 看到 1 次区块确认 (1-confirmation)，向 Mallory 发货！
        5. Mallory 在私下秘密挖一条更长私有链 (#2' 和 #3')，将 30 BTC 重新转回自己的钱包！
        6. Mallory 突然向全网广播私有更长链，全网发生 Reorg，Charlie 的收款凭空蒸发！
        """
        sim = NetworkSimulator(difficulty_zeros=self.difficulty_zeros)
        alice = sim.add_node("Miner_Alice")
        mallory = sim.add_node("Attacker_Mallory")
        charlie = sim.add_node("Merchant_Charlie")
        
        sim.build_full_mesh()

        # Step 1: Mallory 先挖一个块获得初始资金 50 BTC
        mallory.mine_block(broadcast=True)

        # Step 2: Mallory 向 Charlie 发送 30 BTC 购买豪华商品
        tx_payment = mallory.create_transaction(charlie.address, amount=30 * 100000000)

        # Step 3: 诚实矿工 Alice 将这笔支付打包进公开区块 #2
        honest_block_2 = alice.mine_block(broadcast=True)
        charlie_bal_after_payment = charlie.get_balance() / 100000000.0

        # Step 4: Mallory 在本地秘密构建分叉链 (基于区块 #1，完全不包含给 Charlie 的支付)
        # Mallory 秘密挖矿 #2' (Coinbase 奖励给自己)
        parent_block_1 = mallory.blockchain.blocks_by_hash[honest_block_2.header.prev_block_hash]
        priv_block_2 = Block(
            height=2,
            prev_block_hash=parent_block_1.hash,
            transactions=[Transaction.create_coinbase(mallory.address, 50 * 100000000, 2)],
            difficulty_zeros=self.difficulty_zeros
        )
        priv_block_2.mine()

        # Mallory 秘密挖矿 #3' (更长，形成 2 区块长度优势)
        priv_block_3 = Block(
            height=3,
            prev_block_hash=priv_block_2.hash,
            transactions=[Transaction.create_coinbase(mallory.address, 50 * 100000000, 3)],
            difficulty_zeros=self.difficulty_zeros
        )
        priv_block_3.mine()

        # Step 5: Mallory 突然全网广播更长的私有链分支
        alice.receive_block(priv_block_2, broadcast=False)
        alice.receive_block(priv_block_3, broadcast=False)

        charlie.receive_block(priv_block_2, broadcast=False)
        charlie.receive_block(priv_block_3, broadcast=False)

        charlie_bal_after_attack = charlie.get_balance() / 100000000.0

        return {
            "charlie_bal_before": charlie_bal_after_payment,
            "charlie_bal_after": charlie_bal_after_attack,
            "attack_successful": (charlie_bal_after_payment == 30.0 and charlie_bal_after_attack == 0.0),
            "final_height": charlie.blockchain.current_height
        }
