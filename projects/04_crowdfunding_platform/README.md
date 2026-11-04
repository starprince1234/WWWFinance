# 课题 04：全栈众筹平台工程实现 (CloudFund Platform)

> **对应 Gitee 课题**：`#IKSC4Z` 开发众筹平台（工作量大）  
> **项目定位**：完整全栈互联网众筹系统，涵盖用户权限、项目流转、出资原子事务、All-or-Nothing 履约清算与批量自动退款  
> **环境要求**：Python 3.8+ (零外部 npm/pip 依赖，原生标准库与 SQLite 驱动开箱即用)

---

## 一、 系统架构与工程特性

本课题直面任课老师标注的“工作量大”难点，构建了高可用、具备金融级 ACID 事务安全性的全栈互联网众筹平台：

1. **关系型数据库与严格金融事务 (`src/db.py`)**
   - 建立 `users`, `campaigns`, `reward_tiers`, `pledges`, `transaction_logs` 五张核心表；
   - 采用行级锁与外键级联，所有涉及资金变更（出资扣款、放款、退款）均在 `BEGIN TRANSACTION` 原子上下文中完成，杜绝超卖与账实不符。
2. **核心业务与清结算服务引擎 (`src/services.py`)**
   - **All-or-Nothing（全有或全无）履约清算**：
     - 达标成功：系统自动扣除 5% 平台服务费，95% 净款实时结算拨付给发起人；
     - 未达标流标：触发并发批量退款子系统，全额原路返还所有支持者本金；
   - 详尽的资金审计日志（Audit Trail），每一笔款项出入均有唯一 Reference ID 追踪。
3. **RESTful API 与 Token 鉴权 (`src/router.py`, `src/app.py`)**
   - 提供标准 REST 接口：注册、登录、发布项目、出资支持、到期清算；
   - 零依赖自签名令牌验证。
4. **响应式现代化前端 SPA 界面 (`static/`)**
   - 包含实时大屏统计、多分类标签切换、项目详情展示、档位支持弹窗与一键清算演练。

---

## 二、 目录结构

```text
04_crowdfunding_platform/
├── README.md                      # 项目说明与部署指南
├── report.md                      # 期末学术标准技术报告 (Tech Report)
├── src/
│   ├── db.py                      # SQLite 数据库模型、外键与加盐哈希
│   ├── services.py                # 出资、订单、账户结算与批量退款业务逻辑
│   ├── router.py                  # RESTful API 控制器路由与 Token 鉴权
│   └── app.py                     # 单命令 HTTP 后端服务与静态托管
├── static/
│   ├── index.html                 # 响应式 Web 众筹大厅
│   ├── style.css                  # 现代化 UI 样式设计
│   └── main.js                    # 客户端 SPA 状态管理与 API 异步交互
└── tests/
    ├── test_api.py                # 业务生命周期与清结算回归单测
    └── run_platform.py            # 一键综合测试与启动引导
```

---

## 三、 快速上手与运行

### 1. 运行系统回归单元测试
```bash
python3 projects/04_crowdfunding_platform/tests/run_platform.py
```

### 2. 启动全栈 Web 服务
```bash
python3 projects/04_crowdfunding_platform/src/app.py 8081
```
启动后在浏览器打开：`http://localhost:8081`

**内置初始测试账号（密码均为 123456）：**
- 项目发起人：`tech_maker`（初始余额 ¥20,000）
- 普通投资人：`backer_alice`（初始余额 ¥50,000）
- 普通投资人：`backer_bob`（初始余额 ¥30,000）

---

## 四、 技术报告

完整学术报告与架构剖析见配套文档：[期末技术报告：现代互联网众筹平台架构设计与资金清结算实证 (report.md)](./report.md)。
