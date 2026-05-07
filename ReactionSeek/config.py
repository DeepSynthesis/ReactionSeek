# -*- coding: UTF-8 -*-
"""
ReactionSeek 统一配置模块
所有 API key、代理、模型等配置均从 .env 文件读取。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 自动查找并加载项目根目录下的 .env 文件
# 从当前文件向上查找，直到找到包含 .env 的目录
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# --- OpenAI API 配置 ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# --- HTTP 代理 ---
HTTP_PROXY = os.getenv("HTTP_PROXY", "")
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")

# --- 智谱AI GLM 配置 ---
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")

# --- 重试/延迟配置 ---
API_DELAY = int(os.getenv("API_DELAY", "20"))  # API 调用间隔（秒），避免触发频率限制
