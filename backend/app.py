# -*- coding: utf-8 -*-
"""
Flask 主应用：提供 Web 界面和 API 接口
"""

from flask import Flask, render_template, jsonify, send_from_directory
from .agent import run_agent
import os
import logging
from flask import request
from .agnes_client import generate_image


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__, 
            template_folder='../frontend')  # 前端模板目录
            # static_folder='../frontend')    # 静态文件目录

@app.route('/api/generate_image', methods=['POST'])
def generate_image_api():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({"code": -1, "message": "请输入提示词"}), 400
    image_url = generate_image(prompt)
    if image_url:
        return jsonify({"code": 0, "data": {"image_url": image_url}})
    return jsonify({"code": -1, "message": "图像生成失败"}), 500


@app.route('/')
def index():
    """返回主页面"""
    return render_template('index.html')

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """
    API 接口：触发 Agent 并返回结果
    """
    try:
        result = run_agent()
        return jsonify({
            "code": 0,
            "message": "success",
            "data": result
        })
    except Exception as e:
        app.logger.error(f"Agent 执行失败: {e}")
        return jsonify({
            "code": -1,
            "message": str(e),
            "data": None
        }), 500

@app.route('/api/refresh', methods=['GET'])
def refresh_trends():
    """随机换一批（随机采样）"""
    try:
        result = run_agent(randomize=True)
        return jsonify({
            "code": 0,
            "message": "success",
            "data": result
        })
    except Exception as e:
        app.logger.error(f"刷新失败: {e}")
        return jsonify({
            "code": -1,
            "message": str(e),
            "data": None
        }), 500
# （可选）静态文件路由，如果使用 send_from_directory
# 但由于 template_folder 指向 frontend，Flask 会自动服务静态文件

if __name__ == '__main__':
    # 生产环境建议使用 gunicorn 等，开发环境使用 debug
    app.run(host='0.0.0.0', port=5000, debug=True)