"""
众筹叙事专业合规性 - 自动化测试套件 (Test Compliance Auditor)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compliance_checker import CrowdfundingComplianceAuditor

def test_compliant_campaign():
    print("\n--- 1. 测试合规的创新产品众筹文案 ---")
    auditor = CrowdfundingComplianceAuditor()
    title = "轻量级钛合金公路自行车头盔"
    pitch = (
        "我们是一个专注于骑行安全的设计团队。历时18个月研发，我们打造了这款符合国家安全标准的全碳纤维与钛合金结合的超轻头盔。"
        "本次众筹所有资金将专款专用于模具开发和第一批次量产。若项目未达标，平台将全额原路退还支持款。"
    )
    rewards = ["【早鸟支持】获得首批量产头盔一个（顺丰包邮）", "【双人套装】获得定制签名版头盔两个"]

    res = auditor.audit_narrative(title, pitch, rewards)
    print(f"[*] 风险分值: {res['risk_score']} / 100")
    print(f"[*] 评级结果: {res['compliance_rating']}")
    assert res['risk_score'] == 0
    assert res['violations_count'] == 0
    print(">>> 合规文案审查通过 (PASS)")

def test_illegal_fundraising_campaign():
    print("\n--- 2. 测试触犯《刑法》第176条的涉刑高危文案 ---")
    auditor = CrowdfundingComplianceAuditor()
    title = "生态农业智能大棚众筹：年化收益15%，稳赚不赔！"
    pitch = (
        "投资我们的大棚项目，我们向全国公众不限门槛开放认购。"
        "发起人承诺保本保息，每季度享受固定分红，期满后支持溢价回购！出资达到1万元以上额外赠送股权与原始股！"
    )
    rewards = ["支持1万元：享有每年1500元固定分红并赠送股权"]

    res = auditor.audit_narrative(title, pitch, rewards)
    print(f"[*] 风险分值: {res['risk_score']} / 100")
    print(f"[*] 评级结果: {res['compliance_rating']}")
    print(f"[*] 拦截违规点数量: {res['violations_count']}")
    for v in res['violations']:
        print(f"    - [{v['severity']}] {v['category']} | 关键词: '{v['keyword']}' -> 法律条文: {v['law']}")

    assert res['risk_score'] >= 80, "未能有效识别重大涉非吸刑事风险!"
    assert res['violations_count'] >= 4
    print(">>> 涉非吸高危文案成功被拦截与合规标红 (PASS)")

if __name__ == '__main__':
    test_compliant_campaign()
    test_illegal_fundraising_campaign()

