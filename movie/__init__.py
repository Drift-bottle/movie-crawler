"""
movie-crawler 异步 HTTP 请求客户端与通用工具集。

主要提供：
    - Requests: 基于 httpx 的异步请求客户端，集成智能编码检测、耗时监控与 robots.txt 校验
    - logging_configuration: 双通道日志配置（控制台 INFO + 文件 DEBUG）
    - logger: 异步函数执行时间计时装饰器
    - get_position_with_edge_login: 通过 Playwright CDP 复用 Edge 浏览器登录态获取 Cookie
"""

from .client import Requests
from .utils import logging_configuration, logger, get_position_with_edge_login

__all__ = [
    "Requests",
    "logging_configuration",
    "logger",
    "get_position_with_edge_login",
]