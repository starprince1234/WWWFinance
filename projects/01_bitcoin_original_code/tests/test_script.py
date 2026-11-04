"""
中本聪脚本引擎与加密算法测试 (Test Script Engine & ECDSA)
包含纯 Python secp256k1 签名、P2PK 模式与经典 P2PKH 解锁全流程
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crypto import (
    privkey_to_pubkey, ecdsa_sign, ecdsa_verify,
    encode_der, decode_der, hash160, hash256
)
from src.script_engine import (
    ScriptEngine, OP_DUP, OP_HASH160, OP_EQUALVERIFY,
    OP_CHECKSIG, OP_ADD, OP_2, OP_3, OP_EQUAL
)

def test_arithmetic_script():
    print("\n--- 1. 测试基础算术堆栈脚本 (2 + 3 == 5) ---")
    engine = ScriptEngine(trace=True)
    # scriptSig: [OP_2, OP_3] -> 栈: [2, 3]
    # scriptPubKey: [OP_ADD, 5, OP_EQUAL] -> 栈: [True]
    sig_script = [OP_2, OP_3]
    pubkey_script = [OP_ADD, bytes([5]), OP_EQUAL]
    res = engine.execute(sig_script, pubkey_script)
    assert res is True, "算术脚本执行失败!"
    print(">>> 算术脚本验证通过 (PASS)")

def test_p2pkh_script():
    print("\n--- 2. 测试经典 P2PKH (Pay-to-Public-Key-Hash) 签名验证脚本 ---")
    # 模拟私钥
    privkey = 0x123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0
    pubkey = privkey_to_pubkey(privkey, compressed=False)
    pkh = hash160(pubkey)

    # 模拟一笔待签名的交易哈希
    dummy_tx_hash = hash256(b"bitcoin_transaction_test_data_v0.1")

    # 使用私钥签名
    r, s = ecdsa_sign(dummy_tx_hash, privkey)
    der_sig = encode_der(r, s)

    # 锁定脚本 (scriptPubKey):
    # OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
    script_pubkey = [OP_DUP, OP_HASH160, pkh, OP_EQUALVERIFY, OP_CHECKSIG]

    # 解锁脚本 (scriptSig):
    # <sig> <pubKey>
    script_sig = [der_sig, pubkey]

    engine = ScriptEngine(trace=True)
    res = engine.execute(script_sig, script_pubkey, tx_hash=dummy_tx_hash)
    assert res is True, "P2PKH 脚本验证失败!"
    print(">>> P2PKH 完整交易解锁验证通过 (PASS)")

    # 负面测试: 使用错误签名进行欺诈验证
    print("\n--- 3. 负面测试: 伪造签名验证 ---")
    fake_r, fake_s = (r + 1, s)
    fake_sig = encode_der(fake_r, fake_s)
    fake_script_sig = [fake_sig, pubkey]
    engine_fail = ScriptEngine(trace=False)
    fail_res = engine_fail.execute(fake_script_sig, script_pubkey, tx_hash=dummy_tx_hash)
    assert fail_res is False, "伪造签名未被拦截!"
    print(">>> 伪造签名成功被拦截 (PASS)")

if __name__ == '__main__':
    test_arithmetic_script()
    test_p2pkh_script()
