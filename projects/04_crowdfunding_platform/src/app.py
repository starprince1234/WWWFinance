"""
众筹平台全栈工程 - HTTP 服务宿主与静态资源服务器 (Full-Stack HTTP Server)
结合原生 BaseHTTPRequestHandler，提供零第三方依赖的高并发 RESTful API 与前端静态托管
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

from .db import init_db
from .router import ApiRouter

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))

class CrowdfundRequestHandler(BaseHTTPRequestHandler):

    def _send_response_json(self, status_code: int, data: Dict[str, Any]):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _serve_static_file(self, filepath: str, content_type: str):
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        with open(filepath, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. 静态资源路由
        if path == "/" or path == "/index.html":
            return self._serve_static_file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
        if path == "/style.css":
            return self._serve_static_file(os.path.join(STATIC_DIR, "style.css"), "text/css; charset=utf-8")
        if path == "/main.js":
            return self._serve_static_file(os.path.join(STATIC_DIR, "main.js"), "application/javascript; charset=utf-8")

        # 2. RESTful API 路由
        if path.startswith("/api/"):
            query_params = dict(urllib.parse.parse_qsl(parsed.query))
            status_code, resp_data = ApiRouter.handle_request("GET", path, query_params, dict(self.headers))
            return self._send_response_json(status_code, resp_data)

        # 默认回退
        return self._serve_static_file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 读取请求体 JSON
        content_length = int(self.headers.get('Content-Length', 0))
        body = {}
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode('utf-8')
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

        if path.startswith("/api/"):
            status_code, resp_data = ApiRouter.handle_request("POST", path, body, dict(self.headers))
            return self._send_response_json(status_code, resp_data)

        return self._send_response_json(404, {"error": "Endpoint not found"})


def run_server(port: int = 8081, init_database: bool = True):
    if init_database:
        init_db(drop_existing=False)

    server = HTTPServer(("0.0.0.0", port), CrowdfundRequestHandler)
    print("=" * 65)
    print(f"   众筹平台服务已启动！监听端口: http://localhost:{port}")
    print(f"   静态资源目录: {STATIC_DIR}")
    print("=" * 65)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在安全关闭服务...")
        server.server_close()

if __name__ == '__main__':
    port = 8081
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port=port)

