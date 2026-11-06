# 课题 08：众筹叙事的专业合规性与边界控制 (Crowdfunding Narrative Compliance)

> **对应 Gitee 课题**：`#IKSBTX` [众筹叙事的专业合规性（难）](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSBTX)  
> **项目定位**：计算语言学与金融刑法交叉实证，解构前沿论文 *LegitimNarrate* 修辞标注方法、最高法非吸司法解释（法释〔2022〕5号）四要件、合规风险初筛信号引擎与实务文案重构  
> **环境要求**：Python 3.8+ (零外部依赖，纯原生标准库实现)  
> **需求追溯矩阵**：[requirements_matrix.md](./requirements_matrix.md)

---

## 一、 为什么任课老师在此课题标注“（难）”？

在互联网金融创新中，众筹叙事（Pitch / 文案表述）往往是决定一个项目属于**“受鼓励的新质生产力创业”还是“涉嫌触犯刑律的非法集资”**的生死分水岭。

任课教师在 Issue `#IKSBTX` 中特别指出：
> “论文（DOI: 10.63317/3adcqvpnznxt）声称实现了数据集可以分析众筹项目的合规性，不知道什么原因，论文发表了但是数据集没有开源。论文描述了详细的数据集构造方法。  
> 要求（比较难）：1. 使用AI工具阅读总结论文的方法；2. 使用AI工具收集源数据。可能防火墙的原因需要人工处理；3. 使用AI工具整理数据，分析数据；4. 使用AI工具分析：什么样的叙事是合法合规并且促进众筹项目的成功？”

### 1.1 核心难点解析与本课题攻坚方案
1. **理论边界界分**：
   - 国际计算语言学顶会论文 *LegitimNarrate*（LREC-COLING 2026）提出的“Legitimation”侧重于**社会学上的公信力/正当性修辞机制**（身份/组织/关联修辞），且作者明确声明“修辞标签并不直接因果预测众筹成功”；
   - 我国金融法治语境下的“合规性”则严格受制于《刑法》第 176 条（非法吸收公众存款罪）的**法定四要件（非法性、公开性、利诱性、社会性）**与《证券法》第 9 条公开发行红线。
2. **审慎工程实现与工具定位**：
   - 摒弃“关键词等于犯罪成立或合规免责证明”的武断逻辑；
   - 将系统定位于**“辅助文本合规风险信号初筛器”**（`src/compliance_checker.py`），输出文本信号等级（`SIGNAL_LOW` 至 `SIGNAL_HIGH_ALERT`）及重构修改指引，明确必须结合商业实质与主体资质进行人工法务审查；
3. **解答黄金叙事法则**：
   - 给出“底线法定合规（严禁利诱性收益与股权承诺）+ 修辞公信力赋能（专业研发背景、第三方检测与未达标全额退款保障）”的完整叙事解答。

---

## 二、 目录结构

```text
08_crowdfunding_compliance/
├── README.md                      # 项目说明与合规指引概要
├── requirements_matrix.md         # 教师需求逐条追溯矩阵与外部阻碍记录
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── src/
│   ├── regulatory_corpus.py       # 刑法第176条四要件、证券法红线与敏感词库
│   └── compliance_checker.py      # 辅助文本合规风险信号初筛引擎
└── tests/
    ├── test_compliance.py         # 单元测试 (信号等级与边界验证)
    └── run_compliance_audit.py    # 综合司法案例模拟与文案重构演练
```

---

## 三、 快速上手与运行

直接运行综合合规审查套件：
```bash
python3 projects/08_crowdfunding_compliance/tests/run_compliance_audit.py
```
运行单元测试套件：
```bash
python3 projects/08_crowdfunding_compliance/tests/test_compliance.py
```

你将看到：
- **案例一（司法判例模拟）**：茶园众筹中识别出 5 处严重涉刑表征，评定为 `SIGNAL_HIGH_ALERT` 并输出针对性整改方案；
- **案例二（创新科技标杆）**：开源机械臂项目聚焦于工程研发与流标退款保障，评定为 `SIGNAL_LOW` 并提示仍需人工复核商业履约实质；
- **阶段三（叙事实务重构）**：呈现系统的 Before vs After 文案重构对照表。

---

## 四、 技术报告

完整学术实证研报见配套文档：[期末技术报告：众筹叙事的专业合规性与正当性修辞机制研究 (report.md)](./report.md)。
