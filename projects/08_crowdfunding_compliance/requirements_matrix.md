# 课题 08：众筹叙事的专业合规性（难） 需求溯源与对照矩阵 (Requirements Traceability Matrix)

> **对应 Gitee 课题**：`#IKSBTX` [众筹叙事的专业合规性（难）](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSBTX)  
> **任课教师**：Lake HU  
> **外部论文来源**：  
> - 论文 DOI: [`10.63317/3adcqvpnznxt`](https://doi.org/10.63317/3adcqvpnznxt)  
> - 论文标题: *LegitimNarrate: A Dataset for Analyzing Legitimation Mechanisms in Crowdfunding Narratives*  
> - 发表出处: Proceedings of the 2026 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2026), pages 1361–1371  
> - 论文作者: Asmaa Lagrid, Fabrice Lefèvre 等 (Aix-Marseille Université, Université d'Avignon, LIA)  
> - 法律规章与司法解释: 《中华人民共和国刑法》第一百七十六条（非法吸收公众存款罪）、第一百九十二条（集资诈骗罪）；最高人民法院《关于审理非法集资刑事案件具体应用法律若干问题的解释》（法释〔2022〕5号）；《中华人民共和国证券法》第九条；《中华人民共和国广告法》第九条。

---

## 需求项逐条对照与核验矩阵

| 序号 | 教师/题目原始要求 | 官方源材料与条款 | 本地实现与现状证据 | 独立复现命令与验证结果 | 外部限制与阻碍记录 | 最终状态 |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **REQ-01** | **使用 AI 工具阅读总结论文的方法** | LREC-COLING 2026 论文 *LegitimNarrate* (DOI `10.63317/3adcqvpnznxt`)，全文已下载并解析 (`scratch/legitimnarrate.pdf`) | `report.md` 第一章、第二章；`README.md` 第一章 | 查阅 `report.md#一、-lrec-2026-前沿论文-legitimnarrate-方法论精要` | 无阻碍。完整提炼双层标注架构（Tier-1 二元合法性修辞、Tier-2 身份/组织/关联多维修辞）及关键学术声明（作者明确声明该标注不直接预测筹资成功）。 | **已验证** |
| **REQ-02** | **使用 AI 工具收集源数据（可能因防火墙需人工处理）** | 教师 Issue 指出：“论文发表了但是数据集没有开源……描述了详细的数据集构造方法” | `report.md` 第一章 (1.3节)；`src/regulatory_corpus.py` (L1-56) | 查阅 `requirements_matrix.md#外部阻碍详细登记表` | **记录外部阻碍**：经独立查核，论文原作者未在 ACL Anthology 或 GitHub 公开提供全量标注数据下载链接（与教师判断一致）。已依据论文描述的 8 大门类与抽样准则建立对应合规特征库。 | **已实现未验证 (外部阻碍已详细记录)** |
| **REQ-03** | **使用 AI 工具整理数据，分析数据** | 论文修辞维度分类体系与中国金融监管红线体系对比映射 | `src/regulatory_corpus.py`；`src/compliance_checker.py`；`report.md` 第三章 | 运行 `python3 projects/08_crowdfunding_compliance/tests/test_compliance.py` (Exit code 0) | 无阻碍。建立了国际社会学合法性（Sociological Legitimation）与中国法定合规性（Statutory Compliance）的双维对照结构。 | **已验证** |
| **REQ-04** | **分析：什么样的叙事是合法合规并且促进众筹项目的成功？** | 结合 LREC 论文修辞机制与最高法非吸司法解释（法释〔2022〕5号）四要件（非、公、利、社） | `report.md` 第四章、第五章；`tests/run_compliance_audit.py` (阶段三) | 运行 `python3 projects/08_crowdfunding_compliance/tests/run_compliance_audit.py`，查看 Before vs After 对照表 | 无阻碍。系统总结出“底线合规（严禁利诱性收益与股权承诺）+ 促成成功（身份背书、第三方评测、全额退款承诺消除沉没顾虑）”的黄金叙事框架。 | **已验证** |
| **REQ-05** | **合规判定工具的科学性与审慎性纠偏**：关键词不能单独证明法律合规或犯罪构成，移除确定性法律结论与虚假安全保证 | 用户任务提示词中的关键事实审查要求 | `src/compliance_checker.py` (L1-120)；`tests/test_compliance.py` (L1-53) | 运行 `python3 projects/08_crowdfunding_compliance/tests/test_compliance.py` | 无阻碍。已重构：由原先“PASS(合规优秀)”与“直接构成非吸要件”等武断定性，改为“风险信号初筛（Signal-based Scanning）”，添加明确的法律审慎限制与免责声明。 | **已验证** |

---

## 外部阻碍详细登记表

- **资源名称**：LREC-COLING 2026 论文 *LegitimNarrate* 开源标注数据集
- **访问 URL**：`https://doi.org/10.63317/3adcqvpnznxt` / `https://aclanthology.org/2026.lrec-main.118/`
- **获取尝试日期**：2026年11月4日 / 2026年11月5日
- **已尝试方法**：检索论文正文、ACL 官方页面、Footnotes 链接及原作者实验室主页。
- **精确阻碍事实**：论文正文与元数据中未随附或公开外部数据仓库（如 Hugging Face、Zenodo 或公开 GitHub 链接），确认了任课教师在 Issue 中所提“论文发表了但是数据集没有开源”的观察。
- **替代方案与学术对应**：阅读并提取论文 PDF 全文（1.59 MB），系统总结其在 97 个众筹项目（4,954 个句子）上提出的两级标注方法论（Binary Legitimacy & Multi-class Rhetorical Strategies），并结合中国法治实务构建了本土化合规信号库。

