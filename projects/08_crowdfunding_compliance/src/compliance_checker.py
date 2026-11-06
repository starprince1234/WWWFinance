"""
众筹叙事专业合规性 - 辅助文本合规风险信号初筛引擎 (Compliance Signal Checker)
对众筹标题、宣传文案、回报档位进行基于规则的 NLP 特征词筛查，输出风险提示与文本重构参考。

【法律与科学严正声明】：
1. 关键词筛查不能单独证明法律合规或犯罪构成。文案中未命中敏感词并不等同于绝对合法（可能存在其他民事欺诈、专利侵权或实质资金池）；
   文案中命中敏感词亦不能等同于直接定罪（需结合商业实质、资金流转、主观故意等司法要件综合裁量）。
2. 本工具仅作为文案起草过程中的“辅助文本风险信号提示器 (Textual Signal Scanner)”，不输出确定性司法定性结论，
   不可作为最终司法定性或免除合规责任的依据，最终合规性需由执业法律专业人士结合个案商业实质全面审查。
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
    """众筹文案辅助合规信号筛查器"""

    def __init__(self):
        pass

    def audit_narrative(self, title: str, pitch_text: str, reward_descriptions: List[str] = None) -> Dict[str, Any]:
        """
        全面筛查众筹文案文本特征：
        1. 检索涉嫌《刑法》第 176 条非吸“利诱性”的敏感表征词
        2. 检索涉嫌《证券法》第 9 条公开发行股票的敏感表征词
        3. 检索《广告法》绝对化极限表述
        4. 输出文本风险分值 (0-100)、风险信号等级与修改建议
        """
        if reward_descriptions is None:
            reward_descriptions = []

        combined_text = f"{title}\n{pitch_text}\n" + "\n".join(reward_descriptions)

        flagged_signals = []
        risk_score = 0

        # 1. 利诱性敏感表征词检测 (Inducement Signal)
        for kw in ILLEGAL_FUNDRAISING_CRITERIA["INDUCEMENT"]["redlines"]:
            matches = [m.start() for m in re.finditer(re.escape(kw), combined_text)]
            if matches:
                risk_score += len(matches) * 25
                flagged_signals.append({
                    "severity": "CRITICAL",
                    "law": "《刑法》第176条 / 法释〔2022〕5号第一条第二项",
                    "category": "利诱性敏感信号 (涉嫌非法吸收公众存款罪核心要件)",
                    "keyword": kw,
                    "explanation": f"文案包含文本表征词 '{kw}'，存在承诺保本或固定回报的表述风险，极易引致司法与行政重点核查。",
                    "suggestion": COMPLIANCE_REPLACEMENTS.get(kw, "建议移除收益或本金承诺，变更为基于实物交付与项目研发成果的客观说明")
                })

        # 2. 擅自公开发行证券敏感表征词检测 (Securities Signal)
        for kw in SECURITIES_REDLINES:
            matches = [m.start() for m in re.finditer(re.escape(kw), combined_text)]
            if matches:
                risk_score += len(matches) * 20
                flagged_signals.append({
                    "severity": "HIGH",
                    "law": "《证券法》第九条 / 《刑法》第179条",
                    "category": "股权/证券化敏感信号 (涉嫌向不特定公众公开发行证券)",
                    "keyword": kw,
                    "explanation": f"文案包含表征词 '{kw}'，在面向公众的众筹页面中可能被监管机关视为公开发售股权或收益权。",
                    "suggestion": COMPLIANCE_REPLACEMENTS.get(kw, "严禁在奖励型众筹中附加任何股权、股份、期权或分红权益")
                })

        # 3. 广告法违禁词检测 (Advertising Signal)
        for kw in ADVERTISING_REDLINES:
            matches = [m.start() for m in re.finditer(re.escape(kw), combined_text)]
            if matches:
                risk_score += len(matches) * 5
                flagged_signals.append({
                    "severity": "MEDIUM",
                    "law": "《中华人民共和国广告法》第九条第三项",
                    "category": "绝对化用语敏感信号",
                    "keyword": kw,
                    "explanation": f"文案包含极限词 '{kw}'，存在行政处罚与消费者欺诈维权风险。",
                    "suggestion": f"建议替换为客观研发指标或测试数据，如'处于行业先进水平'或'具有自主研发专利'"
                })

        risk_score = min(100, risk_score)

        if risk_score == 0:
            rating = "SIGNAL_LOW (未命中已知高危特征词，需结合商业实质人工复核)"
            summary_msg = "初步文本筛查未命中预设的涉非吸、涉证券或极限词高危表征，文案聚焦产品交付与科技说明。注：不作为免责保证，仍需人工复核商业实质与履约能力。"
        elif risk_score <= 30:
            rating = "SIGNAL_MODERATE (命中少量轻度表征词，建议常规修改)"
            summary_msg = "文案包含少量绝对化用语或轻度模糊表述，建议由文案团队参考整改建议后复核发布。"
        elif risk_score <= 60:
            rating = "SIGNAL_ELEVATED (命中中度涉法特征信号，建议法务重点复核)"
            summary_msg = "文案存在向公众隐性暗示投资回报或权益份额的特征信号，存在较高监管合规摩擦风险，建议由法务部门介入核查。"
        else:
            rating = "SIGNAL_HIGH_ALERT (命中高危涉刑/证券监管关联表征词，需立即人工介入重构)"
            summary_msg = "高度风险警示：文案集中命中了典型非法集资（利诱性）或擅自发行证券相关的敏感特征词汇，在司法实践中极易成为重点审查证据，建议彻底重构叙事逻辑。"

        return {
            "title": title,
            "risk_score": risk_score,
            "compliance_signal_level": rating,
            "violations_count": len(flagged_signals),
            "flagged_signals": flagged_signals,
            # 兼容旧代码字段，但赋予审慎的信号属性
            "compliance_rating": rating,
            "violations": flagged_signals,
            "summary": summary_msg,
            "disclaimer": (
                "【审慎声明】：本筛查结果仅供文案起草辅助参考，不能且不得替代司法定性或执业律师的法律意见书。"
                "最终合规性取决于发起人实际资质、资金账户存管、产品交付真实性等整体商业行为。"
            )
        }
