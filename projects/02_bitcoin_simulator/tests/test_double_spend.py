"""
测试双花防御与 51% 算力双花攻击 (Test Double-Spend Defense & 51% Attack)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.network import NetworkSimulator
from src.node import Node
from src.transaction import Transaction, TxIn, TxOut

def test_mempool_double_spend_prevention():
    print("\n--- 1. 测试节点本地交易内存池 (Mempool) 双花拦截 ---")
    node = Node("Miner_Test", difficulty_zeros=2)
    # 挖出 1 个块获取 50 BTC 初始资金
    node.mine_block(broadcast=False)
    assert node.get_balance() == 50 * 100000000, "挖矿奖励未到账"

    # 获取当前可用的一笔 UTXO
    utxo_key = list(node.blockchain.utxo_set.keys())[0]

    # 构造第 1 笔合法交易
    tx1 = Transaction(
        inputs=[TxIn(prev_txid=utxo_key[0], out_index=utxo_key[1], signature="SIG1")],
        outputs=[TxOut(value=20 * 100000000, recipient_address="1RecipientAddress1111111111111")]
    )
    ok1 = node.receive_transaction(tx1, broadcast=False)
    assert ok1 is True, "第一笔合法交易入池失败"

    # 构造第 2 笔冲突交易 (引用同一笔 UTXO 双花)
    tx2 = Transaction(
        inputs=[TxIn(prev_txid=utxo_key[0], out_index=utxo_key[1], signature="SIG2")],
        outputs=[TxOut(value=30 * 100000000, recipient_address="1AnotherAddress2222222222222")]
    )
    ok2 = node.receive_transaction(tx2, broadcast=False)
    assert ok2 is False, "第二笔双花冲突交易未被内存池拦截!"
    print(">>> 内存池同源 UTXO 双花冲突成功拦截 (PASS)!")


def test_51_percent_double_spend_attack():
    print("\n--- 2. 测试 51% 算力优势下的私有链分叉双花攻击 ---")
    sim = NetworkSimulator(difficulty_zeros=2)
    res = sim.run_scenario_double_spend_attack()
    print(f"[*] 攻击前商家 Charlie 确认入账 : {res['charlie_bal_before']} BTC")
    print(f"[*] 攻击重组后 Charlie 账面余额 : {res['charlie_bal_after']} BTC")
    print(f"[*] 攻击判定结果                : {'[√] 双花成功 (货款蒸发)' if res['attack_successful'] else '[x] 攻击失败'}")
    print(f"[*] 最终链高度                  : #{res['final_height']}")

    assert res['attack_successful'] is True, "51% 深度分叉双花攻击模拟失败!"
    print(">>> 51% 双花攻击与最长链重组实验通过 (PASS)!")

if __name__ == '__main__':
    test_mempool_double_spend_prevention()
    test_51_percent_double_spend_attack()

