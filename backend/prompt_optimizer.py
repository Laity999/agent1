# -*- coding: utf-8 -*-
"""
提示词优化模块：根据抓取结果自动生成高质量的提示词和 API 参数
"""

import re
from collections import Counter
from .import config


def extract_keywords(items, top_n=5):
    """
    从所有 title 和 summary 中提取高频关键词（过滤常见停用词）
    """
    # 简单停用词表
    stopwords = {"the", "a", "an", "of", "for", "on", "at", "to", "in", "with", 
                 "and", "or", "but", "by", "from", "as", "for", "via", "using",
                 "based", "model", "image", "video", "multimodal", "vision"}  # 基础词可忽略
    all_text = " ".join([item["title"] + " " + item["summary"] for item in items])
    # 只提取英文单词（至少3个字母）
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
    # 小写化并过滤
    words = [w.lower() for w in words if w.lower() not in stopwords]
    counter = Counter(words)
    most_common = counter.most_common(top_n)
    return [word for word, _ in most_common]


def generate_prompt_params(items):
    """
    根据抓取结果生成提示词和相关参数
    返回字典，包含 prompt, negative_prompt, cfg_scale, steps 等
    """
    if not items:
        # 无结果时返回默认
        return {
            "prompt": "前沿多模态技术趋势，未来主义风格，高科技视觉",
            "negative_prompt": config.PROMPT_CONFIG["default_negative"],
            "cfg_scale": config.PROMPT_CONFIG["cfg_scale"],
            "steps": config.PROMPT_CONFIG["steps"],
            "seed": config.PROMPT_CONFIG["seed"]
        }
    
    # 提取关键词
    keywords = extract_keywords(items, top_n=6)
    keyword_str = ", ".join(keywords)
    
    # 构造提示词，融入关键词和风格
    base_style = config.PROMPT_CONFIG["default_style"]
    prompt = f"基于最新多模态大模型趋势，包含 {keyword_str}，风格为 {base_style}，高清，细节丰富"
    
    # 附加一些来源信息
    sources = set(item["source"] for item in items)
    source_desc = "，".join(sources)
    prompt += f"，参考来源：{source_desc}"
    
    negative = config.PROMPT_CONFIG["default_negative"]
    cfg = config.PROMPT_CONFIG["cfg_scale"]
    steps = config.PROMPT_CONFIG["steps"]
    seed = config.PROMPT_CONFIG["seed"]
    
    return {
        "prompt": prompt,
        "negative_prompt": negative,
        "cfg_scale": cfg,
        "steps": steps,
        "seed": seed
    }