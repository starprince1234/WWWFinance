"""
比特币模拟器 - 区块结构、默克尔树与 PoW 挖矿 (Block & Merkle Tree)
包含区块头构造、Merkle Root 树形计算、工作量证明与区块哈希
"""

import time
from typing import List, Optional
from .crypto_util import hash256
from .transaction import Transaction

def compute_merkle_root(tx_ids: List[str]) -> str:
    """计算交易列表的 Merkle 根 (Merkle Root)"""
    if not tx_ids:
        return "0" * 64
    if len(tx_ids) == 1:
        return tx_ids[0]

    current_layer = [bytes.fromhex(t)[::-1] for t in tx_ids]
    while len(current_layer) > 1:
        # 如果当前层为奇数，将最后一个元素复制一份凑成偶数
        if len(current_layer) % 2 != 0:
            current_layer.append(current_layer[-1])
        next_layer = []
        for i in range(0, len(current_layer), 2):
            combined = current_layer[i] + current_layer[i + 1]
            next_layer.append(hash256(combined))
        current_layer = next_layer

    return current_layer[0][::-1].hex()


class BlockHeader:
    def __init__(self, version: int, prev_block_hash: str, merkle_root: str, timestamp: float, difficulty_zeros: int, nonce: int = 0):
        self.version = version
        self.prev_block_hash = prev_block_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.difficulty_zeros = difficulty_zeros
        self.nonce = nonce

    def to_string(self) -> str:
        return f"{self.version}_{self.prev_block_hash}_{self.merkle_root}_{self.timestamp}_{self.difficulty_zeros}_{self.nonce}"

    def compute_hash(self) -> str:
        """计算区块头双重 SHA256 哈希"""
        raw = self.to_string().encode('utf-8')
        return hash256(raw)[::-1].hex()


class Block:
    def __init__(self, height: int, prev_block_hash: str, transactions: List[Transaction], difficulty_zeros: int = 3, timestamp: Optional[float] = None):
        self.height = height
        self.transactions = transactions
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.difficulty_zeros = difficulty_zeros

        tx_ids = [tx.txid for tx in transactions]
        merkle_root = compute_merkle_root(tx_ids)

        self.header = BlockHeader(
            version=1,
            prev_block_hash=prev_block_hash,
            merkle_root=merkle_root,
            timestamp=self.timestamp,
            difficulty_zeros=difficulty_zeros,
            nonce=0
        )
        self.hash = self.header.compute_hash()

    def mine(self, max_nonce: int = 2000000) -> bool:
        """
        进行工作量证明寻优 (PoW 挖矿):
        寻找使区块哈希满足指定前导零数量的 Nonce
        """
        prefix = "0" * self.difficulty_zeros
        while self.header.nonce < max_nonce:
            h = self.header.compute_hash()
            if h.startswith(prefix):
                self.hash = h
                return True
            self.header.nonce += 1
        return False

    def is_valid_pow(self) -> bool:
        """校验 PoW 是否有效"""
        prefix = "0" * self.difficulty_zeros
        return self.header.compute_hash() == self.hash and self.hash.startswith(prefix)

    def to_dict(self) -> dict:
        return {
            "height": self.height,
            "hash": self.hash,
            "prev_hash": self.header.prev_block_hash,
            "merkle_root": self.header.merkle_root,
            "nonce": self.header.nonce,
            "difficulty": self.difficulty_zeros,
            "tx_count": len(self.transactions),
            "timestamp": self.timestamp
        }
