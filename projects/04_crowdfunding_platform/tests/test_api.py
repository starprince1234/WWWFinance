"""
众筹平台全栈工程 - 接口与清结算系统自动化测试套件 (Test Crowdfund API & Settlement)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import init_db, get_db_connection
from src.services import CrowdfundService

def test_full_crowdfunding_lifecycle():
    print("=== 开始众筹平台全生命周期业务与事务测试 ===")
    init_db(drop_existing=True)

    # 1. 注册与登录
    reg_res = CrowdfundService.register_user("inventor_chen", "pass123", role="CREATOR")
    assert reg_res["success"] is True, "发起人注册失败"
    creator_id = reg_res["user_id"]

    reg_backer1 = CrowdfundService.register_user("investor_zhao", "pass123", role="USER")
    backer1_id = reg_backer1["user_id"]

    reg_backer2 = CrowdfundService.register_user("investor_qian", "pass123", role="USER")
    backer2_id = reg_backer2["user_id"]

    print("[*] 1. 用户注册与角色权限分配成功")

    # 2. 发起众筹 (目标 10000 元，期限 30 天)
    camp_res = CrowdfundService.create_campaign(
        creator_id=creator_id,
        title="低功耗智能环境监测仪",
        category="TECH",
        description="基于 LoRaWAN 的农业与室内温湿度多合一物联网监测终端",
        goal_amount=10000.0,
        duration_days=30,
        tiers=[
            {"title": "早鸟体验版", "description": "裸板套件", "price": 299.0, "backer_limit": 50},
            {"title": "量产整机版", "description": "IP67 防水整机", "price": 599.0, "backer_limit": 30}
        ]
    )
    assert camp_res["success"] is True
    cid = camp_res["campaign_id"]
    print(f"[*] 2. 众筹项目创建成功，ID: {cid}")

    # 3. 投资者出资 (Pledge)
    # 投资人 1 出资 6000 元
    p1 = CrowdfundService.pledge(backer1_id, cid, amount=6000.0)
    assert p1["success"] is True

    # 投资人 2 出资 5000 元 -> 总额 11000 元 (已达标超募 110%)
    p2 = CrowdfundService.pledge(backer2_id, cid, amount=5000.0)
    assert p2["success"] is True

    camp_detail = CrowdfundService.get_campaign_detail(cid)
    assert camp_detail["current_amount"] == 11000.0
    assert camp_detail["backer_count"] == 2
    print(f"[*] 3. 出资事务执行成功，当前筹资总额: ¥{camp_detail['current_amount']} (达标率: 110%)")

    # 4. 执行到期清算 (Settlement Engine: 达标放款)
    creator_bal_before = CrowdfundService.get_user_profile(creator_id)["balance"]
    settle_res = CrowdfundService.settle_campaign(cid)
    assert settle_res["success"] is True
    assert settle_res["status"] == "SUCCEEDED"

    # 平台扣除 5% 佣金 (11000 * 0.05 = 550 元)，发起人得 10450 元
    expected_payout = 11000.0 * 0.95
    creator_bal_after = CrowdfundService.get_user_profile(creator_id)["balance"]
    assert creator_bal_after == creator_bal_before + expected_payout
    print(f"[*] 4. 众筹达标清算成功: 总额 ¥11000，扣除 5% 服务费 ¥550，发起人到账 ¥{expected_payout}")

    # 5. 模拟另一个未达标项目的批量自动退款 (All-or-Nothing Refund)
    camp_failed_res = CrowdfundService.create_campaign(
        creator_id=creator_id,
        title="复古朋克机械键盘",
        category="CREATIVE",
        description="全黄铜外壳、纯手工打磨轴体",
        goal_amount=50000.0, # 高门槛
        duration_days=7,
        tiers=[]
    )
    fail_cid = camp_failed_res["campaign_id"]
    
    # 投资人 1 支持 2000 元
    b1_bal_before_fail = CrowdfundService.get_user_profile(backer1_id)["balance"]
    CrowdfundService.pledge(backer1_id, fail_cid, amount=2000.0)
    assert CrowdfundService.get_user_profile(backer1_id)["balance"] == b1_bal_before_fail - 2000.0

    # 众筹期限到期，仅筹得 2000 / 50000 (流标)
    fail_settle = CrowdfundService.settle_campaign(fail_cid)
    assert fail_settle["success"] is True
    assert fail_settle["status"] == "FAILED"
    assert fail_settle["refunded_count"] == 1

    # 验证投资人 1 余额已全额自动原路返回！
    b1_bal_after_refund = CrowdfundService.get_user_profile(backer1_id)["balance"]
    assert b1_bal_after_refund == b1_bal_before_fail
    print(f"[*] 5. 众筹未达标清算成功: 自动触发批量退款，投资人本金 100% 原路返还")

    print("\n>>> 全部 5 项金融业务与清结算核心测试通过 (PASS)!")

if __name__ == '__main__':
    test_full_crowdfunding_lifecycle()

