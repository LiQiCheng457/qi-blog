"""进程内滑动窗口限流（按 IP）。

单 worker 部署下够用；重启后计数清零，可接受。
nginx 已设置 X-Real-IP，直连场景退回 socket 地址。
"""
import collections
import time


_HITS: dict[str, collections.deque] = {}


def client_ip(request) -> str:
    return request.headers.get("x-real-ip") or (request.client.host if request.client else "unknown")


def allow(key: str, limit: int, window_seconds: int = 3600) -> bool:
    """检查 key 是否还能消费一次配额，可以则记录并返回 True"""
    now = time.time()
    hits = _HITS.setdefault(key, collections.deque())
    while hits and now - hits[0] > window_seconds:
        hits.popleft()
    if len(hits) >= limit:
        return False
    hits.append(now)
    return True


def blocked(key: str, limit: int, window_seconds: int = 3600) -> bool:
    """只检查 key 是否已达上限，不记录"""
    hits = _HITS.get(key)
    if not hits:
        return False
    now = time.time()
    while hits and now - hits[0] > window_seconds:
        hits.popleft()
    return len(hits) >= limit


def record(key: str) -> None:
    """手动记录一次（如登录失败）"""
    _HITS.setdefault(key, collections.deque()).append(time.time())
