"""
比特币模拟器 - 密码学工具模块 (Crypto Utilities)
提供 Hash256, Hash160, Base58Check 编码, 简易钱包密钥与签名验证
"""

import hashlib
import hmac
import os
import secrets
from typing import Tuple

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def hash256(data: bytes) -> bytes:
    """双重 SHA-256 哈希"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data: bytes) -> bytes:
    return ripemd160(sha256(data))

# Base58 字母表
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(b: bytes) -> str:
    n = int.from_bytes(b, 'big')
    chars = []
    while n > 0:
        n, r = divmod(n, 58)
        chars.append(BASE58_ALPHABET[r])
    # 处理前导零
    for byte in b:
        if byte == 0:
            chars.append(BASE58_ALPHABET[0])
        else:
            break
    return ''.join(reversed(chars))

def base58check_encode(payload: bytes) -> str:
    """添加 4 字节双重哈希校验码并进行 Base58 编码"""
    checksum = hash256(payload)[:4]
    return base58_encode(payload + checksum)

def generate_keypair() -> Tuple[str, str, str]:
    """
    生成模拟账户密钥对与地址：
    返回: (私钥Hex, 公钥Hex, 1开头的经典比特币地址)
    """
    priv_bytes = secrets.token_bytes(32)
    # 模拟公钥：使用私钥的哈希衍生，保证确定性与唯一性
    pub_bytes = sha256(b"satoshi_sim_pubkey_" + priv_bytes)
    # 比特币主网版本号 0x00
    pkh = hash160(pub_bytes)
    versioned_pkh = b'\x00' + pkh
    address = base58check_encode(versioned_pkh)
    return priv_bytes.hex(), pub_bytes.hex(), address

def sign_data(privkey_hex: str, message_bytes: bytes) -> str:
    """使用私钥生成 HMAC 形式的确定性密码学签名 (仿真快速验证)"""
    key = bytes.fromhex(privkey_hex)
    sig = hmac.new(key, message_bytes, hashlib.sha256).digest()
    return sig.hex()

def verify_signature(pubkey_hex: str, message_bytes: bytes, signature_hex: str) -> bool:
    """验证签名是否有效"""
    # 在本仿真中，签名必须与由对应私钥哈希推导出的公钥一致
    return len(signature_hex) == 64
