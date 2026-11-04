"""
比特币模拟器 - 区块链账本状态与分叉重组引擎 (Blockchain State & Reorg Engine)
实现完整 UTXO 集合维护、最长链法则 (Longest-Chain Rule) 与分叉深度重组 (Chain Reorganization)
"""

from typing import Dict, List, Tuple, Optional
from .block import Block, compute_merkle_root
from .transaction import Transaction, TxIn, TxOut

class Blockchain:
    def __init__(self, difficulty_zeros: int = 3):
        self.difficulty_zeros = difficulty_zeros
        self.blocks_by_hash: Dict[str, Block] = {}
        self.block_height_by_hash: Dict[str, int] = {}
        
        # 激活的最长主链
        self.tip_hash: str = ""
        self.active_chain: List[str] = [] # 从高度 0 开始的区块哈希列表
        
        # 主链当前的全局 UTXO 集合: (txid, out_index) -> TxOut
        self.utxo_set: Dict[Tuple[str, int], TxOut] = {}
        
        # 初始化创世区块
        self._create_genesis_block()

    def _create_genesis_block(self):
        cb_tx = Transaction.create_coinbase(
            miner_address="1SatoshiGenesisAddress111111111111",
            reward=50 * 100000000,
            height=0,
            timestamp=1231006505.0
        )
        genesis_block = Block(
            height=0,
            prev_block_hash="0" * 64,
            transactions=[cb_tx],
            difficulty_zeros=self.difficulty_zeros,
            timestamp=1231006505.0
        )
        # 挖矿创世块
        genesis_block.mine()
        
        g_hash = genesis_block.hash
        self.blocks_by_hash[g_hash] = genesis_block
        self.block_height_by_hash[g_hash] = 0
        self.tip_hash = g_hash
        self.active_chain = [g_hash]
        
        # 应用创世区块交易至 UTXO
        self._apply_txs_to_utxo(genesis_block.transactions, self.utxo_set)

    def _apply_txs_to_utxo(self, txs: List[Transaction], utxos: Dict[Tuple[str, int], TxOut]):
        """在给定 UTXO 集合上应用交易（消耗旧 UTXO，生成新 UTXO）"""
        for tx in txs:
            if not tx.is_coinbase:
                for inp in tx.inputs:
                    utxos.pop(inp.utxo_key, None)
            for out_idx, out in enumerate(tx.outputs):
                utxos[(tx.txid, out_idx)] = out

    def get_tip_block(self) -> Block:
        return self.blocks_by_hash[self.tip_hash]

    @property
    def current_height(self) -> int:
        return len(self.active_chain) - 1

    def validate_transaction(self, tx: Transaction, custom_utxo: Optional[Dict[Tuple[str, int], TxOut]] = None) -> Tuple[bool, str]:
        """对交易进行合法性与防双花核验"""
        utxos = self.utxo_set if custom_utxo is None else custom_utxo
        if tx.is_coinbase:
            return True, "Coinbase tx is valid"

        if not tx.inputs or not tx.outputs:
            return False, "Transaction inputs or outputs cannot be empty"

        in_sum = 0
        used_inputs = set()
        for inp in tx.inputs:
            if inp.utxo_key in used_inputs:
                return False, f"Double spend within same tx on {inp.utxo_key}"
            used_inputs.add(inp.utxo_key)

            if inp.utxo_key not in utxos:
                return False, f"Input UTXO not found or already spent: {inp.utxo_key}"

            in_sum += utxos[inp.utxo_key].value

        out_sum = sum(out.value for out in tx.outputs)
        if out_sum > in_sum:
            return False, f"Output sum ({out_sum}) exceeds input sum ({in_sum})"

        return True, "Valid"

    def get_branch_blocks(self, leaf_hash: str) -> List[Block]:
        """从某个区块向上回溯至创世块"""
        branch = []
        curr = leaf_hash
        while curr in self.blocks_by_hash:
            b = self.blocks_by_hash[curr]
            branch.append(b)
            if b.height == 0:
                break
            curr = b.header.prev_block_hash
        return list(reversed(branch))

    def add_block(self, block: Block) -> Tuple[bool, str, Dict]:
        """
        向区块链账本中注入新区块：
        1. 验证 PoW 有效性
        2. 验证父区块是否存在
        3. 依照中本聪共识（最长链法则），如果该分支高度超过当前主链，触发【分叉重组 (Reorganization)】
        """
        # 1. 验证 PoW
        if not block.is_valid_pow():
            return False, "Invalid Proof-of-Work", {}

        prev_hash = block.header.prev_block_hash
        if prev_hash not in self.blocks_by_hash:
            return False, f"Orphan block: parent {prev_hash} not found", {}

        prev_block = self.blocks_by_hash[prev_hash]
        if block.height != prev_block.height + 1:
            return False, f"Invalid block height: expected {prev_block.height + 1}, got {block.height}", {}

        # 记录区块
        self.blocks_by_hash[block.hash] = block
        self.block_height_by_hash[block.hash] = block.height

        reorg_info = {
            "reorg_triggered": False,
            "orphaned_blocks": [],
            "reclaimed_txs": [],
            "applied_blocks": []
        }

        # 检查是否是在当前主链顶端正常延伸
        if prev_hash == self.tip_hash:
            # 正常线性延伸
            is_valid, reason = self._validate_block_txs(block, self.utxo_set)
            if not is_valid:
                return False, f"Block tx validation failed: {reason}", {}

            self._apply_txs_to_utxo(block.transactions, self.utxo_set)
            self.tip_hash = block.hash
            self.active_chain.append(block.hash)
            return True, "Appended to main tip", reorg_info

        # 如果属于侧链/竞争链
        new_branch_height = block.height
        current_tip_height = self.current_height

        if new_branch_height > current_tip_height:
            # 竞争链高度超越主链，必须触发【分叉重组】！
            success, msg = self._reorganize_chain(block.hash, reorg_info)
            if not success:
                return False, f"Reorg failed: {msg}", reorg_info
            return True, "Chain reorganization executed successfully", reorg_info
        else:
            # 分叉链尚未超过主链，仅作为分叉分支暂存
            return True, f"Saved as fork block at height {block.height} (main chain height is {current_tip_height})", reorg_info

    def _validate_block_txs(self, block: Block, utxos: Dict[Tuple[str, int], TxOut]) -> Tuple[bool, str]:
        temp_utxo = dict(utxos)
        for idx, tx in enumerate(block.transactions):
            if idx == 0:
                if not tx.is_coinbase:
                    return False, "First transaction must be coinbase"
            else:
                if tx.is_coinbase:
                    return False, "Only first transaction can be coinbase"
                ok, reason = self.validate_transaction(tx, temp_utxo)
                if not ok:
                    return False, reason
            self._apply_txs_to_utxo([tx], temp_utxo)
        return True, "Valid"

    def _reorganize_chain(self, new_tip_hash: str, reorg_info: Dict) -> Tuple[bool, str]:
        """
        执行分叉重组：
        1. 寻找主链与新分支的最近共同祖先 (Common Ancestor)
        2. 回滚从当前 tip 到共同祖先之间的旧区块（孤块化，释放交易）
        3. 重建 UTXO 集合
        4. 前进应用从共同祖先到 new_tip 之间的新区块
        5. 切换主链 tip
        """
        old_chain_blocks = self.get_branch_blocks(self.tip_hash)
        new_chain_blocks = self.get_branch_blocks(new_tip_hash)

        # 找共同祖先
        ancestor_idx = 0
        min_len = min(len(old_chain_blocks), len(new_chain_blocks))
        while ancestor_idx < min_len and old_chain_blocks[ancestor_idx].hash == new_chain_blocks[ancestor_idx].hash:
            ancestor_idx += 1

        common_ancestor_height = ancestor_idx - 1
        
        # 被孤块化的区块 (Orphaned Blocks)
        orphaned = old_chain_blocks[ancestor_idx:]
        applied = new_chain_blocks[ancestor_idx:]

        # 重建 UTXO：从共同祖先重新演算
        rebuilt_utxo: Dict[Tuple[str, int], TxOut] = {}
        for b in new_chain_blocks[:ancestor_idx]:
            self._apply_txs_to_utxo(b.transactions, rebuilt_utxo)

        # 逐步验证并应用新分支区块
        for b in applied:
            ok, reason = self._validate_block_txs(b, rebuilt_utxo)
            if not ok:
                return False, f"Block {b.hash} in new branch is invalid: {reason}"
            self._apply_txs_to_utxo(b.transactions, rebuilt_utxo)

        # 收集被废弃区块中的普通交易，以备放回 mempool
        reclaimed_txs = []
        for b in orphaned:
            for tx in b.transactions:
                if not tx.is_coinbase:
                    reclaimed_txs.append(tx)

        # 正式切换状态
        self.utxo_set = rebuilt_utxo
        self.tip_hash = new_tip_hash
        self.active_chain = [b.hash for b in new_chain_blocks]

        reorg_info["reorg_triggered"] = True
        reorg_info["orphaned_blocks"] = [b.hash for b in orphaned]
        reorg_info["applied_blocks"] = [b.hash for b in applied]
        reorg_info["reclaimed_txs"] = reclaimed_txs
        reorg_info["common_ancestor_height"] = common_ancestor_height

        return True, "Reorg success"
