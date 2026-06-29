document.addEventListener('DOMContentLoaded', function() {
    // ---------- DOM 元素 ----------
    const fetchBtn = document.getElementById('fetchBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const loadingDiv = document.getElementById('loading');
    const trendsSection = document.getElementById('trendsSection');
    const promptSection = document.getElementById('promptSection');
    const trendsList = document.getElementById('trendsList');
    const promptParams = document.getElementById('promptParams');
    const trendCount = document.getElementById('trendCount');
    const labelIcons = {
    "任务": "⚙️",
    "语音": "🎤",
    "语言": "🌐",
    "许可证": "📄",
    "其他": "🏷️",
    "模型类型": "🔖",
    "学科分类": "📚",
    "交叉分类": "🔀",
    "主题": "🏷️"
};
// 标签显示顺序（按此顺序渲染）
    const tagOrder = ["任务", "语言", "语音",  "许可证", "其他", "学科分类", "交叉分类", "主题"];
    let currentData = null;

    // ---------- 渲染函数 ----------
function renderTrends(trends) {
    if (!trends || trends.length === 0) {
        trendsList.innerHTML = '<p style="color: var(--text-muted);">暂无数据，请稍后重试。</p >';
        return;
    }

    let html = '';
    trends.forEach(item => {
        const date = item.date || '未知日期';
        const source = item.source || '未知来源';
        const link = item.link || '#';
        const isValid = link && (link.startsWith('http://') || link.startsWith('https://'));

        // 生成标签（带图标）
        let tagHtml = '';
        if (item.categorized_tags) {
            // 按照指定顺序渲染标签
            for (const label of tagOrder) {
                const values = item.categorized_tags[label];
                if (values && values.length) {
                    // 获取图标，没有则用默认
                    const icon = labelIcons[label] || '📌';
                    const uniqueValues = [...new Set(values)];
                    tagHtml += `<div style="margin-top:6px;"><span style="font-weight:500;color:#666;">${icon} ${label}:</span> `;
                    tagHtml += uniqueValues.map(v => `<span class="tag-badge">${v}</span>`).join(' ');
                    tagHtml += `</div>`;
                }
            }
        }

        // 组装卡片
        html += `
            <a href="${link}" ${isValid ? 'target="_blank"' : ''} class="trend-item-link" style="text-decoration: none; display: block; color: inherit;">
                <div class="trend-item">
                    <div class="title">${item.title}</div>
                    <div class="meta">
                        <span class="source-badge">${source}</span>
                        <span>📅 ${date}</span>
                    </div>
                    <div class="summary">${item.summary}</div>
                    ${tagHtml}
                </div>
            </a >
        `;
    });
    trendsList.innerHTML = html;
}

    function renderPromptParams(params) {
        if (!params || Object.keys(params).length === 0) {
            promptParams.textContent = '暂无生成的参数。';
            return;
        }
        let html = '';
        for (const [key, value] of Object.entries(params)) {
            html += `<div class="param-block"><span class="param-key">${key}:</span><span class="param-value">${value}</span></div>`;
        }
        promptParams.innerHTML = html;
    }

    // ---------- 获取最新趋势 ----------
    fetchBtn.addEventListener('click', async function() {
        fetchBtn.disabled = true;
        fetchBtn.innerHTML = '<span class="btn-icon">⏳</span> 加载中...';
        loadingDiv.style.display = 'block';
        trendsSection.style.display = 'none';
        promptSection.style.display = 'none';
        if (refreshBtn) refreshBtn.style.display = 'none';

        try {
            const response = await fetch('/api/trends');
            const result = await response.json();

            if (result.code === 0) {
                currentData = result.data;
                renderTrends(currentData.trends);
                renderPromptParams(currentData.prompt_params);
                trendsSection.style.display = 'block';
                promptSection.style.display = 'block';
                if (trendCount) {
                    trendCount.textContent = currentData.trends.length + ' 条';
                }
                if (refreshBtn) refreshBtn.style.display = 'inline-block';
                trendsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert('获取数据失败: ' + result.message);
            }
        } catch (err) {
            alert('请求异常: ' + err.message);
        } finally {
            loadingDiv.style.display = 'none';
            fetchBtn.disabled = false;
            fetchBtn.innerHTML = '<span class="btn-icon">📡</span> 获取最新趋势';
        }
    });

    // ---------- 换一批 ----------
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function() {
            this.disabled = true;
            this.textContent = '⏳ 刷新中...';
            try {
                const response = await fetch('/api/refresh');
                const result = await response.json();
                if (result.code === 0) {
                    currentData = result.data;
                    renderTrends(currentData.trends);
                    renderPromptParams(currentData.prompt_params);
                    if (trendCount) {
                        trendCount.textContent = currentData.trends.length + ' 条';
                    }
                    // 自动配图（如果已经集成 Agnes AI）
                    const promptText = document.querySelector('.param-value')?.textContent;
                    if (promptText) {
                        try {
                            const imgRes = await fetch('/api/generate_image', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ prompt: promptText })
                            });
                            const imgData = await imgRes.json();
                            if (imgData.code === 0 && imgData.data.image_url) {
                                const container = document.getElementById('generated-image');
                                if (container) {
                                    container.innerHTML = `< img src="${imgData.data.image_url}" alt="生成的图片" style="max-width:100%; border-radius:12px; margin-top:20px;">`;
                                }
                            }
                        } catch(err) {
                            console.error('配图失败:', err);
                        }
                    }
                } else {
                    alert('刷新失败: ' + result.message);
                }
            } catch (err) {
                alert('请求异常: ' + err.message);
            } finally {
                this.disabled = false;
                this.textContent = '🔄 换一批';
            }
        });
    }

    // ---------- 鼠标光晕 ----------
    document.addEventListener('mousemove', (e) => {
        const glow = document.getElementById('mouse-glow') || (() => {
            const el = document.createElement('div');
            el.id = 'mouse-glow';
            el.style.cssText = 'position:fixed;width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(79,124,255,0.06),transparent 70%);pointer-events:none;z-index:-1;transform:translate(-50%,-50%);';
            document.body.appendChild(el);
            return el;
        })();
        glow.style.left = e.clientX + 'px';
        glow.style.top = e.clientY + 'px';
    });
});

// ========== 独立时钟（不依赖 DOMContentLoaded） ==========
(function() {
    function updateClock() {
        const el = document.getElementById('current-time');
        if (!el) return;
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        el.textContent = `⏱️ ${h}:${m}:${s}`;
    }
    // 立即执行一次
    updateClock();
    // 每秒更新
    setInterval(updateClock, 1000);
})();