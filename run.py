#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目启动脚本
"""

from backend.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 