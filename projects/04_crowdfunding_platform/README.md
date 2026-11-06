# 课题 04：全栈众筹平台开发 (Full-Stack Crowdfunding Platform)

> **对应 Gitee 课题**：`#IKSC4Z` [开发众筹平台（工作量大）](https://gitee.com/NIMUESCU/WWWFinance/issues/IKSC4Z)  
> **指定参考论文**：[Design And Full Stack Development Of A Crowdfunding Platform](https://doi.org/10.13140/RG.2.2.15052.33926) (Taha Bouhsine, FSA Ibn Zohr University, PFE 2020, 开源原型: *Sahem*)  
> **核心对照文档**：[需求与验证矩阵 (requirements_matrix.md)](./requirements_matrix.md) | [技术研报 (report.md)](./report.md)  
> **运行环境**：macOS (Darwin 24.3.0, arm64) | Python 3.9.6 | SQLite 3.39+

---

## 一、 重要声明与原论文复现范畴界定

1. **论文原著与工程原型 (Taha Bouhsine 2020: Sahem)**：
   - 论文全面规范了众筹平台的四大核心角色（**Creator 发起人、Funder 出资人、Administrator 管理员、Visitor 访客**）以及多档回报、资金出资、All-or-Nothing 清算退款的 UML 规约；
   - 原文前端采用 Angular + NativeScript，后端为 Node.js 控制器。本实现遵循原论文规约，采用**纯 Python 异步服务 + 原生 HTML5/ES6 SPA + 关系型 SQLite 数据库**的轻量级全栈实现，兼顾了论文完整的用例覆盖与高校教学的零外部环境配置负担。
2. **并发控制与虚拟账本安全说明**：
   - **锁机制澄清**：系统底层存储采用 SQLite 关系型引擎，严格遵照 SQLite 的并发控制规范（WAL 模式支持并发读取与单写事务串行化，**不支持行级锁**，采用数据库/表级排他锁）；
   - **资金与凭证声明**：平台内置资金账户（如测试账户初始余额）为本地闭环模拟账本，未接入真实金融支付网关；默认测试密码（`123456`）仅限本地开发测试使用。

---

## 二、 目录结构

```text
04_crowdfunding_platform/
├── README.md                      # 项目快速使用与复现指南
├── requirements_matrix.md         # 原论文 UML 需求逐项对照矩阵与实测日志
├── report.md                      # 技术研报与金融清结算系统架构分析
├── src/
│   ├── app.py                     # 全栈 HTTP Web 服务器与静态资源挂载入口
│   ├── db.py                      # 3NF 关系型数据库模式与初始化引擎
│   ├── router.py                  # RESTful API 路由分发与 Token 鉴权
│   ├── services.py                # 核心业务服务层与 All-or-Nothing 清结算引擎
│   └── crowdfunding.db            # SQLite 关系型数据库文件
├── static/                        # 响应式前端 SPA (单页应用)
│   ├── index.html                 # 前端视图
│   ├── main.js                    # 动态渲染与异步 API 交互
│   └── style.css                  # 现代化扁平金融 UI 样式
└── tests/
    ├── run_platform.py            # 全栈服务启动与业务回归演示
    └── test_api.py                # 自动化测试套件 (含幂等性与资金守恒断言)
```

---

## 三、 快速复现与验证步骤

### 1. 运行核心业务与清结算自动化测试（推荐）
在项目根目录执行：
```bash
python3 projects/04_crowdfunding_platform/tests/test_api.py
```
**实测结果说明**：
- 用户注册与权限分配成功（Creator / Funder / Admin）；
- 众筹项目创建并挂载多个回报档位（早鸟版、量产版）；
- 支持者出资出账原子化完成，当前筹集达标率 110%；
- 众筹达标清算执行：扣除 5% 平台佣金后净额划拨发起人；
- **幂等性测试**：拦截重复清算请求（PASS）；
- 未达标流标自动批量全额原路退款至投资人账户（PASS）；
- **资金守恒定律**：全网用户总资金净变化与平台留存佣金严格守恒（PASS）。

### 2. 启动全栈 Web 服务并浏览交互
```bash
python3 projects/04_crowdfunding_platform/src/app.py 8081
```
在浏览器中访问：`http://localhost:8081`  
- 内置测试发起人：`tech_maker` / `123456`
- 内置测试投资人：`backer_alice` / `123456`

---

## 四、 研报与学术分析

详细系统设计与清结算引擎数学论证请参阅配套研报：[`report.md`](./report.md)。
