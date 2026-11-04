"""
比特币模拟器 - 交易与 UTXO 核心模型 (Transaction & UTXO Model)
实现标准交易、Coinbase 铸币交易、双花检测与 UTXO 状态迁移
"""

import time
from typing import List, Dict, Optional, Tuple
from .crypto_util import hash256, sign_data

class TxIn:
    def __init__(self, prev_txid: str, out_index: int, signature: str = "", pubkey: str = ""):
        self.prev_txid = prev_txid
        self.out_index = out_index
        self.signature = signature
        self.pubkey = pubkey

    def to_dict(self) -> dict:
        return {
            "prev_txid": self.prev_txid,
            "out_index": self.out_index,
            "signature": self.signature,
            "pubkey": self.pubkey
        }

    @property
    def utxo_key(self) -> Tuple[str, int]:
        return (self.prev_txid, self.out_index)


class TxOut:
    def __init__(self, value: int, recipient_address: str):
        self.value = value  # satoshis (1 BTC = 100,000,000 satoshis)
        self.recipient_address = recipient_address

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "recipient_address": self.recipient_address
        }


class Transaction:
    def __init__(self, inputs: List[TxIn], outputs: List[TxOut], is_coinbase: bool = False, timestamp: Optional[float] = None):
        self.inputs = inputs
        self.outputs = outputs
        self.is_coinbase = is_coinbase
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.txid = self.calculate_txid()

    def calculate_txid(self) -> str:
        """根据交易的所有输入、输出及时间戳计算唯一的 64 位十六进制哈希"""
        payload = f"{self.is_coinbase}_{self.timestamp}_"
        for inp in self.inputs:
            payload += f"{inp.prev_txid}:{inp.out_index}:{inp.signature};"
        for out in self.outputs:
            payload += f"{out.recipient_address}:{out.value};"
        return hash256(payload.encode('utf-8'))[::-1].hex()

    @classmethod
    def create_coinbase(cls, miner_address: str, reward: int = 50 * 100000000, height: int = 0, timestamp: Optional[float] = None) -> 'Transaction':
        """构造矿工奖励的 Coinbase 交易 (无输入，凭空产生新币)"""
        cb_in = TxIn(prev_txid=f"coinbase_block_{height:08d}", out_index=0, signature="COINBASE_PROOF")
        cb_out = TxOut(value=reward, recipient_address=miner_address)
        return cls(inputs=[cb_in], outputs=[cb_out], is_coinbase=True, timestamp=timestamp)

    def get_fee(self, utxo_set: Dict[Tuple[str, int], TxOut]) -> int:
        """计算矿工费 = 输入总和 - 输出总和"""
        if self.is_coinbase:
            return 0
        in_sum = sum(utxo_set[inp.utxo_key].value for inp in self.inputs if inp.utxo_key in utxo_set)
        out_sum = sum(out.value for out in self.outputs)
        return in_sum - out_sum

    def to_dict(self) -> dict:
        return {
            "txid": self.txid,
            "is_coinbase": self.is_coinbase,
            "timestamp": self.timestamp,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs]
        }
