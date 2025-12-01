"""Utilities."""

import os


async def pid_str() -> str:
    return f'\033[0;34m{os.getpid()}\033[0m'
