"""
比特币模拟器 - P2P 网络节点与独立矿工实现 (P2P Node & Miner)
每个节点拥有独立的本地区块链拷贝、交易内存池 (Mempool)、钱包密钥与 Gossip 广播逻辑
"""

import time
from typing import Dict, List, Optional, Tuple
from .crypto_util import generate_keypair
from .transaction import Transaction, TxIn, TxOut
from .block import Block
from .blockchain import Blockchain

class Node:
    def __init__(self, node_id: str, difficulty_zeros: int = 3):
        self.node_id = node_id
        self.privkey, self.pubkey, self.address = generate_keypair()
        self.blockchain = Blockchain(difficulty_zeros=difficulty_zeros)
        self.mempool: Dict[str, Transaction] = {}
        self.peers: List['Node'] = []
        self.logs: List[str] = []

    def log(self, msg: str):
        log_line = f"[{self.node_id}] {msg}"
        self.logs.append(log_line)

    def connect(self, peer: 'Node'):
        if peer not in self.peers and peer != self:
            self.peers.append(peer)
            peer.peers.append(self)
            self.log(f"已与节点 [{peer.node_id}] 建立 P2P 双向连接")

    def get_balance(self) -> int:
        """从当前激活主链的 UTXO 集合中计算属于本节点的未花费余额 (单位: 聪 satoshis)"""
        bal = 0
        for (txid, out_idx), out in self.blockchain.utxo_set.items():
            if out.recipient_address == self.address:
                bal += out.value
        return bal

    def create_transaction(self, recipient_address: str, amount: int, fee: int = 1000) -> Optional[Transaction]:
        """从本地可用 UTXO 中组装并签名一笔新交易"""
        needed = amount + fee
        collected = 0
        inputs: List[TxIn] = []

        # 查找可用 UTXO
        for (txid, out_idx), out in self.blockchain.utxo_set.items():
            if out.recipient_address == self.address:
                # 检查该 UTXO 是否已在当前 mempool 的已有交易中被引用
                is_spent_in_mempool = any(
                    any(inp.utxo_key == (txid, out_idx) for inp in m_tx.inputs)
                    for m_tx in self.mempool.values()
                )
                if not is_spent_in_mempool:
                    collected += out.value
                    inputs.append(TxIn(prev_txid=txid, out_index=out_idx, signature="VALID_SIG", pubkey=self.pubkey))
                    if collected >= needed:
                        break

        if collected < needed:
            self.log(f"余额不足: 需要 {needed} satoshis, 可用仅 {collected} satoshis")
            return None

        outputs: List[TxOut] = [TxOut(value=amount, recipient_address=recipient_address)]
        # 找零
        change = collected - needed
        if change > 0:
            outputs.append(TxOut(value=change, recipient_address=self.address))

        tx = Transaction(inputs=inputs, outputs=outputs)
        self.receive_transaction(tx, broadcast=True)
        return tx

    def receive_transaction(self, tx: Transaction, broadcast: bool = True) -> bool:
        """接收并核验一笔交易，校验防双花与资金合法性后存入本地 mempool 并向对等邻居广播"""
        if tx.txid in self.mempool:
            return False

        ok, reason = self.blockchain.validate_transaction(tx)
        if not ok:
            self.log(f"拒绝非法交易 {tx.txid[:10]}... 原因: {reason}")
            return False

        # 检查是否与本地内存池中的其他交易冲突 (Mempool Double Spend Check)
        for inp in tx.inputs:
            for existing_tx in self.mempool.values():
                for ex_inp in existing_tx.inputs:
                    if inp.utxo_key == ex_inp.utxo_key:
                        self.log(f"拦截内存池双花冲突: UTXO {inp.utxo_key} 已被待处理交易 {existing_tx.txid[:8]} 占用")
                        return False

        self.mempool[tx.txid] = tx
        self.log(f"交易 {tx.txid[:8]}... 成功通过校验并入库 Mempool (当前池大小: {len(self.mempool)})")

        if broadcast:
            for peer in self.peers:
                peer.receive_transaction(tx, broadcast=False)
        return True

    def mine_block(self, max_tx_count: int = 10, broadcast: bool = True) -> Optional[Block]:
        """打包 Mempool 中的交易并进行 PoW 挖矿"""
        parent_block = self.blockchain.get_tip_block()
        new_height = parent_block.height + 1

        # 1. 创建矿工奖励 Coinbase 交易 (50 BTC)
        cb_tx = Transaction.create_coinbase(
            miner_address=self.address,
            reward=50 * 100000000,
            height=new_height
        )

        # 2. 选取合规交易
        selected_txs = [cb_tx]
        for txid, tx in list(self.mempool.items())[:max_tx_count]:
            ok, _ = self.blockchain.validate_transaction(tx)
            if ok:
                selected_txs.append(tx)

        # 3. 构造区块
        new_block = Block(
            height=new_height,
            prev_block_hash=parent_block.hash,
            transactions=selected_txs,
            difficulty_zeros=self.blockchain.difficulty_zeros
        )

        # 4. 执行工作量证明挖矿
        self.log(f"开始在高度 #{new_height} 进行 PoW 挖矿寻优...")
        start_t = time.time()
        success = new_block.mine()
        elapsed = time.time() - start_t

        if not success:
            self.log("挖矿超时未找到黄金 Nonce")
            return None

        self.log(f"恭喜挖出新区块 #{new_height}! 哈希: {new_block.hash[:16]}... (Nonce: {new_block.header.nonce}, 耗时: {elapsed:.3f}s)")

        # 5. 应用到本地主链
        ok, msg, reorg_info = self.blockchain.add_block(new_block)
        if not ok:
            self.log(f"本地提交区块异常: {msg}")
            return None

        # 6. 从 Mempool 中剔除已上链的交易
        for tx in selected_txs:
            self.mempool.pop(tx.txid, None)

        # 7. 全网 Gossip 广播
        if broadcast:
            for peer in self.peers:
                peer.receive_block(new_block, broadcast=True)

        return new_block

    def receive_block(self, block: Block, broadcast: bool = True) -> bool:
        """接收邻居节点广播的新区块，并依照中本聪最长链规则更新本地账本"""
        if block.hash in self.blockchain.blocks_by_hash:
            return False

        ok, msg, reorg_info = self.blockchain.add_block(block)
        if not ok:
            self.log(f"拒绝非法或失效区块 #{block.height} ({block.hash[:8]}...): {msg}")
            return False

        if reorg_info.get("reorg_triggered"):
            self.log(f"⚠️ 触发【分叉重组 (Chain Reorganization)】!")
            self.log(f"   回滚孤块数量: {len(reorg_info['orphaned_blocks'])}, 应用新分支区块数: {len(reorg_info['applied_blocks'])}")
            self.log(f"   新主链高度更新为: #{self.blockchain.current_height}, Tip: {self.blockchain.tip_hash[:12]}...")
            # 将孤立块中的交易放回 mempool
            for reclaimed_tx in reorg_info.get("reclaimed_txs", []):
                self.mempool[reclaimed_tx.txid] = reclaimed_tx
                self.log(f"   交易 {reclaimed_tx.txid[:8]}... 从孤立块回流至 Mempool")
        else:
            self.log(f"成功接收区块 #{block.height} ({block.hash[:12]}...), 本地主链高度: #{self.blockchain.current_height}")

        # 清除已入块交易
        for tx in block.transactions:
            self.mempool.pop(tx.txid, None)

        if broadcast:
            for peer in self.peers:
                peer.receive_block(block, broadcast=True)

        return True

