# 课题 05：众筹书籍的数据分析 (Book Crowdfunding Empirical Analysis)

> **对应 Gitee 课题**：`#IKSANG` 众筹书籍的数据分析  
> **项目定位**：出版类众筹大数据实证研究，包含 600 个项目大样本、NLP 文本叙事特征、Logistic 成功率几率比回归与 OLS 超募弹性模型  
> **环境要求**：Python 3.8+ (零外部依赖，纯原生标准库数学与矩阵运算)

---

## 一、 研究背景与核心问题

在奖励型众筹中，出版与图书类目（Publishing）是最早成熟的垂直业态之一（如国外 Unbound、Kickstarter Publishing，国内摩点图书类目）。与标准化工业产品不同，图书众筹高度依赖“内容叙事”、“情感共鸣”与“粉丝社区认同”。

本项目聚焦出版众筹实证，探究以下三大核心金融问题：
1. **目标门槛弹性**：筹资目标金额的高低如何非线性抑制项目达标概率？
2. **信号理论与信息对称性**：文案长度（字数）、积极情感分（Sentiment）、视频宣传与过往信用记录能否有效发挥质量信号功能？
3. **阶梯定价捕获**：多样化的回报档位设置（Reward Tiers）对消费者异质性剩余价值的吸纳效应。

---

## 二、 目录结构

```text
05_crowdfunding_books_analysis/
├── README.md                      # 项目说明与实证摘要
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── data/
│   ├── book_crowdfunding_dataset.csv # 600个样本完整数据集
│   └── data_dictionary.md         # 变量与数据字典详细说明
├── src/
│   ├── data_generator.py          # 真实计量经济学特征数据集生成器
│   ├── eda.py                     # 描述性统计与分组均值差异检验
│   └── models.py                  # 高斯-约旦消元 OLS 与 Logistic 回归算法
└── tests/
    └── run_analysis.py            # 一键综合实证运行与分析报告导出
```

---

## 三、 快速上手与运行

直接运行综合实证分析套件：
```bash
python3 projects/05_crowdfunding_books_analysis/tests/run_analysis.py
```
你将看到：
- 全样本与各图书细分题材（学术、艺术画册、科幻、少儿、小说）的成功率与目标分布；
- 成功组 vs 失败组关键指标的均值对照表；
- Logistic 回归估计系数、几率比（Odds Ratio）与预测准确率；
- OLS 超募倍率多元线性回归参数与 t 统计量显著性检验。

---

## 四、 技术报告

完整学术实证研报见配套文档：[期末技术报告：出版类众筹成功率影响机制实证与叙事计量经济学研究 (report.md)](./report.md)。
