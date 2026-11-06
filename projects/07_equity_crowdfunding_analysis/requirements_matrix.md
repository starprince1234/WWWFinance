# 课题 07：股权式众筹及数据分析 需求溯源与对照矩阵 (Requirements Traceability Matrix)

> **对应 Gitee 课题**：`#I8K09K` [股权式众筹及数据分析](https://gitee.com/NIMUESCU/WWWFinance/issues/I8K09K)  
> **任课教师**：Lake HU  
> **外部材料来源**：  
> - 外部数据集链接：[Equity Crowdfunding Synthetic Dataset](https://doi.org/10.5281/zenodo.18847367) (DOI: `10.5281/zenodo.18847367`)  
> - 法律规章与规范性文件：2014 年中国证券业协会《私募股权众筹融资管理办法（试行）（征求意见稿）》、2015 年中国人民银行等十部委《关于促进互联网金融健康发展的指导意见》（银发〔2015〕221号）、《中华人民共和国证券法》（2019年修订）、《中华人民共和国公司法》（2023年修订，2024年7月1日施行）第四十二条、中国证监会《私募投资基金监督管理暂行办法》及国务院《私募投资基金监督管理条例》（2023年）。

---

## 需求项逐条对照与核验矩阵

| 序号 | 教师/题目原始要求 | 官方源材料与条款 | 本地实现与现状证据 | 独立复现命令与验证结果 | 外部限制与阻碍记录 | 最终状态 |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **REQ-01** | **股权众筹平台法律属性**：2014年《私募股权众筹管理办法（试行）（征求意见稿）》第5条平台定义（信息中介）与2015年《指导意见》 | 证券业协会2014征求意见稿第5条；十部委2015《指导意见》第七条 | `report.md` 第一章、第四章；`README.md` 第一章 | 查阅 `report.md#一、-股权众筹商业逻辑与境内外制度变迁` | 无阻碍。完整呈现中介性质与多层次资本市场定位。 | **已验证** |
| **REQ-02** | **股权式众筹的金融本质与回报特征**：明确以项目股权作为回报，本质属民间融资、私募股权互联网化 | 教师 Issue 原文第3、4段；大纲第五章（5.2与5.4节） | `report.md` 第一章、第二章；`src/equity_data.py` (L27-32) | 运行 `python3 projects/07_equity_crowdfunding_analysis/tests/run_equity_analysis.py` 查阅阶段二与阶段三 | 无阻碍。界定私募与公募红线、SAFE协议与普通股对价。 | **已验证** |
| **REQ-03** | **2026年最新数据实证**：获取并分析教师指定链接 `https://doi.org/10.5281/zenodo.18847367` (*Equity Crowdfunding Synthetic Dataset*) | Zenodo DOI `10.5281/zenodo.18847367` (*Equity Crowdfunding Synthetic Dataset*, 3,000 synthetic campaigns) | `report.md` 摘要及第三章；`src/equity_data.py` (L1-114) | 运行 `python3 projects/07_equity_crowdfunding_analysis/tests/run_equity_analysis.py` | **记录外部阻碍**：Zenodo 页面返回 JavaScript Proof-of-Work 反爬屏障 (`zenodo-clear-v2`)，依据安全准则停止自动化破解。原作者标题已明确注明为「Synthetic Dataset」(合成数据集)。本地构建等效 500 条参数化教学模拟数据集。 | **已实现未验证 (外部阻碍已详细记录)** |
| **REQ-04** | **领投人机制与生存率实证真实性纠偏**：修正“生成器硬编码赋权却宣称实证发现因果效应”的循环论证缺陷 | 用户任务提示词中专门指出的事实审计缺陷 | `src/equity_data.py` (L60-65)；`src/survival_analysis.py` (L56-79)；`report.md` 第三章 (L73-84) | 运行 `python3 projects/07_equity_crowdfunding_analysis/tests/run_equity_analysis.py`，查看阶段四输出提示 | 无阻碍。已彻底更正：明确说明 `quality_score` 包含 `0.5 * lead_investor` 系模型生成规则，对比差异属于模型参数推演，坚决不宣称为真实世界因果证据。 | **已验证** |
| **REQ-05** | **中国法律本土化制度制约**：有限责任公司股东 50 人上限、SPV有限合伙代持、200人公开发行红线与穿透核查 | 《公司法》（2023年修订）第四十二条（原第二十四条）；《证券法》第九条；证监会穿透式监管规范 | `report.md` 第四章 (L85-105)；`tests/run_equity_analysis.py` (L68-71) | 查阅 `report.md#四、-中国股权众筹的法律瓶颈与制度突围` | 无阻碍。已更新至最新 2023 年修订版《公司法》条文编号与私募监管穿透核查实务。 | **已验证** |

---

## 外部阻碍详细登记表

- **资源名称**：Zenodo 2026 股权众筹数据集 (*Equity Crowdfunding Synthetic Dataset*)
- **访问 URL**：`https://doi.org/10.5281/zenodo.18847367` (重定向至 `https://zenodo.org/records/18847367`)
- **获取尝试日期**：2026年11月4日 / 2026年11月5日
- **已尝试方法**：通过 HTTP 客户端携带常规 User-Agent 头直接请求；通过 cURL 获取头部与内容。
- **精确报错与阻碍**：服务器返回包含 JavaScript 客户端算力挑战（Proof-of-Work Challenge: `zenodo-clear-v2:...`）的反爬虫网关页面，拒绝向无头客户端直出 CSV 附件。依据 AI 安全行为准则，不得自动解答或绕过 PoW 验证网关。
- **元数据分析与替代方案**：从网关响应提取的 OpenGraph / Schema.org 元数据确认，该项目标题明确为 **"Equity Crowdfunding Synthetic Dataset"**（合成数据集，包含 2020-2026 年 3000 条合成众筹数据）。因此，本项目依据该数据集公开声明的参数结构，在本地编写了高保真参数化发生器 `src/equity_data.py`（500 条样本），并在报告中诚实声明数据性质。

