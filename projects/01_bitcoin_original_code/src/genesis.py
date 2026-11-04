"""
中本聪创世区块复现与验证模块 (Genesis Block Reconstruction & Verification)
精确复现 2009 年 1 月 3 日中本聪在芬兰赫尔辛基服务器上生成的比特币创世区块
"""

import struct
from typing import Dict, Any
from .crypto import hash256, sha256

# 中本聪著名的泰晤士报头条留言
GENESIS_COINBASE_MESSAGE = b"The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"

# 创世区块公钥 (65 字节未压缩公钥)
GENESIS_PUBKEY_HEX = (
    "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc"
    "3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
)

# 历史真实创世区块参数
GENESIS_VERSION = 1
GENESIS_PREV_BLOCK = b'\x00' * 32
GENESIS_TIME = 1231006505           # 2009-01-03 18:15:05 UTC
GENESIS_BITS = 0x1d00ffff           # 初始 PoW 难度
GENESIS_NONCE = 2083236893          # 挖矿得到的黄金 Nonce
GENESIS_REWARD = 50 * 100000000     # 50 BTC (以聪计: 50亿 satoshi)

# 预期历史哈希 (小端序在十六进制中显示为倒序)
EXPECTED_GENESIS_HASH = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
EXPECTED_MERKLE_ROOT = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"


def build_genesis_coinbase_tx() -> bytes:
    """
    构造创世区块的 Coinbase 交易字节流
    格式:
    - nVersion: 4 bytes (1)
    - in_count: 1 byte (1)
    - prevout_hash: 32 bytes (0x00)
    - prevout_index: 4 bytes (0xffffffff)
    - scriptSig: 包含留言 + 难度编码
    - nSequence: 4 bytes (0xffffffff)
    - out_count: 1 byte (1)
    - nValue: 8 bytes (50 BTC = 5,000,000,000 satoshis)
    - scriptPubKey: pubkey + OP_CHECKSIG (0xac)
    - nLockTime: 4 bytes (0)
    """
    # 构造 scriptSig: 包含紧凑 bits 编码 (4字节) + 留言
    # 中本聪原始代码: txin.scriptSig = CScript() << 486604799 << CBigNum(4) << vector<unsigned char>((const unsigned char*)pszTimestamp, ...)
    # 完整原始 scriptSig 字节: 04ffff001d010445 + len + pszTimestamp
    script_sig = (
        b'\x04\xff\xff\x00\x1d\x01\x04\x45' + 
        GENESIS_COINBASE_MESSAGE
    )

    # 构造 scriptPubKey: 65 字节公钥 + 0xac (OP_CHECKSIG)
    pubkey_bytes = bytes.fromhex(GENESIS_PUBKEY_HEX)
    script_pubkey = bytes([len(pubkey_bytes)]) + pubkey_bytes + b'\xac'

    tx = bytearray()
    # 1. nVersion (4 bytes, little-endian)
    tx += struct.pack('<I', GENESIS_VERSION)
    # 2. tx_in count = 1
    tx += b'\x01'
    # 3. prevout hash (32 bytes 0)
    tx += b'\x00' * 32
    # 4. prevout index (0xffffffff)
    tx += struct.pack('<I', 0xffffffff)
    # 5. scriptSig 长度 + 内容
    tx += bytes([len(script_sig)]) + script_sig
    # 6. nSequence (0xffffffff)
    tx += struct.pack('<I', 0xffffffff)
    # 7. tx_out count = 1
    tx += b'\x01'
    # 8. nValue (8 bytes, little-endian) = 50 BTC
    tx += struct.pack('<Q', GENESIS_REWARD)
    # 9. scriptPubKey 长度 + 内容
    tx += bytes([len(script_pubkey)]) + script_pubkey
    # 10. nLockTime (4 bytes) = 0
    tx += struct.pack('<I', 0)

    return bytes(tx)

def build_block_header(
    version: int,
    prev_hash: bytes,
    merkle_root: bytes,
    timestamp: int,
    bits: int,
    nonce: int
) -> bytes:
    """构造标准的 80 字节比特币区块头 (Block Header)"""
    return struct.pack(
        '<I32s32sIII',
        version,
        prev_hash,
        merkle_root,
        timestamp,
        bits,
        nonce
    )

def verify_genesis_block() -> Dict[str, Any]:
    """
    一键复算并验证创世区块：
    1. 构建 Coinbase 交易并计算其双重 SHA256 哈希
    2. 验证 Merkle Root 是否与历史完全一致
    3. 组装 80 字节区块头
    4. 执行双重 SHA256 计算区块哈希，并与中本聪 2009 年公布的创世哈希进行全等比对
    """
    tx_bytes = build_genesis_coinbase_tx()
    # Coinbase 交易的 hash256 即为 Merkle Root (单笔交易时)
    tx_hash = hash256(tx_bytes)
    # 转换为小端倒序显示为人类可读 hex
    merkle_root_hex = tx_hash[::-1].hex()

    # 组装 80 字节区块头 (注意 merkle_root 直接以原始小端字节传入)
    header_bytes = build_block_header(
        version=GENESIS_VERSION,
        prev_hash=GENESIS_PREV_BLOCK,
        merkle_root=tx_hash,
        timestamp=GENESIS_TIME,
        bits=GENESIS_BITS,
        nonce=GENESIS_NONCE
    )

    # 计算区块哈希
    block_hash_raw = hash256(header_bytes)
    block_hash_hex = block_hash_raw[::-1].hex()

    is_merkle_match = (merkle_root_hex == EXPECTED_MERKLE_ROOT)
    is_hash_match = (block_hash_hex == EXPECTED_GENESIS_HASH)

    return {
        "success": is_merkle_match and is_hash_match,
        "coinbase_tx_len": len(tx_bytes),
        "merkle_root_hex": merkle_root_hex,
        "expected_merkle": EXPECTED_MERKLE_ROOT,
        "is_merkle_match": is_merkle_match,
        "block_header_len": len(header_bytes),
        "calculated_hash": block_hash_hex,
        "expected_hash": EXPECTED_GENESIS_HASH,
        "is_hash_match": is_hash_match,
        "timestamp_utc": "2009-01-03 18:15:05 UTC",
        "golden_nonce": GENESIS_NONCE,
        "headline": GENESIS_COINBASE_MESSAGE.decode('ascii')
    }

