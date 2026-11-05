"""
众筹平台全栈工程 - 数据库架构与事务持久层 (Database & ACID Transactions)
基于 SQLite 原生驱动，实现外键级联、行级约束与严苛的金融支付一致性事务
"""

import sqlite3
import os
import hashlib
from typing import Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "crowdfunding.db")

def get_db_connection() -> sqlite3.Connection:
    """获取支持字典行访问与外键约束的 SQLite 连接"""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password: str) -> str:
    """SHA-256 加盐哈希密码"""
    salt = "scu_wwwfinance_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db(drop_existing: bool = False):
    """初始化数据库数据表与初始种子数据"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if drop_existing:
        cursor.executescript("""
            DROP TABLE IF EXISTS transaction_logs;
            DROP TABLE IF EXISTS pledges;
            DROP TABLE IF EXISTS reward_tiers;
            DROP TABLE IF EXISTS campaigns;
            DROP TABLE IF EXISTS users;
        """)

    cursor.executescript("""
        -- 1. 用户表 (Users)
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'USER', -- 'USER', 'CREATOR', 'ADMIN'
            balance REAL DEFAULT 10000.0, -- 虚拟资金账户 (元)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 2. 众筹项目表 (Campaigns)
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL, -- 'TECH', 'CREATIVE', 'PUBLISHING', 'COMMUNITY'
            description TEXT NOT NULL,
            goal_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0.0,
            backer_count INTEGER DEFAULT 0,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'ACTIVE', -- 'ACTIVE', 'SUCCEEDED', 'FAILED', 'SETTLED'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- 3. 回报档位表 (Reward Tiers)
        CREATE TABLE IF NOT EXISTS reward_tiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            backer_limit INTEGER DEFAULT -1, -- -1 为无限制
            current_backers INTEGER DEFAULT 0,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
        );

        -- 4. 出资订单表 (Pledges / Orders)
        CREATE TABLE IF NOT EXISTS pledges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            tier_id INTEGER,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'PAID', -- 'PAID', 'REFUNDED'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (tier_id) REFERENCES reward_tiers(id) ON DELETE SET NULL
        );

        -- 5. 资金账户流水日志表 (Transaction Logs / Audit Trail)
        CREATE TABLE IF NOT EXISTS transaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            direction TEXT NOT NULL, -- 'IN', 'OUT'
            tx_type TEXT NOT NULL, -- 'RECHARGE', 'PLEDGE', 'REFUND', 'PAYOUT'
            reference_id TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # 插入默认测试账户与种子项目
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        pwd = hash_password("123456")
        cursor.execute("INSERT INTO users (username, password_hash, role, balance) VALUES (?, ?, 'CREATOR', 20000.0)", ("tech_maker", pwd))
        cursor.execute("INSERT INTO users (username, password_hash, role, balance) VALUES (?, ?, 'USER', 50000.0)", ("backer_alice", pwd))
        cursor.execute("INSERT INTO users (username, password_hash, role, balance) VALUES (?, ?, 'USER', 30000.0)", ("backer_bob", pwd))
        
        # 种子项目 1: 智能仿生机械臂
        cursor.execute("""
            INSERT INTO campaigns (creator_id, title, category, description, goal_amount, current_amount, backer_count, end_time, status)
            VALUES (1, '开源智能桌面仿生六轴机械臂', 'TECH', '全开源伺服驱动控制算法，具备高精度机器视觉与力控反馈，适用于高校科研与创客二次开发。', 50000.0, 32000.0, 16, datetime('now', '+15 days'), 'ACTIVE')
        """)
        c1_id = cursor.lastrowid
        cursor.execute("INSERT INTO reward_tiers (campaign_id, title, description, price, backer_limit) VALUES (?, '早鸟极客套件', '包含主控板、舵机与亚克力外壳', 1299.0, 50)", (c1_id,))
        cursor.execute("INSERT INTO reward_tiers (campaign_id, title, description, price, backer_limit) VALUES (?, '尊享科研整机', '金属 CNC 加工，出厂校准力控传感器', 2999.0, 20)", (c1_id,))

        # 种子项目 2: 出版众筹
        cursor.execute("""
            INSERT INTO campaigns (creator_id, title, category, description, goal_amount, current_amount, backer_count, end_time, status)
            VALUES (1, '《去中心化金融通识与实践》特装版', 'PUBLISHING', '全面拆解 DeFi 借贷、AMM 自动化做市与智能合约安全漏洞，附赠全套实验代码与配套课件。', 15000.0, 16500.0, 85, datetime('now', '+3 days'), 'ACTIVE')
        """)
        c2_id = cursor.lastrowid
        cursor.execute("INSERT INTO reward_tiers (campaign_id, title, description, price, backer_limit) VALUES (?, '精装实体书 + 专属藏书票', '作者签名编号精装本', 99.0, 200)", (c2_id,))
        cursor.execute("INSERT INTO reward_tiers (campaign_id, title, description, price, backer_limit) VALUES (?, '藏家纪念礼盒', '含实体书、数字藏品纪念勋章与线下沙龙门票', 299.0, 50)", (c2_id,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db(drop_existing=True)
    print(">>> 众筹平台数据库初始化完毕！")

