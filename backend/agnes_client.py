import requests
import logging
from .config import AGNES_API_KEY, AGNES_API_URL, AGNES_IMAGE_MODEL

logger = logging.getLogger(__name__)

def generate_image(prompt: str, negative_prompt: str = "", steps: int = 30, width: int = 1024, height: int = 1024):
    """调用 Agnes AI 图像生成 API[reference:9][reference:10]"""
    if not AGNES_API_KEY:
        logger.error("AGNES_API_KEY 未设置")
        return None

    url = f"{AGNES_API_URL}/images/generations"  # 图像生成端点[reference:11]
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json"
    }
    # Agnes 兼容 OpenAI 风格接口[reference:12]
    payload = {
        "model": AGNES_IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": f"{width}x{height}",
        "steps": steps,
        "negative_prompt": negative_prompt
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        image_url = result.get("data", [{}])[0].get("url")
        logger.info(f"图像生成成功: {image_url}")
        return image_url
    except Exception as e:
        logger.error(f"图像生成失败: {e}")
        return None