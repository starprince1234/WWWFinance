"""
以太坊众筹 DAPP - EVM 状态机模拟器 (Pure Python EVM-Equivalent State Machine)
精确复现 Solidity 智能合约中的存储布局、msg.sender/msg.value、自定义错误与转账原子性
"""

import time
from typing import Dict, List, Any, Optional

WEI_PER_ETH = 10**18

class EvmRevert(Exception):
    """模拟 EVM Revert 异常"""
    pass

class MockAccount:
    def __init__(self, address: str, initial_balance_eth: float = 100.0):
        self.address = address
        self.balance_wei = int(initial_balance_eth * WEI_PER_ETH)

    @property
    def balance_eth(self) -> float:
        return self.balance_wei / WEI_PER_ETH


class DecentralizedCrowdfundSimulator:
    """与 Solidity 智能合约 100% 对齐的去中心化众筹合约模拟器"""

    def __init__(self):
        self.campaign_count = 0
        self.campaigns: Dict[int, Dict[str, Any]] = {}
        self.pledged_amount: Dict[int, Dict[str, int]] = {} # campaign_id -> (address -> wei)
        self.milestones: Dict[int, Dict[int, Dict[str, Any]]] = {} # campaign_id -> (m_id -> data)
        self.contract_balance_wei = 0
        self.current_timestamp = int(time.time())
        self.events: List[Dict[str, Any]] = []

    def set_time(self, ts: int):
        """控制区块链当前时间戳 (测试用)"""
        self.current_timestamp = ts

    def advance_time(self, seconds: int):
        """推进区块链时间"""
        self.current_timestamp += seconds

    def launch(self, sender: MockAccount, title: str, description: str, goal_eth: float, duration_seconds: int) -> int:
        if goal_eth <= 0:
            raise EvmRevert("InvalidGoal: 目标金额必须大于0")
        if duration_seconds < 60:
            raise EvmRevert("InvalidDuration: 持续时间过短")

        self.campaign_count += 1
        cid = self.campaign_count
        goal_wei = int(goal_eth * WEI_PER_ETH)

        self.campaigns[cid] = {
            "id": cid,
            "creator": sender.address,
            "title": title,
            "description": description,
            "goal": goal_wei,
            "total_pledged": 0,
            "current_balance": 0,
            "start_at": self.current_timestamp,
            "end_at": self.current_timestamp + duration_seconds,
            "claimed": False,
            "backer_count": 0,
            "milestone_count": 0
        }
        self.pledged_amount[cid] = {}
        self.milestones[cid] = {}

        self.events.append({
            "event": "CampaignLaunched",
            "campaign_id": cid,
            "creator": sender.address,
            "goal_eth": goal_eth
        })
        return cid

    def pledge(self, sender: MockAccount, campaign_id: int, amount_eth: float):
        if campaign_id not in self.campaigns:
            raise EvmRevert("CampaignNotFound")

        c = self.campaigns[campaign_id]
        if self.current_timestamp < c["start_at"] or self.current_timestamp > c["end_at"]:
            raise EvmRevert("CampaignNotActive: 众筹未启动或已截止")

        val_wei = int(amount_eth * WEI_PER_ETH)
        if val_wei <= 0:
            raise EvmRevert("InvalidGoal: 出资金额必须大于0")
        if sender.balance_wei < val_wei:
            raise EvmRevert("InsufficientFunds: 钱包余额不足")

        # 扣减支持者钱包，转入合约
        sender.balance_wei -= val_wei
        self.contract_balance_wei += val_wei

        if sender.address not in self.pledged_amount[campaign_id]:
            self.pledged_amount[campaign_id][sender.address] = 0
            c["backer_count"] += 1

        self.pledged_amount[campaign_id][sender.address] += val_wei
        c["total_pledged"] += val_wei
        c["current_balance"] += val_wei

        self.events.append({
            "event": "Pledged",
            "campaign_id": campaign_id,
            "backer": sender.address,
            "amount_eth": amount_eth
        })

    def unpledge(self, sender: MockAccount, campaign_id: int, amount_eth: float):
        c = self.campaigns[campaign_id]
        if self.current_timestamp > c["end_at"]:
            raise EvmRevert("CampaignEnded: 众筹已截止，无法撤单")

        val_wei = int(amount_eth * WEI_PER_ETH)
        curr_pledged = self.pledged_amount[campaign_id].get(sender.address, 0)
        if curr_pledged < val_wei:
            raise EvmRevert("ExceedsAvailableBalance: 撤资额超出已出资金额")

        self.pledged_amount[campaign_id][sender.address] -= val_wei
        c["total_pledged"] -= val_wei
        c["current_balance"] -= val_wei

        if self.pledged_amount[campaign_id][sender.address] == 0:
            c["backer_count"] -= 1

        self.contract_balance_wei -= val_wei
        sender.balance_wei += val_wei

        self.events.append({
            "event": "Unpledged",
            "campaign_id": campaign_id,
            "backer": sender.address,
            "amount_eth": amount_eth
        })

    def refund(self, sender: MockAccount, campaign_id: int):
        c = self.campaigns[campaign_id]
        if self.current_timestamp <= c["end_at"]:
            raise EvmRevert("CampaignNotActive: 众筹未截止，暂不能退款")
        if c["total_pledged"] >= c["goal"]:
            raise EvmRevert("GoalAlreadyReached: 目标已达成，无法退款")

        bal_wei = self.pledged_amount[campaign_id].get(sender.address, 0)
        if bal_wei == 0:
            raise EvmRevert("NothingToRefund: 无可退款金额")

        self.pledged_amount[campaign_id][sender.address] = 0
        c["current_balance"] -= bal_wei
        self.contract_balance_wei -= bal_wei
        sender.balance_wei += bal_wei

        self.events.append({
            "event": "Refunded",
            "campaign_id": campaign_id,
            "backer": sender.address,
            "amount_eth": bal_wei / WEI_PER_ETH
        })

    def propose_milestone(self, sender: MockAccount, campaign_id: int, desc: str, amount_eth: float, recipient: str) -> int:
        c = self.campaigns[campaign_id]
        if sender.address != c["creator"]:
            raise EvmRevert("NotCreator: 仅项目发起人可提报里程碑")
        if self.current_timestamp <= c["end_at"]:
            raise EvmRevert("CampaignNotActive: 众筹尚未结束")
        if c["total_pledged"] < c["goal"]:
            raise EvmRevert("GoalNotReached: 目标未达成")

        amt_wei = int(amount_eth * WEI_PER_ETH)
        if amt_wei > c["current_balance"]:
            raise EvmRevert("ExceedsAvailableBalance: 申请款项超出合约剩余储备")

        c["milestone_count"] += 1
        mid = c["milestone_count"]
        self.milestones[campaign_id][mid] = {
            "id": mid,
            "desc": desc,
            "amount": amt_wei,
            "recipient": recipient,
            "votes_in_favor": 0,
            "executed": False,
            "voted_backers": set()
        }

        self.events.append({
            "event": "MilestoneProposed",
            "campaign_id": campaign_id,
            "milestone_id": mid,
            "amount_eth": amount_eth
        })
        return mid

    def vote_milestone(self, sender: MockAccount, campaign_id: int, milestone_id: int):
        weight = self.pledged_amount[campaign_id].get(sender.address, 0)
        if weight == 0:
            raise EvmRevert("NotBacker: 只有出资支持者拥有投票权")

        m = self.milestones[campaign_id][milestone_id]
        if m["executed"]:
            raise EvmRevert("MilestoneAlreadyExecuted: 该阶段已拨款")
        if sender.address in m["voted_backers"]:
            raise EvmRevert("AlreadyVoted: 重复投票")

        m["voted_backers"].add(sender.address)
        m["votes_in_favor"] += weight

        self.events.append({
            "event": "MilestoneVoted",
            "campaign_id": campaign_id,
            "milestone_id": milestone_id,
            "voter": sender.address,
            "weight_eth": weight / WEI_PER_ETH
        })

    def execute_milestone(self, campaign_id: int, milestone_id: int, recipient_account: MockAccount):
        c = self.campaigns[campaign_id]
        m = self.milestones[campaign_id][milestone_id]

        if m["executed"]:
            raise EvmRevert("MilestoneAlreadyExecuted: 重复执行")
        if m["votes_in_favor"] * 2 <= c["total_pledged"]:
            raise EvmRevert("InsufficientMilestoneVotes: 赞成票未过半数(>50%)")
        if m["amount"] > c["current_balance"]:
            raise EvmRevert("ExceedsAvailableBalance: 余额不足")

        m["executed"] = true = True
        c["current_balance"] -= m["amount"]
        self.contract_balance_wei -= m["amount"]
        recipient_account.balance_wei += m["amount"]

        self.events.append({
            "event": "MilestoneExecuted",
            "campaign_id": campaign_id,
            "milestone_id": milestone_id,
            "amount_eth": m["amount"] / WEI_PER_ETH,
            "recipient": recipient_account.address
        })

