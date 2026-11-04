"""
中本聪原始 IRC 节点发现机制仿真 (Satoshi v0.1 IRC Peer Discovery Simulation)
深度复现 2009 年中本聪在 irc.cpp 中利用 IRC 聊天室频道进行去中心化对等节点网络发现的历史机制
"""

import socket
import struct
from typing import List, Dict, Optional

class SatoshiIRCDiscovery:
    """
    仿真中本聪 v0.1 源码中的 IRC 节点发现协议：
    1. 编码自身 IP：将 IPv4 地址 (4字节大端序) 转换为 IRC 昵称后缀
       中本聪原始格式: "x" + base58/hex 编码的 IP
    2. 加入公共聊天频道: irc.oftc.net 上的 #bitcoin 频道
    3. 监听频道用户列表 (WHO 命令响应)，解析出在线节点的 IP 并加入连接候选池
    """
    CHANNEL = "#bitcoin"
    IRC_SERVER = "irc.oftc.net"
    PORT = 8333  # 原始比特币默认端口

    @staticmethod
    def encode_ip_to_nick(ip_str: str) -> str:
        """将 IPv4 地址 (如 192.168.1.1) 编码为中本聪 IRC 昵称格式"""
        try:
            ip_packed = socket.inet_aton(ip_str)
            # v0.1 中使用前缀 'x' 加上 16 进制大端编码
            return f"x{ip_packed.hex()}"
        except Exception:
            return f"x00000000"

    @staticmethod
    def decode_nick_to_ip(nick: str) -> Optional[str]:
        """从 IRC 昵称中解码还原出对端节点的 IPv4 地址"""
        if nick.startswith("x") and len(nick) == 9:
            try:
                hex_part = nick[1:]
                ip_bytes = bytes.fromhex(hex_part)
                return socket.inet_ntoa(ip_bytes)
            except Exception:
                return None
        return None


class IRCServerMock:
    """模拟 2009 年 IRC 频道中继服务器，供本地离线实验与教学演示"""
    def __init__(self):
        self.channel_members: Dict[str, str] = {}  # nick -> ip

    def register_node(self, node_ip: str) -> str:
        nick = SatoshiIRCDiscovery.encode_ip_to_nick(node_ip)
        self.channel_members[nick] = node_ip
        return nick

    def get_discovered_peers(self, my_nick: str) -> List[str]:
        """获取当前频道内除自身以外的所有节点 IP"""
        peers = []
        for nick, ip in self.channel_members.items():
            if nick != my_nick:
                decoded_ip = SatoshiIRCDiscovery.decode_nick_to_ip(nick)
                if decoded_ip:
                    peers.append(decoded_ip)
        return peers

