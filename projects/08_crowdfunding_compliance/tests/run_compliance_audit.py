"""
课题08：众筹叙事的专业合规性(难) - 综合实务合规审计运行器 (Master Compliance Auditor)
深度演练典型司法裁判案例、涉刑非吸红线识别与专业文案合规重构
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compliance_checker import CrowdfundingComplianceAuditor

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"   {title}")
    print("=" * 80)

def main():
    print("=" * 80)
    print("   《互联网金融》课题08：众筹叙事的专业合规性与边界控制 (Compliance Auditor)")
    print("   Sichuan University (SCU) - Internet Finance Research Project")
    print("=" * 80)

    auditor = CrowdfundingComplianceAuditor()

    # 案例一：司法判例模拟 —— 典型的“保本回购+消费返利型”非法吸收公众存款案
    print_header("案例一：司法判例模拟 —— 涉嫌《刑法》第176条'保本+溢价回购'涉刑项目审查")
    c1_title = "【有机茶庄园众筹】认养一亩茶园，年化收益12%且享有本金保本回购！"
    c1_pitch = (
        "为推进乡村振兴，我们面向社会公众不限门槛开放茶园众筹认领。"
        "每一位支持者均可享有固定分红，每年按出资额返还12%现金收益。三年期满后，庄园提供溢价回购承诺，保证稳赚不赔！"
        "投资额达到5万元者，额外赠送公司原始股代持份额！"
    )
    c1_res = auditor.audit_narrative(c1_title, c1_pitch, ["档位：投资1万元，季度固定分红300元"])
    print(f"[*] 项目标题: {c1_title}")
    print(f"[*] 综合合规风险评分: {c1_res['risk_score']} / 100")
    print(f"[*] 司法合规评级    : {c1_res['compliance_rating']}")
    print(f"[*] 拦截违规点总计  : {c1_res['violations_count']} 处")
    print("\n[ 违规司法要件深度判定 ]")
    for v in c1_res['violations']:
        print(f"  ❌ [{v['severity']}] {v['category']}")
        print(f"     触发词: '{v['keyword']}' | 适用法条: {v['law']}")
        print(f"     专业整改方案: {v['suggestion']}")
    print(f"\n[ 审计专家结论 ]: {c1_res['summary']}")

    # 案例二：标杆案例 —— 严格合规的硬核创新科技众筹文案
    print_header("案例二：行业合规标杆 —— 纯粹奖励型 (Reward-based) 创新硬件众筹文案")
    c2_title = "OpenBionic 六轴桌面级机械臂套件：全开源设计与机器视觉赋能"
    c2_pitch = (
        "我们是一群机器人工程探索者。经过两年的算法攻关，我们完成了桌面机械臂的软硬件架构设计。"
        "本次众筹所募集的款项将全部用于第一期工程开模、PCB贴片加工与元器件集采。"
        "支持者将获得量产后的第一期硬件套件、完整的开源开发文档与技术交流社区准入资格。"
        "我们深知硬件量产存在客观风险，特承诺：若在截止日前未达到筹集门槛，平台将全额原路退还支持者款项。"
    )
    c2_res = auditor.audit_narrative(c2_title, c2_pitch, ["【早鸟档】机械臂硬件套件一套（附教程）", "【极客套装】双机协作版"])
    print(f"[*] 项目标题: {c2_title}")
    print(f"[*] 综合合规风险评分: {c2_res['risk_score']} / 100")
    print(f"[*] 司法合规评级    : {c2_res['compliance_rating']}")
    print(f"[*] 拦截违规点总计  : {c2_res['violations_count']} 处")
    print(f"[ 审计专家结论 ]: {c2_res['summary']}")

    # 案例三：文案合规重构对比 (Before vs After)
    print_header("阶段三：众筹叙事专业合规重构对照表 (Before vs After)")
    print(f"{'违规模棱两可的原叙事 (Before / Non-compliant)':<36} | {'重构后的专业合规叙事 (After / Legally Compliant)'}")
    print("-" * 80)
    print(f"{'“支持一万元，承诺年化15%固定收益”':<36} | {'“支持一万元，获得第一批次定制硬件及3年期云服务升级特权”'}")
    print(f"{'“期满全额保本，并支持按120%溢价回购”':<34} | {'“项目若流标自动全额退款；达标后提供全国联保与标准化售后”'}")
    print(f"{'“额外赠送公司原始股与未来上市分红”':<35} | {'“列入官网鸣谢荣誉支持者名录，享有首发产品内测评审投票权”'}")
    print(f"{'“零风险跟投，稳赚不赔的理财新选择”':<35} | {'“明确披露早期创新客观风险，理性支持新质生产力探索”'}")

    print_header("全部专业合规审计实验演练完毕！")
    print("本审计引擎与研究报告完整解答了教师在题目中特别标注的'（难）'点所在。\n")

if __name__ == '__main__':
    main()

