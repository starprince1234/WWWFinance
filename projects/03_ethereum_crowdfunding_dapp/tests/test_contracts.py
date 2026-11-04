"""
以太坊众筹 DAPP 智能合约自动化测试套件 (Test Decentralized Crowdfund Contract)
涵盖众筹发起、出资、撤单、未达标全额退款、里程碑 DAO 投票拨款全流程
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evm_simulator import DecentralizedCrowdfundSimulator, MockAccount, EvmRevert

def test_campaign_pledge_and_unpledge():
    print("\n--- 1. 测试项目发起、出资与众筹期内撤回 ---")
    dapp = DecentralizedCrowdfundSimulator()
    creator = MockAccount("0xCreator11111111111111111111111111111111")
    alice = MockAccount("0xAlice2222222222222222222222222222222222")

    # 1. 发起 10 ETH 众筹，周期 7 天 (604800 秒)
    cid = dapp.launch(creator, "Web3 开源硬件", "研发去中心化物联网硬件", goal_eth=10.0, duration_seconds=604800)
    assert cid == 1

    # 2. Alice 出资 6 ETH
    dapp.pledge(alice, cid, 6.0)
    assert dapp.campaigns[cid]["total_pledged"] == 6 * 10**18
    assert alice.balance_eth == 94.0

    # 3. Alice 撤回 2 ETH
    dapp.unpledge(alice, cid, 2.0)
    assert dapp.campaigns[cid]["total_pledged"] == 4 * 10**18
    assert alice.balance_eth == 96.0
    print(">>> 出资与撤回测试通过 (PASS)")


def test_failed_campaign_full_refund():
    print("\n--- 2. 测试众筹未达标全额退款机制 (Refund) ---")
    dapp = DecentralizedCrowdfundSimulator()
    creator = MockAccount("0xCreator11111111111111111111111111111111")
    bob = MockAccount("0xBob33333333333333333333333333333333333333", initial_balance_eth=50.0)

    # 目标 20 ETH，为期 3 天
    cid = dapp.launch(creator, "独立游戏开发", "基于虚幻引擎的RPG游戏", goal_eth=20.0, duration_seconds=3 * 86400)

    # Bob 仅支持了 8 ETH (未达标)
    dapp.pledge(bob, cid, 8.0)
    assert bob.balance_eth == 42.0

    # 时间推移 4 天 (跨越截止日期)
    dapp.advance_time(4 * 86400)

    # Bob 申请全额退款
    dapp.refund(bob, cid)
    assert bob.balance_eth == 50.0, "退款后余额应完全恢复"
    assert dapp.pledged_amount[cid][bob.address] == 0
    print(">>> 未达标退款测试通过 (PASS)")


def test_milestone_dao_governance():
    print("\n--- 3. 测试里程碑资金拨款 DAO 治理 (防卷款跑路) ---")
    dapp = DecentralizedCrowdfundSimulator()
    creator = MockAccount("0xCreator11111111111111111111111111111111")
    alice = MockAccount("0xAlice2222222222222222222222222222222222", initial_balance_eth=100.0)
    bob = MockAccount("0xBob33333333333333333333333333333333333333", initial_balance_eth=100.0)
    supplier = MockAccount("0xSupplier44444444444444444444444444444444", initial_balance_eth=0.0)

    # 目标 10 ETH
    cid = dapp.launch(creator, "绿色能源众筹", "分布式微电网储能站", goal_eth=10.0, duration_seconds=86400)

    # Alice 投资 7 ETH (占比 70%)，Bob 投资 3 ETH (占比 30%) -> 总额 10 ETH (达标)
    dapp.pledge(alice, cid, 7.0)
    dapp.pledge(bob, cid, 3.0)

    # 众筹结束
    dapp.advance_time(86401)

    # 发起人申请第 1 期用款 4 ETH 采购电池模组
    mid = dapp.propose_milestone(creator, cid, "采购第1期储能锂电池", amount_eth=4.0, recipient=supplier.address)

    # 测试防冒充：若未达半数投票，不可拨款
    try:
        dapp.execute_milestone(cid, mid, supplier)
        assert False, "赞成票不足应被驳回"
    except EvmRevert as e:
        print(f"    [√] 成功拦截未达半数投票的提款: {e}")

    # Alice (持有 70% 投票权) 投赞成票
    dapp.vote_milestone(alice, cid, mid)

    # 执行拨款
    dapp.execute_milestone(cid, mid, supplier)
    assert supplier.balance_eth == 4.0, "供应商应顺利收到 4 ETH 货款"
    print(">>> 里程碑 DAO 治理与投票拨款测试通过 (PASS)")

if __name__ == '__main__':
    test_campaign_pledge_and_unpledge()
    test_failed_campaign_full_refund()
    test_milestone_dao_governance()
