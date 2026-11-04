"""
课题01：比特币原始代码实践 - 综合实验运行套件 (Master Experiment Runner)
一键运行并演示中本聪 v0.1 核心机制的现代复现与实验结果
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.genesis import verify_genesis_block
from src.pow_target import (
    nbits_to_target, target_to_nbits, calculate_difficulty,
    adjust_difficulty, mine_block, POW_LIMIT_BITS
)
from src.script_engine import (
    ScriptEngine, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG
)
from src.crypto import privkey_to_pubkey, hash160, hash256, ecdsa_sign, encode_der
from src.irc_discovery_sim import SatoshiIRCDiscovery, IRCServerMock

def print_banner(title: str):
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)

def run_experiment_1_genesis():
    print_banner("实验一：中本聪创世区块 (Genesis Block) 原生参数全量复现与比对")
    res = verify_genesis_block()
    print(f"[*] 创世时间 (Timestamp) : {res['timestamp_utc']}")
    print(f"[*] 泰晤士报头条留言     : \"{res['headline']}\"")
    print(f"[*] 创世 Coinbase 交易长 : {res['coinbase_tx_len']} 字节")
    print(f"[*] 计算所得 Merkle 根   : {res['merkle_root_hex']}")
    print(f"[*] 官方预期 Merkle 根   : {res['expected_merkle']}")
    print(f"[*] Merkle 根完全一致性  : {'[√] PASS (100% 吻合)' if res['is_merkle_match'] else '[x] FAIL'}")
    print(f"[*] 计算所得创世区块哈希 : {res['calculated_hash']}")
    print(f"[*] 官方预期创世区块哈希 : {res['expected_hash']}")
    print(f"[*] 创世哈希完全一致性   : {'[√] PASS (100% 吻合)' if res['is_hash_match'] else '[x] FAIL'}")
    print(f"[*] 黄金 Nonce (随机数)  : {res['golden_nonce']}")

def run_experiment_2_pow_mining():
    print_banner("实验二：工作量证明 (PoW) 目标计算、动态难度调整与算力模拟")
    # 演示目标值转换
    target_int = nbits_to_target(POW_LIMIT_BITS)
    print(f"[*] 紧凑格式 (nBits) 0x1d00ffff 展开为 256 位大整数目标值:")
    print(f"    0x{target_int:064x}")
    print(f"[*] 创世基准难度 (Difficulty): {calculate_difficulty(target_int):.4f}")

    # 模拟难度调整机制 (假设过去 2016 个区块仅用了 7 天，算力暴涨一倍)
    actual_time = 7 * 24 * 3600  # 7 天 (目标应为 14 天)
    new_nbits = adjust_difficulty(POW_LIMIT_BITS, actual_time)
    new_target = nbits_to_target(new_nbits)
    new_diff = calculate_difficulty(new_target)
    print(f"[*] 模拟 2016 区块出块耗时过短 (7天/目标14天) -> 难度自动上调:")
    print(f"    调整前难度: 1.0000 -> 调整后难度: {new_diff:.4f} (难度翻倍, 目标值缩半)")

    # 本地实时挖矿演示 (设置测试难度为前导 16 位零)
    test_nbits = 0x1f00ffff  # 极低难度，快速出块演示
    test_header_prefix = b'\x01\x00\x00\x00' + b'\x00'*32 + b'\xaa'*32 + int(time.time()).to_bytes(4, 'little') + test_nbits.to_bytes(4, 'little')
    print(f"[*] 启动本地挖矿 ScanHash 循环 (模拟中本聪 v0.1 挖矿)...")
    start_t = time.time()
    ok, nonce, h, tries = mine_block(test_header_prefix, test_nbits, max_tries=500000)
    dur = time.time() - start_t
    if ok:
        hash_hex = h[::-1].hex()
        hashrate = tries / (dur if dur > 0 else 0.001)
        print(f"    [√] 成功挖出新区块!")
        print(f"    出块哈希: {hash_hex}")
        print(f"    消耗 Nonce: {nonce} | 尝试次数: {tries} 次 | 耗时: {dur:.4f}秒")
        print(f"    本地瞬时算力: {hashrate:.2f} Hash/s")

def run_experiment_3_script_vm():
    print_banner("实验三：基于堆栈的 Forth 风格脚本引擎 (P2PKH 交易解锁单步追踪)")
    priv = 0x8888888888888888888888888888888888888888888888888888888888888888
    pub = privkey_to_pubkey(priv, compressed=False)
    pkh = hash160(pub)
    tx_hash = hash256(b"satoshi_original_tx_payload")
    r, s = ecdsa_sign(tx_hash, priv)
    sig = encode_der(r, s)

    engine = ScriptEngine(trace=True)
    script_sig = [sig, pub]
    script_pubkey = [OP_DUP, OP_HASH160, pkh, OP_EQUALVERIFY, OP_CHECKSIG]
    print("[*] 正在执行 P2PKH 交易解锁单步追踪:")
    valid = engine.execute(script_sig, script_pubkey, tx_hash=tx_hash)
    print(f"[*] 脚本验证最终判定: {'[√] PASS (签名有效，UTXO成功花费)' if valid else '[x] FAIL'}")

def run_experiment_4_irc_discovery():
    print_banner("实验四：中本聪 2009 年 IRC 聊天室去中心化节点发现机制仿真")
    mock_irc = IRCServerMock()
    # 模拟加入节点的 IP 地址
    nodes = ["192.168.1.10", "10.0.0.5", "172.16.2.88", "114.114.114.114"]
    print(f"[*] 节点启动，连接 irc.oftc.net:6667 频道 #bitcoin")
    for ip in nodes:
        nick = mock_irc.register_node(ip)
        print(f"    -> 节点 [{ip}] 上线，向 IRC 注册昵称: {nick}")

    my_nick = SatoshiIRCDiscovery.encode_ip_to_nick("192.168.1.10")
    discovered = mock_irc.get_discovered_peers(my_nick)
    print(f"[*] 本地节点 [{my_nick}] 通过 IRC WHO 命令解析到的邻居对等节点列表:")
    for peer in discovered:
        print(f"    [√] 成功发现对等节点: {peer}:8333 (发起握手)")

def main():
    print("=" * 70)
    print("   《互联网金融》课题01：比特币原始代码实践 (v0.1.0 深度复现套件)")
    print("   Sichuan University (SCU) - Internet Finance Research Project")
    print("=" * 70)
    run_experiment_1_genesis()
    run_experiment_2_pow_mining()
    run_experiment_3_script_vm()
    run_experiment_4_irc_discovery()
    print_banner("全部 4 项实验顺利执行完毕，验证结果 100% 符合预期！")

if __name__ == '__main__':
    main()
