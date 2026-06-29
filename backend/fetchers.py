# -*- coding: utf-8 -*-
"""
数据抓取模块：从 arXiv、GitHub、Hugging Face 获取最新技术动态
"""

import requests
from huggingface_hub import HfApi
from datetime import datetime, timedelta
from .import config
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_arxiv(max_results=None):
    if max_results is None:
        max_results = config.MAX_RESULTS["arxiv"]
    query = config.SEARCH_QUERIES["arxiv"]
    
    # 使用 arXiv API 的 RSS 接口
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    
    try:
        import requests
        import xml.etree.ElementTree as ET
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        
        # 命名空间
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        results = []
        for entry in root.findall('atom:entry', ns):
            # 提取标题、摘要、链接、日期
            title = entry.find('atom:title', ns).text
            summary = entry.find('atom:summary', ns).text[:200] + "..."
            link = entry.find('atom:id', ns).text
            published = entry.find('atom:published', ns).text[:10]  # 取日期
            
            # ===== 提取学科分类 =====
            # arXiv 的分类信息在 <arxiv:primary_category> 和 <category> 标签中
            categories = []
            primary = entry.find('{http://arxiv.org/schemas/atom}primary_category')
            if primary is not None:
                cat = primary.get('term')
                if cat:
                    categories.append(cat)
            # 其他分类（交叉分类）
            for cat_elem in entry.findall('{http://arxiv.org/schemas/atom}category'):
                cat = cat_elem.get('term')
                if cat and cat not in categories:
                    categories.append(cat)
            
            categorized_tags = {}
            if categories:
                main = categories[0] if categories else ""
                cross = categories[1:] if len(categories) > 1 else []
                if main:
                    categorized_tags["学科分类"] = [main]
                if cross:
                    categorized_tags["交叉分类"] = cross
            
            results.append({
                "title": title,
                "summary": summary,
                "link": link,
                "date": published,
                "source": "arXiv",
                "categorized_tags": categorized_tags
            })
        logger.info(f"arXiv 抓取成功，共 {len(results)} 条")
        return results
    except Exception as e:
        logger.error(f"arXiv 抓取失败: {e}")
        return []


def fetch_github(max_results=None):
    if max_results is None:
        max_results = config.MAX_RESULTS["github"]
    query = config.SEARCH_QUERIES["github"]
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": max_results
    }
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    # ===== 新增：如果配置了 GitHub Token，添加认证头 =====
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    # ===== 新增结束 =====

    results = []
    try:
        resp = requests.get(config.GITHUB_API_URL, params=params, 
                            headers=headers, timeout=config.REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("items", []):
                # ===== 新增：提取仓库主题（Topics） =====
                topics = item.get("topics", [])  # 主题列表
                categorized_tags = {}
                if topics:
                    categorized_tags["主题"] = topics
                # ===== 新增结束 =====

                link = item.get("html_url", "")
                if not link:
                    link = f"https://github.com/{item.get('full_name', '')}"
                results.append({
                    "title": item["name"],
                    "summary": item.get("description", "无描述")[:200],
                    "link": link,
                    "date": item["updated_at"][:10],
                    "source": "GitHub",
                    "categorized_tags": categorized_tags   # 新增字段
                })
            logger.info(f"GitHub 抓取成功，共 {len(results)} 条")
        else:
            logger.error(f"GitHub 请求失败，状态码: {resp.status_code}")
    except Exception as e:
        logger.error(f"GitHub 抓取异常: {e}")
    return results

def categorize_hf_tags(tags):
    """将 HuggingFace 标签分为：任务、语言、语音、许可证、其他"""
    categories = {
        "任务": [],
        "语言": [],
        "语音": [],
        "许可证": [],
        "其他": []
    }
    # 任务关键词映射
    task_keywords = {
        "text-generation": "文本生成",
        "image-text-to-text": "图像转文本",
        "automatic-speech-recognition": "语音识别",
        "speech-summarization": "语音摘要",
        "speech-translation": "语音翻译",
        "visual-question-answering": "视觉问答",
        "text-to-speech": "文本转语音",
        "voice-cloning": "语音克隆",
        "image-feature-extraction": "图像特征提取"
    }
    # 语言关键词映射（ISO 639-1 代码 → 中文名）
    lang_keywords = {
        "en": "英语", "zh": "中文", "nl": "荷兰语", "fr": "法语",
        "de": "德语", "he": "希伯来语", "hu": "匈牙利语", "it": "意大利语",
        "ja": "日语", "ko": "韩语", "no": "挪威语", "pl": "波兰语",
        "pt": "葡萄牙语", "ru": "俄语", "es": "西班牙语", "sv": "瑞典语",
        "th": "泰语", "tr": "土耳其语", "uk": "乌克兰语", "ar": "阿拉伯语"
    }
    # 语音相关关键词（用于归类）
    voice_keywords = ["audio", "speech", "tts", "voice", "higgs-audio"]
    
    for tag in tags:
        if tag.startswith("license:"):
            categories["许可证"].append(tag.replace("license:", ""))
        elif tag in task_keywords:
            categories["任务"].append(task_keywords[tag])
        elif tag in lang_keywords:
            categories["语言"].append(lang_keywords[tag])
        elif any(vk in tag.lower() for vk in voice_keywords):
            categories["语音"].append(tag)
        else:
            categories["其他"].append(tag)
    return categories

def fetch_huggingface(max_results=None):
    """
    从 Hugging Face 获取最新的多模态模型
    """
    if max_results is None:
        max_results = config.MAX_RESULTS["huggingface"]
    
    query = config.SEARCH_QUERIES["huggingface"]
    api = HfApi()
    results = []
    try:
        # 使用 list_models 搜索，按下载量或更新时间排序（需要遍历）
        # 注意：list_models 返回全部，我们手动过滤并取前 N 个
        models = api.list_models(search=query, sort="downloads", direction=-1)
        count = 0
        for model in models:
            if count >= max_results:
                break
            # 只取视觉/多模态相关（通过标签或名称简单过滤）
            if any(kw in model.id.lower() for kw in ["vision", "image", "video", "multimodal"]):
                results.append({
                    "title": model.id,
                    "summary": f"下载量: {model.downloads or 0}",
                    "link": f"https://huggingface.co/{model.id}",
                    "date": datetime.now().strftime("%Y-%m-%d"),  # API 不直接提供更新时间，用当前日期
                    "source": "HuggingFace",
                    "tags": model.tags or [],                              #保存原始标签
                    "categorized_tags": categorize_hf_tags(model.tags or [])   #分类结果
                })
                count += 1
        logger.info(f"HuggingFace 抓取成功，共 {len(results)} 条")
    except Exception as e:
        logger.error(f"HuggingFace 抓取异常: {e}")
    return results


def fetch_all():
    """
    并行抓取所有平台数据
    """
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_arxiv = executor.submit(fetch_arxiv)
        future_github = executor.submit(fetch_github)
        future_hf = executor.submit(fetch_huggingface)
        
        results = []
        results.extend(future_arxiv.result())
        results.extend(future_github.result())
        results.extend(future_hf.result())
    # 按日期排序（降序）
    results.sort(key=lambda x: x["date"], reverse=True)
    return results