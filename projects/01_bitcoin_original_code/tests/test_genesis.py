"""
创世区块验证测试 (Test Genesis Block)
验证创世交易、Merkle 根与区块双重哈希是否与中本聪 2009 年公布的真实历史完全一致
"""

import sys
import os

# 将上一级路径加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.genesis import verify_genesis_block, EXPECTED_GENESIS_HASH, EXPECTED_MERKLE_ROOT

def test_genesis_verification():
    res = verify_genesis_block()
    print("=== 创世区块测试详情 ===")
    print(f"Coinbase 长度: {res['coinbase_tx_len']} 字节")
    print(f"Merkle 根:     {res['merkle_root_hex']}")
    print(f"预期 Merkle:   {res['expected_merkle']}")
    print(f"Merkle 一致性: {res['is_merkle_match']}")
    print(f"计算区块哈希:  {res['calculated_hash']}")
    print(f"预期区块哈希:  {res['expected_hash']}")
    print(f"区块哈希匹配:  {res['is_hash_match']}")
    print(f"创世留言:      {res['headline']}")

    assert res['is_merkle_match'] is True, "Merkle 根不匹配!"
    assert res['is_hash_match'] is True, "创世区块哈希不匹配!"
    assert res['success'] is True, "创世区块整体验证失败!"
    print(">>> 创世区块复现测试全部通过 (PASS)!")

if __name__ == '__main__':
    test_genesis_verification()

