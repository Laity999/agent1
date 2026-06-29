# -*- coding: utf-8 -*-
"""
Agent 核心模块：整合抓取与优化，提供统一接口
"""

from .fetchers import fetch_all
from .prompt_optimizer import generate_prompt_params
import logging

logger = logging.getLogger(__name__)



def run_agent():
    
    """
    执行 Agent 任务：抓取最新趋势，生成优化提示词参数
    返回结构：
    {
        "trends": [ {title, summary, link, date, source}, ... ],
        "prompt_params": { prompt, negative_prompt, cfg_scale, steps, seed }
    }
    """
    logger.info("Agent 开始执行...")
    trends = fetch_all()
    logger.info(f"抓取到 {len(trends)} 条趋势")
    params = generate_prompt_params(trends)
    logger.info("提示词优化完成")
    for i, t in enumerate(trends[:5]):
        logger.info(f"示例链接: {t['link']}")
    return {
        "trends": trends,
        "prompt_params": params
    }
import random
from .config import RANDOM_SAMPLE_SIZE

def run_agent(randomize=False):
    logger.info("Agent 开始执行...")
    trends = fetch_all()
    logger.info(f"抓取到 {len(trends)} 条趋势")
    
    if randomize and len(trends) > RANDOM_SAMPLE_SIZE:
        # 随机采样并打乱
        trends = random.sample(trends, RANDOM_SAMPLE_SIZE)
        random.shuffle(trends)
        logger.info(f"随机采样 {len(trends)} 条")
    elif randomize:
        # 如果总数不足，则打乱全部
        random.shuffle(trends)
        logger.info(f"总数不足，打乱全部 {len(trends)} 条")
    
    params = generate_prompt_params(trends)
    logger.info("提示词优化完成")
    return {"trends": trends, "prompt_params": params}