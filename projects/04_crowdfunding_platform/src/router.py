"""
众筹平台全栈工程 - HTTP 请求分发与 RESTful 路由 (RESTful Router & Controller)
处理用户鉴权、数据校验、JSON 序列化与跨域支持
"""

import json
import base64
import time
from typing import Dict, Any, Tuple
from .services import CrowdfundService

# 极简确定性 Token 机制 (无外部依赖 JWT)
TOKEN_SECRET = "scu_internet_finance_2026_key"

def generate_token(user: Dict[str, Any]) -> str:
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": int(time.time()) + 86400 * 7
    }
    raw = json.dumps(payload).encode('utf-8')
    return base64.urlsafe_b64encode(raw).decode('utf-8')

def parse_token(token_str: str) -> Dict[str, Any]:
    try:
        raw = base64.urlsafe_b64decode(token_str.encode('utf-8'))
        payload = json.loads(raw.decode('utf-8'))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


class ApiRouter:
    """RESTful API 控制器路由"""

    @staticmethod
    def handle_request(method: str, path: str, body: Dict[str, Any], headers: Dict[str, str]) -> Tuple[int, Dict[str, Any]]:
        # 1. 认证路由 (Auth)
        if method == "POST" and path == "/api/auth/register":
            username = body.get("username", "").strip()
            password = body.get("password", "").strip()
            role = body.get("role", "USER")
            if not username or not password:
                return 400, {"error": "用户名或密码不能为空"}
            res = CrowdfundService.register_user(username, password, role)
            return (200, res) if res.get("success") else (400, res)

        if method == "POST" and path == "/api/auth/login":
            username = body.get("username", "").strip()
            password = body.get("password", "").strip()
            user = CrowdfundService.authenticate_user(username, password)
            if not user:
                return 401, {"error": "用户名或密码错误"}
            token = generate_token(user)
            return 200, {"success": True, "token": token, "user": user}

        # 2. 需鉴权路由提取用户
        current_user = None
        auth_header = headers.get("Authorization", headers.get("authorization", ""))
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            current_user = parse_token(token)

        if method == "GET" and path == "/api/user/profile":
            if not current_user:
                return 401, {"error": "未登录或凭据失效"}
            profile = CrowdfundService.get_user_profile(current_user["user_id"])
            return 200, {"success": True, "user": profile}

        # 3. 众筹项目路由 (Campaigns)
        if method == "GET" and path == "/api/campaigns":
            # 支持 query params 在调用方预拆分
            category = body.get("category", "ALL")
            status = body.get("status", "ALL")
            items = CrowdfundService.list_campaigns(category, status)
            return 200, {"success": True, "data": items}

        if method == "POST" and path == "/api/campaigns":
            if not current_user:
                return 401, {"error": "发起众筹前请先登录"}
            title = body.get("title", "")
            category = body.get("category", "TECH")
            desc = body.get("description", "")
            goal = float(body.get("goal_amount", 0))
            days = int(body.get("duration_days", 14))
            tiers = body.get("tiers", [])
            res = CrowdfundService.create_campaign(current_user["user_id"], title, category, desc, goal, days, tiers)
            return (200, res) if res.get("success") else (400, res)

        if method == "GET" and path.startswith("/api/campaigns/"):
            try:
                cid = int(path.split("/api/campaigns/")[1])
                detail = CrowdfundService.get_campaign_detail(cid)
                if not detail:
                    return 404, {"error": "项目未找到"}
                return 200, {"success": True, "data": detail}
            except Exception:
                return 400, {"error": "无效的项目 ID"}

        # 4. 出资与结算路由
        if method == "POST" and path.endswith("/pledge"):
            if not current_user:
                return 401, {"error": "出资前请先登录账户"}
            try:
                parts = path.split("/")
                cid = int(parts[3])
                amt = float(body.get("amount", 0))
                tier_id = body.get("tier_id")
                if tier_id:
                    tier_id = int(tier_id)
                res = CrowdfundService.pledge(current_user["user_id"], cid, amt, tier_id)
                return (200, res) if res.get("success") else (400, res)
            except Exception as e:
                return 400, {"error": f"参数格式异常: {e}"}

        if method == "POST" and path.endswith("/settle"):
            try:
                parts = path.split("/")
                cid = int(parts[3])
                res = CrowdfundService.settle_campaign(cid)
                return (200, res) if res.get("success") else (400, res)
            except Exception as e:
                return 400, {"error": f"清算执行失败: {e}"}

        return 404, {"error": f"API 路由不存在: {method} {path}"}

