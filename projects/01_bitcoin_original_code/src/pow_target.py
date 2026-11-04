"""
中本聪工作量证明与难度目标计算模块 (Proof-of-Work & Target Mechanics)
实现 v0.1 源码中的 nBits 紧凑编码转换、挖矿哈希判定与 2016 区块难度调整算法
"""

import time
from typing import Tuple
from .crypto import hash256

# 创世区块初始 PoW 极限 (Genesis Target / PoW Limit)
# 紧凑编码 0x1d00ffff 对应的最大目标值
POW_LIMIT_BITS = 0x1d00ffff

def nbits_to_target(nbits: int) -> int:
    """
    将 32 位紧凑目标值 (Compact Target) 转换为 256 位大整数目标值
    例如: 0x1d00ffff -> 0x00000000FFFF0000000000000000000000000000000000000000000000000000
    公式: Target = Mantissa * 256^(Exponent - 3)
    """
    exponent = (nbits >> 24) & 0xff
    mantissa = nbits & 0x7fffff
    is_negative = (nbits & 0x800000) != 0

    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))

    if is_negative:
        target = -target
    return target

def target_to_nbits(target: int) -> int:
    """
    将 256 位大整数目标值转换为 32 位紧凑编码 (nBits)
    """
    if target <= 0:
        return 0
    
    # 转换为字节序
    size = (target.bit_length() + 7) // 8
    if size <= 3:
        mantissa = target << (8 * (3 - size))
    else:
        mantissa = target >> (8 * (size - 3))

    if mantissa & 0x800000:
        mantissa >>= 8
        size += 1

    return (size << 24) | (mantissa & 0x7fffff)

GENESIS_TARGET = nbits_to_target(POW_LIMIT_BITS)

def calculate_difficulty(current_target: int) -> float:
    """计算当前难度: Difficulty = GenesisTarget / CurrentTarget"""
    if current_target <= 0:
        return 0.0
    return float(GENESIS_TARGET) / float(current_target)


# ==========================================
# 难度调整机制 (Satoshi v0.1 Difficulty Adjustment)
# ==========================================

TARGET_TIMESPAN = 14 * 24 * 60 * 60  # 两周 (1209600 秒)
TARGET_SPACING = 10 * 60            # 10 分钟 (600 秒)
INTERVAL = TARGET_TIMESPAN // TARGET_SPACING # 2016 个区块

def adjust_difficulty(last_nbits: int, actual_timespan: int) -> int:
    """
    中本聪 v0.1 源码中的难度调整逻辑 (每 2016 个区块调整一次):
    1. 限制实际用时在 [0.25 * 目标用时, 4 * 目标用时] 之间 (防止单次剧烈波动)
    2. 新目标值 = 旧目标值 * 实际用时 / 目标用时
    3. 不能超过创世 PoW 极限 (POW_LIMIT)
    """
    # 限制实际时间跨度在 [3.5 天, 56 天]
    if actual_timespan < TARGET_TIMESPAN // 4:
        actual_timespan = TARGET_TIMESPAN // 4
    if actual_timespan > TARGET_TIMESPAN * 4:
        actual_timespan = TARGET_TIMESPAN * 4

    old_target = nbits_to_target(last_nbits)
    new_target = (old_target * actual_timespan) // TARGET_TIMESPAN

    if new_target > GENESIS_TARGET:
        new_target = GENESIS_TARGET

    return target_to_nbits(new_target)


# ==========================================
# 挖矿 PoW 计算循环 (Satoshi ScanHash 模拟)
# ==========================================

def check_proof_of_work(block_hash_bytes: bytes, nbits: int) -> bool:
    """
    校验区块哈希是否满足目标难度要求
    在比特币中，哈希值被视为小端序整数 (Little-Endian)
    即 256 位整数值必须 <= Target
    """
    target = nbits_to_target(nbits)
    hash_int = int.from_bytes(block_hash_bytes, 'little')
    return hash_int <= target

def mine_block(header_prefix_bytes: bytes, nbits: int, start_nonce: int = 0, max_tries: int = 1000000) -> Tuple[bool, int, bytes, int]:
    """
    模拟中本聪 ScanHash 挖矿寻优循环
    返回: (成功状态, 成功nonce, 区块双重哈希, 尝试总次数)
    """
    target = nbits_to_target(nbits)
    nonce = start_nonce
    tries = 0

    while tries < max_tries:
        header = header_prefix_bytes + nonce.to_bytes(4, 'little')
        # 比特币双重 SHA256
        h = hash256(header)
        h_int = int.from_bytes(h, 'little')

        if h_int <= target:
            return True, nonce, h, tries + 1

        nonce = (nonce + 1) & 0xffffffff
        tries += 1

    return False, nonce, b'', tries

