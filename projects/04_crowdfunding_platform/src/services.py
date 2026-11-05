"""
众筹平台全栈工程 - 核心金融业务与清结算服务层 (Services & Settlement Engine)
封装项目流转、出资原子事务、All-or-Nothing 履约清算与批量自动退款
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from .db import get_db_connection, hash_password

class CrowdfundService:

    @staticmethod
    def register_user(username: str, password: str, role: str = 'USER') -> Dict[str, Any]:
        conn = get_db_connection()
        try:
            pwd_hash = hash_password(password)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, pwd_hash, role))
            user_id = cur.lastrowid
            conn.commit()
            return {"success": True, "user_id": user_id, "username": username, "role": role}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": f"用户名已被注册或参数非法: {e}"}
        finally:
            conn.close()

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        pwd_hash = hash_password(password)
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, balance FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
        row = cur.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    @staticmethod
    def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, balance, created_at FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create_campaign(creator_id: int, title: str, category: str, description: str, goal_amount: float, duration_days: int, tiers: List[Dict]) -> Dict[str, Any]:
        if goal_amount <= 0:
            return {"success": False, "error": "目标筹资金额必须大于 0"}
        if duration_days < 1:
            return {"success": False, "error": "众筹天数至少为 1 天"}

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO campaigns (creator_id, title, category, description, goal_amount, end_time, status)
                VALUES (?, ?, ?, ?, ?, datetime('now', ?), 'ACTIVE')
            """, (creator_id, title, category, description, goal_amount, f'+{duration_days} days'))
            cid = cur.lastrowid

            for t in tiers:
                cur.execute("""
                    INSERT INTO reward_tiers (campaign_id, title, description, price, backer_limit)
                    VALUES (?, ?, ?, ?, ?)
                """, (cid, t.get('title', '标准回报'), t.get('description', ''), float(t.get('price', 10.0)), int(t.get('backer_limit', -1))))

            conn.commit()
            return {"success": True, "campaign_id": cid}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def list_campaigns(category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT c.*, u.username as creator_name
            FROM campaigns c
            JOIN users u ON c.creator_id = u.id
            WHERE 1=1
        """
        params = []
        if category and category != 'ALL':
            query += " AND c.category = ?"
            params.append(category)
        if status and status != 'ALL':
            query += " AND c.status = ?"
            params.append(status)

        query += " ORDER BY c.id DESC"
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_campaign_detail(campaign_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.*, u.username as creator_name
            FROM campaigns c
            JOIN users u ON c.creator_id = u.id
            WHERE c.id = ?
        """, (campaign_id,))
        camp = cur.fetchone()
        if not camp:
            conn.close()
            return None

        result = dict(camp)
        cur.execute("SELECT * FROM reward_tiers WHERE campaign_id = ?", (campaign_id,))
        result["tiers"] = [dict(r) for r in cur.fetchall()]
        conn.close()
        return result

    @staticmethod
    def pledge(user_id: int, campaign_id: int, amount: float, tier_id: Optional[int] = None) -> Dict[str, Any]:
        """
        支持者出资核心事务 (ACID Transaction):
        1. 检查众筹状态与用户可用余额
        2. 扣减出资人余额
        3. 递增众筹当前筹集金额与支持人数
        4. 记录订单 (pledges) 与审计流水日志 (transaction_logs)
        """
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            # 查验用户资金
            cur.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
            user_row = cur.fetchone()
            if not user_row or user_row['balance'] < amount:
                return {"success": False, "error": "账户可用余额不足，请充值"}

            # 查验众筹状态
            cur.execute("SELECT status, end_time FROM campaigns WHERE id = ?", (campaign_id,))
            camp_row = cur.fetchone()
            if not camp_row or camp_row['status'] != 'ACTIVE':
                return {"success": False, "error": "该项目不在开放出资状态"}

            # 执行扣款与数据更新
            cur.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_id))
            cur.execute("UPDATE campaigns SET current_amount = current_amount + ?, backer_count = backer_count + 1 WHERE id = ?", (amount, campaign_id))

            if tier_id:
                cur.execute("UPDATE reward_tiers SET current_backers = current_backers + 1 WHERE id = ?", (tier_id,))

            cur.execute("""
                INSERT INTO pledges (campaign_id, user_id, tier_id, amount, status)
                VALUES (?, ?, ?, ?, 'PAID')
            """, (campaign_id, user_id, tier_id, amount))
            pledge_id = cur.lastrowid

            cur.execute("""
                INSERT INTO transaction_logs (user_id, amount, direction, tx_type, reference_id, note)
                VALUES (?, ?, 'OUT', 'PLEDGE', ?, ?)
            """, (user_id, amount, f"pledge_{pledge_id}", f"支持众筹项目 #{campaign_id}"))

            conn.commit()
            return {"success": True, "pledge_id": pledge_id, "amount": amount}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": f"出资事务执行异常: {e}"}
        finally:
            conn.close()

    @staticmethod
    def settle_campaign(campaign_id: int) -> Dict[str, Any]:
        """
        众筹到期履约清算引擎 (All-or-Nothing Settlement Engine):
        - 达成目标 (current_amount >= goal_amount) -> 状态更新为 SUCCEEDED，资金扣除 5% 平台服务费后拨付给项目发起人
        - 未达目标 (current_amount < goal_amount) -> 状态更新为 FAILED，触发全自动批量退款事务，本金原路返回支持者钱包
        """
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
            camp = cur.fetchone()
            if not camp:
                return {"success": False, "error": "项目不存在"}
            if camp['status'] in ('SUCCEEDED', 'FAILED', 'SETTLED'):
                return {"success": False, "error": f"项目已完成清算，当前状态为 {camp['status']}"}

            current_amt = camp['current_amount']
            goal_amt = camp['goal_amount']
            creator_id = camp['creator_id']

            if current_amt >= goal_amt:
                # 众筹成功 -> 结算资金至发起人
                platform_fee = current_amt * 0.05
                net_payout = current_amt - platform_fee
                cur.execute("UPDATE campaigns SET status = 'SUCCEEDED' WHERE id = ?", (campaign_id,))
                cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (net_payout, creator_id))
                cur.execute("""
                    INSERT INTO transaction_logs (user_id, amount, direction, tx_type, reference_id, note)
                    VALUES (?, ?, 'IN', 'PAYOUT', ?, ?)
                """, (creator_id, net_payout, f"campaign_{campaign_id}", f"众筹项目 #{campaign_id} 达标放款 (扣除5%平台佣金)"))

                conn.commit()
                return {"success": True, "status": "SUCCEEDED", "current_amount": current_amt, "payout": net_payout, "fee": platform_fee}
            else:
                # 众筹失败 -> 批量自动退款
                cur.execute("UPDATE campaigns SET status = 'FAILED' WHERE id = ?", (campaign_id,))
                cur.execute("SELECT id, user_id, amount FROM pledges WHERE campaign_id = ? AND status = 'PAID'", (campaign_id,))
                pledges = cur.fetchall()

                refund_count = 0
                total_refunded = 0.0
                for p in pledges:
                    cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (p['amount'], p['user_id']))
                    cur.execute("UPDATE pledges SET status = 'REFUNDED' WHERE id = ?", (p['id'],))
                    cur.execute("""
                        INSERT INTO transaction_logs (user_id, amount, direction, tx_type, reference_id, note)
                        VALUES (?, ?, 'IN', 'REFUND', ?, ?)
                    """, (p['user_id'], p['amount'], f"refund_p_{p['id']}", f"项目 #{campaign_id} 未达标自动退款"))
                    refund_count += 1
                    total_refunded += p['amount']

                conn.commit()
                return {"success": True, "status": "FAILED", "refunded_count": refund_count, "total_refunded": total_refunded}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": f"清算异常: {e}"}
        finally:
            conn.close()

