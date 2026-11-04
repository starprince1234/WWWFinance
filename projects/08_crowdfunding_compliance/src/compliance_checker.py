"""
众筹叙事专业合规性 - 智能合规审计与红线审查引擎 (Compliance Auditor Engine)
对众筹标题、宣传文案、回报档位进行基于规则的 NLP 审查，输出风险分值与法律条文修改指南
"""

import re
from typing import Dict, List, Any
from .regulatory_corpus import (
    ILLEGAL_FUNDRAISING_CRITERIA,
    SECURITIES_REDLINES,
    ADVERTISING_REDLINES,
    COMPLIANCE_REPLACEMENTS
)

class CrowdfundingComplianceAuditor:
    """众筹文案合规审查器"""

    def __init__(self):
        pass

    def audit_narrative(self, title: str, pitch_text: str, reward_descriptions: List[str] = None) -> Dict[str, Any]:
        """
        全面审查众筹文案：
        1. 刑法第 176 条非吸“利诱性”特征检索 (权重极高)
        2. 证券法第 9 条擅自公开发行股票风险检索
        3. 广告法极限词检索
        4. 综合合规风险评分 (0-100 分) 与专业法律润色建议
        """
        if reward_descriptions is None:
            reward_descriptions = []

        combined_text = f"{title}\n{pitch_text}\n" + "\n".join(reward_descriptions)

        violations = []
        risk_score = 0

        # 1. 利诱性检测 (Inducement - 非法吸收公众存款罪核心要件)
        inducement_matches = []
        for kw in ILLEGAL_FUNDRAISING_CRITERIA["INDUCEMENT"]["redlines"]:
            matches = [m.start() for m in re.finditer(re.escape(kw), combined_text)]
            if matches:
                inducement_matches.append(kw)
                risk_score += len(matches) * 25
                violations.append({
                    "severity": "CRITICAL",
                    "law": "《刑法》第176条 / 法释〔2022〕5号第一条第二项",
                    "category": "利诱性承诺 (涉嫌非法吸收公众存款罪)",
                    "keyword": kw,
                    "explanation": f"文案出现 '{kw}'，承诺保本付息或固定收益，直接触发非法集资核心红线！",
                    "suggestion": COMPLIANCE_REPLACEMENTS.get(kw, "删除该表述，变更为基于实物产品的质量交付承诺")
                })

        # 2. 擅自公开发行证券检测 (Securities Violation)
        sec_matches = []
        for kw in SECURITIES_REDLINES:
            matches = [m.start() for m in re.finditer(re.escape(kw), combined_text)]
            if matches:
                sec_matches.append(kw)
                risk_score += len(matches) * 20
                violations.append({
                    "severity": "HIGH",
                    "law": "《证券法》第九条 / 《刑法》第179条 (擅自发行股票罪)",
                    "category": "涉嫌公开发售证券 / 股权代持",
                    "keyword": kw,
                    "explanation": f"文案出现 '{kw}'，众筹属于公开传播，向不特定公众出让公司股份或收益权涉嫌非法公开发行！",
                    "suggestion": COMPLIANCE_REPLACEMENTS.get(kw, "严禁在奖励型众筹中附加任何股权或分红权益")
                })

        # 3. 广告法违禁词检测 (Advertising Law)
        ad_matches = []
        for kw in ADVERTISING_REDLINES:
            matches = [m.start() for m in re.finditer(re.escape(kw), combined_text)]
            if matches:
                ad_matches.append(kw)
                risk_score += len(matches) * 5
                violations.append({
                    "severity": "MEDIUM",
                    "law": "《中华人民共和国广告法》第九条",
                    "category": "绝对化用语与虚假宣传",
                    "keyword": kw,
                    "explanation": f"文案出现绝对化极限词 '{kw}'，违反广告法并可能构成消费误导。",
                    "suggestion": f"建议替换为客观描述，如'处于行业先进水平'或'创新性设计'"
                })

        risk_score = min(100, risk_score)

        if risk_score == 0:
            rating = "PASS (合规优秀)"
            summary_msg = "文案严格遵守奖励型众筹规范，聚焦产品交付与科技创新，未触碰金融监管红线。"
        elif risk_score <= 30:
            rating = "LOW_RISK (轻度违规)"
            summary_msg = "文案包含少量绝对化用语或模糊表述，整改后可安全发布。"
        elif risk_score <= 60:
            rating = "MEDIUM_RISK (中度涉法风险)"
            summary_msg = "文案存在向公众隐蔽承诺收益或股权的倾向，具有引发行政处罚风险，必须全面修订。"
        else:
            rating = "HIGH_CRITICAL_RISK (重大刑事合规红线)"
            summary_msg = "严重警报：文案直接具备非法吸收公众存款罪（刑法176条）的利诱性与公募要件，必须彻底下架重构！"

        return {
            "title": title,
            "risk_score": risk_score,
            "compliance_rating": rating,
            "violations_count": len(violations),
            "violations": violations,
            "summary": summary_msg
        }
