"""
比特币原始密码学工具库 (Pure Python Implementation)
实现中本聪在 v0.1 代码中使用的哈希函数与 secp256k1 椭圆曲线数字签名算法 (ECDSA)
"""

import hashlib
import hmac
import os
import struct

# ==========================================
# 1. 基础哈希算法
# ==========================================

def sha256(data: bytes) -> bytes:
    """单次 SHA-256 哈希"""
    return hashlib.sha256(data).digest()

def hash256(data: bytes) -> bytes:
    """双重 SHA-256 哈希 (Satoshi Hash256)"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def ripemd160(data: bytes) -> bytes:
    """RIPEMD-160 哈希"""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()

def hash160(data: bytes) -> bytes:
    """Hash160: RIPEMD160(SHA256(data))，用于生成比特币地址公钥哈希"""
    return ripemd160(sha256(data))


# ==========================================
# 2. secp256k1 椭圆曲线参数与算法
# ==========================================

# secp256k1 曲线方程: y^2 = x^3 + 7 (mod P)
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

def _modinv(a: int, m: int) -> int:
    """模逆元扩展欧几里得算法"""
    return pow(a, m - 2, m)

def point_add(pt1, pt2):
    """椭圆曲线上两点相加"""
    if pt1 is None:
        return pt2
    if pt2 is None:
        return pt1

    x1, y1 = pt1
    x2, y2 = pt2

    if x1 == x2 and y1 != y2:
        return None  # 无穷远点

    if x1 == x2:
        # 倍点公式: lambda = (3 * x1^2) / (2 * y1)
        slope = (3 * x1 * x1) * _modinv(2 * y1, P) % P
    else:
        # 点加公式: lambda = (y2 - y1) / (x2 - x1)
        slope = (y2 - y1) * _modinv(x2 - x1, P) % P

    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)

def point_mul(k: int, pt=G):
    """标量乘法 (Double-and-Add) 计算 k * P"""
    res = None
    curr = pt
    k = k % N
    while k > 0:
        if k & 1:
            res = point_add(res, curr)
        curr = point_add(curr, curr)
        k >>= 1
    return res

def privkey_to_pubkey(privkey_int: int, compressed: bool = False) -> bytes:
    """私钥整数转化为原始公钥字节 (中本聪 v0.1 使用未压缩的 65 字节公钥)"""
    pt = point_mul(privkey_int, G)
    x, y = pt
    if compressed:
        prefix = b'\x02' if y % 2 == 0 else b'\x03'
        return prefix + x.to_bytes(32, 'big')
    else:
        # 0x04 + 32字节x + 32字节y (65 字节未压缩公钥)
        return b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

def parse_pubkey(pubkey_bytes: bytes):
    """解析公钥字节为点 (x, y)"""
    if len(pubkey_bytes) == 65 and pubkey_bytes[0] == 4:
        x = int.from_bytes(pubkey_bytes[1:33], 'big')
        y = int.from_bytes(pubkey_bytes[33:65], 'big')
        return (x, y)
    elif len(pubkey_bytes) == 33 and pubkey_bytes[0] in (2, 3):
        x = int.from_bytes(pubkey_bytes[1:33], 'big')
        y_sq = (pow(x, 3, P) + 7) % P
        y = pow(y_sq, (P + 1) // 4, P)
        if (pubkey_bytes[0] == 2 and y % 2 != 0) or (pubkey_bytes[0] == 3 and y % 2 == 0):
            y = P - y
        return (x, y)
    raise ValueError(f"Invalid public key format or length: {len(pubkey_bytes)}")

# ==========================================
# 3. ECDSA 签名与 DER 编码/校验
# ==========================================

def ecdsa_sign(message_hash: bytes, privkey_int: int, k: int = None) -> (int, int):
    """使用私钥对 32 字节哈希进行 ECDSA 签名 (r, s)"""
    z = int.from_bytes(message_hash, 'big')
    if k is None:
        # RFC 6979 确定性生成 k 避免弱随机数漏洞
        k = int.from_bytes(hash256(privkey_int.to_bytes(32, 'big') + message_hash), 'big') % (N - 1) + 1
    
    r_pt = point_mul(k, G)
    r = r_pt[0] % N
    if r == 0:
        return ecdsa_sign(message_hash, privkey_int, k + 1)
    
    k_inv = _modinv(k, N)
    s = (k_inv * (z + r * privkey_int)) % N
    if s == 0:
        return ecdsa_sign(message_hash, privkey_int, k + 1)
    
    # BIP 62 低 s 规范化
    if s > N // 2:
        s = N - s
    return (r, s)

def ecdsa_verify(message_hash: bytes, pubkey_bytes: bytes, r: int, s: int) -> bool:
    """验证 ECDSA 签名"""
    if not (1 <= r < N and 1 <= s < N):
        return False
    try:
        pt = parse_pubkey(pubkey_bytes)
    except Exception:
        return False

    z = int.from_bytes(message_hash, 'big')
    w = _modinv(s, N)
    u1 = (z * w) % N
    u2 = (r * w) % N
    
    res = point_add(point_mul(u1, G), point_mul(u2, pt))
    if res is None:
        return False
    return (res[0] % N) == r

def encode_der(r: int, s: int) -> bytes:
    """将 (r, s) 编码为标准 DER 格式字节序列"""
    def encode_int(n: int) -> bytes:
        b = n.to_bytes((n.bit_length() + 7) // 8 or 1, 'big')
        if b[0] & 0x80:
            b = b'\x00' + b
        return b'\x02' + bytes([len(b)]) + b
    
    rb = encode_int(r)
    sb = encode_int(s)
    body = rb + sb
    return b'\x30' + bytes([len(body)]) + body

def decode_der(der_bytes: bytes) -> (int, int):
    """从 DER 编码中解码出 (r, s)"""
    if der_bytes[0] != 0x30:
        raise ValueError("Invalid DER header")
    idx = 2
    if der_bytes[idx] != 0x02:
        raise ValueError("Invalid r marker")
    r_len = der_bytes[idx + 1]
    r = int.from_bytes(der_bytes[idx + 2 : idx + 2 + r_len], 'big')
    
    idx = idx + 2 + r_len
    if der_bytes[idx] != 0x02:
        raise ValueError("Invalid s marker")
    s_len = der_bytes[idx + 1]
    s = int.from_bytes(der_bytes[idx + 2 : idx + 2 + s_len], 'big')
    return (r, s)

