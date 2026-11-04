"""
中本聪原始交易结构与 UTXO 验证模型 (Transaction & UTXO Model)
实现 v0.1 源码中的 CTransaction 序列化、反序列化、SIGHASH 签名哈希计算与完整解锁验证
"""

import struct
from typing import List, Tuple, Dict, Any, Optional
from .crypto import hash256, ecdsa_sign, encode_der
from .script_engine import (
    ScriptEngine,
    OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG
)

def encode_varint(n: int) -> bytes:
    """比特币变长整数 (CompactSize / VarInt) 编码"""
    if n < 0xfd:
        return bytes([n])
    elif n <= 0xffff:
        return b'\xfd' + struct.pack('<H', n)
    elif n <= 0xffffffff:
        return b'\xfe' + struct.pack('<I', n)
    else:
        return b'\xff' + struct.pack('<Q', n)

def decode_varint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """比特币变长整数解码，返回 (数值, 占用字节长度)"""
    first = data[offset]
    if first < 0xfd:
        return first, 1
    elif first == 0xfd:
        return struct.unpack_from('<H', data, offset + 1)[0], 3
    elif first == 0xfe:
        return struct.unpack_from('<I', data, offset + 1)[0], 5
    else:
        return struct.unpack_from('<Q', data, offset + 1)[0], 9


class TxIn:
    """交易输入 (CTxIn)"""
    def __init__(self, prev_tx_hash: bytes, prev_index: int, script_sig: bytes = b'', sequence: int = 0xffffffff):
        self.prev_tx_hash = prev_tx_hash  # 32 字节小端序
        self.prev_index = prev_index      # 4 字节无符号整数
        self.script_sig = script_sig      # 解锁脚本字节
        self.sequence = sequence          # 4 字节序列号

    def serialize(self) -> bytes:
        res = bytearray()
        res += self.prev_tx_hash
        res += struct.pack('<I', self.prev_index)
        res += encode_varint(len(self.script_sig))
        res += self.script_sig
        res += struct.pack('<I', self.sequence)
        return bytes(res)


class TxOut:
    """交易输出 (CTxOut)"""
    def __init__(self, value: int, script_pubkey: bytes):
        self.value = value                  # 8 字节金额 (聪 / satoshi)
        self.script_pubkey = script_pubkey  # 锁定脚本字节

    def serialize(self) -> bytes:
        res = bytearray()
        res += struct.pack('<Q', self.value)
        res += encode_varint(len(self.script_pubkey))
        res += self.script_pubkey
        return bytes(res)


class Transaction:
    """中本聪 v0.1 核心交易对象 (CTransaction)"""
    def __init__(self, version: int = 1, locktime: int = 0):
        self.version = version
        self.vin: List[TxIn] = []
        self.vout: List[TxOut] = []
        self.locktime = locktime

    def add_input(self, prev_tx_hash: bytes, prev_index: int, script_sig: bytes = b'', sequence: int = 0xffffffff):
        self.vin.append(TxIn(prev_tx_hash, prev_index, script_sig, sequence))

    def add_output(self, value: int, script_pubkey: bytes):
        self.vout.append(TxOut(value, script_pubkey))

    def serialize(self) -> bytes:
        """完整交易二进制序列化"""
        res = bytearray()
        res += struct.pack('<I', self.version)
        res += encode_varint(len(self.vin))
        for tx_in in self.vin:
            res += tx_in.serialize()
        res += encode_varint(len(self.vout))
        for tx_out in self.vout:
            res += tx_out.serialize()
        res += struct.pack('<I', self.locktime)
        return bytes(res)

    def txid(self) -> str:
        """计算交易 ID (即序列化后的双重 SHA256，以小端逆序十六进制表示)"""
        return hash256(self.serialize())[::-1].hex()

    def signature_hash(self, input_index: int, prev_script_pubkey: bytes, hash_type: int = 1) -> bytes:
        """
        中本聪 v0.1 SignatureHash 计算算法 (SIGHASH_ALL):
        1. 复制原交易
        2. 清空所有输入的 script_sig，仅将当前待签名 input 的 script_sig 替换为引用输出的 prev_script_pubkey
        3. 在序列化数据末尾追加 4 字节的 hash_type (0x01000000)
        4. 进行双重 SHA-256 哈希
        """
        copy_tx = Transaction(self.version, self.locktime)
        for i, tx_in in enumerate(self.vin):
            script = prev_script_pubkey if i == input_index else b''
            copy_tx.add_input(tx_in.prev_tx_hash, tx_in.prev_index, script, tx_in.sequence)
        for tx_out in self.vout:
            copy_tx.add_output(tx_out.value, tx_out.script_pubkey)

        serialized = copy_tx.serialize() + struct.pack('<I', hash_type)
        return hash256(serialized)


def build_p2pkh_script_pubkey(pubkey_hash160: bytes) -> bytes:
    """构造标准 P2PKH 锁定脚本: OP_DUP OP_HASH160 <hash160> OP_EQUALVERIFY OP_CHECKSIG"""
    return (
        bytes([OP_DUP, OP_HASH160, len(pubkey_hash160)]) +
        pubkey_hash160 +
        bytes([OP_EQUALVERIFY, OP_CHECKSIG])
    )

def parse_script_tokens(script_bytes: bytes) -> List[Any]:
    """将脚本二进制字节解析为操作码与数据列表"""
    tokens = []
    i = 0
    n = len(script_bytes)
    while i < n:
        op = script_bytes[i]
        if 1 <= op <= 75:  # 直接推入 1~75 字节数据
            data = script_bytes[i + 1 : i + 1 + op]
            tokens.append(data)
            i += 1 + op
        else:
            tokens.append(op)
            i += 1
    return tokens
