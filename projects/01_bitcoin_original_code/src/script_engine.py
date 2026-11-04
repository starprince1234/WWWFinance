"""
中本聪原始比特币脚本引擎 (Satoshi Bitcoin Script Engine Emulator)
基于 Forth 语言风格的基于栈 (Stack-based) 虚拟机
支持单步调试追踪、P2PK、P2PKH、多签以及经典堆栈操作符
"""

from typing import List, Tuple, Any, Optional
from .crypto import hash160, hash256, sha256, ripemd160, ecdsa_verify, decode_der

# ==========================================
# 1. 操作码常量定义 (Opcodes)
# ==========================================
OP_0 = 0x00
OP_FALSE = 0x00
OP_1 = 0x51
OP_TRUE = 0x51
OP_2 = 0x52
OP_3 = 0x53
OP_4 = 0x54
OP_5 = 0x55
OP_6 = 0x56
OP_7 = 0x57
OP_8 = 0x58
OP_9 = 0x59
OP_10 = 0x5a
OP_11 = 0x5b
OP_12 = 0x5c
OP_13 = 0x5d
OP_14 = 0x5e
OP_15 = 0x5f
OP_16 = 0x60

# 堆栈控制操作码
OP_NOP = 0x61
OP_VERIFY = 0x69
OP_RETURN = 0x6a
OP_TOALTSTACK = 0x6b
OP_FROMALTSTACK = 0x6c
OP_DROP = 0x75
OP_DUP = 0x76
OP_SWAP = 0x7c
OP_OVER = 0x7b
OP_ROT = 0x7b
OP_2DUP = 0x6e

# 逻辑与运算
OP_EQUAL = 0x87
OP_EQUALVERIFY = 0x88
OP_1ADD = 0x8b
OP_1SUB = 0x8c
OP_NEGATE = 0x8f
OP_ABS = 0x90
OP_NOT = 0x91
OP_0NOTEQUAL = 0x92
OP_ADD = 0x93
OP_SUB = 0x94

# 密码学操作码
OP_RIPEMD160 = 0xa6
OP_SHA1 = 0xa7
OP_SHA256 = 0xa8
OP_HASH160 = 0xa9
OP_HASH256 = 0xaa
OP_CHECKSIG = 0xac
OP_CHECKSIGVERIFY = 0xad
OP_CHECKMULTISIG = 0xae

OP_NAMES = {
    0x00: "OP_0",
    0x51: "OP_1",
    0x52: "OP_2",
    0x53: "OP_3",
    0x69: "OP_VERIFY",
    0x6a: "OP_RETURN",
    0x6b: "OP_TOALTSTACK",
    0x6c: "OP_FROMALTSTACK",
    0x75: "OP_DROP",
    0x76: "OP_DUP",
    0x7c: "OP_SWAP",
    0x6e: "OP_2DUP",
    0x87: "OP_EQUAL",
    0x88: "OP_EQUALVERIFY",
    0x93: "OP_ADD",
    0x94: "OP_SUB",
    0xa6: "OP_RIPEMD160",
    0xa8: "OP_SHA256",
    0xa9: "OP_HASH160",
    0xaa: "OP_HASH256",
    0xac: "OP_CHECKSIG",
    0xad: "OP_CHECKSIGVERIFY",
    0xae: "OP_CHECKMULTISIG",
}


def _cast_to_bool(val: bytes) -> bool:
    """根据中本聪源码，空字节或者负零/正零视作 False，其余为 True"""
    if not val:
        return False
    for i in range(len(val)):
        if val[i] != 0:
            # 最后一个字节如果是 0x80 (负零)，且前面都为 0，则为 False
            if i == len(val) - 1 and val[i] == 0x80:
                return False
            return True
    return False

def _decode_num(val: bytes) -> int:
    """小端有符号整数解码 (CScriptNum)"""
    if not val:
        return 0
    res = 0
    for i, b in enumerate(val):
        res |= (b & (0x7f if i == len(val) - 1 else 0xff)) << (8 * i)
    if val[-1] & 0x80:
        res = -res
    return res

def _encode_num(val: int) -> bytes:
    """小端有符号整数编码 (CScriptNum)"""
    if val == 0:
        return b''
    neg = val < 0
    val = abs(val)
    res = bytearray()
    while val > 0:
        res.append(val & 0xff)
        val >>= 8
    if res[-1] & 0x80:
        res.append(0x80 if neg else 0x00)
    elif neg:
        res[-1] |= 0x80
    return bytes(res)


class ScriptEngine:
    """中本聪 v0.1 堆栈脚本解释器"""

    def __init__(self, trace: bool = False):
        self.stack: List[bytes] = []
        self.altstack: List[bytes] = []
        self.trace = trace
        self.trace_logs: List[str] = []

    def _log(self, msg: str):
        if self.trace:
            self.trace_logs.append(msg)
            print(f"[Script Trace] {msg}")

    def execute(self, script_sig: List[Any], script_pubkey: List[Any], tx_hash: Optional[bytes] = None) -> bool:
        """
        完整执行比特币交易验证逻辑：
        1. 运行 解锁脚本 (scriptSig)
        2. 继承当前栈状态，运行 锁定脚本 (scriptPubKey)
        3. 检查栈顶结果是否为 True
        """
        self.stack = []
        self.altstack = []
        self.trace_logs = []

        self._log("=== 开始执行解锁脚本 (scriptSig) ===")
        if not self._eval_stream(script_sig, tx_hash):
            return False

        self._log(f"=== 解锁脚本执行完毕，当前堆栈深度: {len(self.stack)} ===")

        self._log("=== 开始执行锁定脚本 (scriptPubKey) ===")
        if not self._eval_stream(script_pubkey, tx_hash):
            return False

        if not self.stack:
            self._log("执行失败: 最终堆栈为空！")
            return False

        final_val = self.stack[-1]
        success = _cast_to_bool(final_val)
        self._log(f"=== 脚本验证完毕: 栈顶值={final_val.hex() if isinstance(final_val, bytes) else final_val}, 判定结果={'PASS' if success else 'FAIL'} ===")
        return success

    def _eval_stream(self, tokens: List[Any], tx_hash: Optional[bytes]) -> bool:
        for token in tokens:
            if isinstance(token, bytes):
                # 直接压入数据
                self.stack.append(token)
                self._log(f"PUSH DATA ({len(token)} bytes): {token.hex()[:24]}... | 栈深度: {len(self.stack)}")
                continue

            if isinstance(token, int):
                op = token
                name = OP_NAMES.get(op, f"OP_{hex(op)}")

                if op == OP_0:
                    self.stack.append(b'')
                    self._log(f"{name} -> 压入空字节")
                elif 0x51 <= op <= 0x60:
                    num = op - 0x50
                    self.stack.append(_encode_num(num))
                    self._log(f"{name} -> 压入常数 {num}")
                elif op == OP_DUP:
                    if len(self.stack) < 1:
                        return False
                    self.stack.append(self.stack[-1])
                    self._log(f"{name} -> 复制栈顶元素")
                elif op == OP_2DUP:
                    if len(self.stack) < 2:
                        return False
                    self.stack.extend(self.stack[-2:])
                    self._log(f"{name} -> 复制栈顶前两个元素")
                elif op == OP_DROP:
                    if len(self.stack) < 1:
                        return False
                    self.stack.pop()
                    self._log(f"{name} -> 丢弃栈顶元素")
                elif op == OP_SWAP:
                    if len(self.stack) < 2:
                        return False
                    self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
                    self._log(f"{name} -> 交换栈顶前两个元素")
                elif op == OP_ADD:
                    if len(self.stack) < 2:
                        return False
                    a = _decode_num(self.stack.pop())
                    b = _decode_num(self.stack.pop())
                    self.stack.append(_encode_num(b + a))
                    self._log(f"{name} -> 计算 {b} + {a} = {b+a}")
                elif op == OP_SUB:
                    if len(self.stack) < 2:
                        return False
                    a = _decode_num(self.stack.pop())
                    b = _decode_num(self.stack.pop())
                    self.stack.append(_encode_num(b - a))
                    self._log(f"{name} -> 计算 {b} - {a} = {b-a}")
                elif op == OP_EQUAL:
                    if len(self.stack) < 2:
                        return False
                    a = self.stack.pop()
                    b = self.stack.pop()
                    res = b'\x01' if a == b else b''
                    self.stack.append(res)
                    self._log(f"{name} -> 比较相等: {a == b}")
                elif op == OP_EQUALVERIFY:
                    if len(self.stack) < 2:
                        return False
                    a = self.stack.pop()
                    b = self.stack.pop()
                    if a != b:
                        self._log(f"{name} -> 验证失败: {a.hex()} != {b.hex()}")
                        return False
                    self._log(f"{name} -> 验证成功且消耗两元素")
                elif op == OP_HASH160:
                    if len(self.stack) < 1:
                        return False
                    item = self.stack.pop()
                    h = hash160(item)
                    self.stack.append(h)
                    self._log(f"{name} -> 计算 Hash160: {h.hex()}")
                elif op == OP_HASH256:
                    if len(self.stack) < 1:
                        return False
                    item = self.stack.pop()
                    h = hash256(item)
                    self.stack.append(h)
                    self._log(f"{name} -> 计算 Hash256: {h.hex()}")
                elif op == OP_SHA256:
                    if len(self.stack) < 1:
                        return False
                    item = self.stack.pop()
                    h = sha256(item)
                    self.stack.append(h)
                    self._log(f"{name} -> 计算 SHA256: {h.hex()}")
                elif op == OP_CHECKSIG or op == OP_CHECKSIGVERIFY:
                    if len(self.stack) < 2:
                        return False
                    pubkey = self.stack.pop()
                    sig_der = self.stack.pop()
                    if tx_hash is None:
                        self._log("未提供待签名交易哈希 tx_hash")
                        return False
                    
                    try:
                        r, s = decode_der(sig_der)
                        valid = ecdsa_verify(tx_hash, pubkey, r, s)
                    except Exception as e:
                        self._log(f"签名格式解析错误: {e}")
                        valid = False

                    if op == OP_CHECKSIG:
                        self.stack.append(b'\x01' if valid else b'')
                        self._log(f"OP_CHECKSIG 验证结果: {'有效 (PASS)' if valid else '无效 (FAIL)'}")
                    else: # OP_CHECKSIGVERIFY
                        if not valid:
                            self._log("OP_CHECKSIGVERIFY 失败!")
                            return False
                        self._log("OP_CHECKSIGVERIFY 成功")
                else:
                    self._log(f"未支持的操作码: {hex(op)}")
                    return False
        return True

