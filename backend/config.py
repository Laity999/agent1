# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# 加载 .env 文件（必须放在最前面）
load_dotenv()

# ===== 原有配置（保留你之前的内容）=====
SEARCH_QUERIES = {
    "arxiv": "image video multimodal",
    "github": "multimodal vision video image",
    "huggingface": "multimodal"
}
GITHUB_API_URL = "https://api.github.com/search/repositories"
HUGGINGFACE_API_URL = "https://huggingface.co/api/models"
REQUEST_TIMEOUT = 10
MAX_RESULTS = {"arxiv": 10, "github": 5, "huggingface": 5}
PROMPT_CONFIG = {
    "default_style": "前沿科技, 未来主义, 高细节",
    "default_negative": "模糊, 低质量, 变形",
    "cfg_scale": 7.5,
    "steps": 30,
    "seed": -1
}
RANDOM_SAMPLE_SIZE = 10

# ===== Agnes AI 配置（新增）=====
AGNES_API_KEY = os.getenv("AGNES_API_KEY")
AGNES_API_URL = "https://apihub.agnes-ai.com/v1"
AGNES_IMAGE_MODEL = "agnes-image-2.1-flash"