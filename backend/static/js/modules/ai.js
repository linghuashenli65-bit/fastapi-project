import { post } from '../api.js';
import { showToast } from '../utils.js';
import { API_BASE } from '../config.js';

export async function render(container) {
    container.innerHTML = `
        <div class="card">
            <h3>🤖 AI 智能助手</h3>
            <div style="display: flex; gap: 20px; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0;">
                <button id="tab-dispatch" class="tab-btn active">AI 查询（执行SQL）</button>
                <button id="tab-dashboard" class="tab-btn">AI 分析（流式）</button>
            </div>
            <div id="ai-panel">
                <!-- AI 查询面板 -->
                <div id="dispatch-panel">
                    <div class="form-group">
                        <label>选择模型：</label>
                        <select id="dispatch-model">
                            <option value="deepseek">DeepSeek</option>
                            <option value="qwen" selected>通义千问 (Qwen)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>查询内容（自然语言或SQL）：</label>
                        <textarea id="dispatch-query" rows="3" placeholder="例如：查询所有男学生"></textarea>
                    </div>
                    <button id="dispatch-btn" class="btn btn-primary">执行查询</button>
                    <div style="margin-top: 20px;">
                        <strong>执行结果：</strong>
                        <pre id="dispatch-result" style="background:#f1f5f9; padding:12px; border-radius:16px; margin-top:8px; white-space:pre-wrap;"></pre>
                    </div>
                </div>
                <!-- AI 分析面板（流式） -->
                <div id="dashboard-panel" style="display:none;">
                    <div class="form-group">
                        <label>选择模型：</label>
                        <select id="dashboard-model">
                            <option value="deepseek">DeepSeek</option>
                            <option value="qwen" selected>通义千问 (Qwen)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>分析长度：</label>
                        <select id="dashboard-length">
                            <option value="short">简短</option>
                            <option value="medium" selected>中等</option>
                            <option value="long">详细</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>分析问题：</label>
                        <textarea id="dashboard-query" rows="3" placeholder="例如：近三年就业趋势分析"></textarea>
                    </div>
                    <button id="dashboard-btn" class="btn btn-primary">开始流式分析</button>
                    <!-- 进度条容器 -->
                    <div id="dashboard-progress" style="display: none; margin-top: 16px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span id="progress-stage">准备中...</span>
                            <span id="progress-percent">0%</span>
                        </div>
                        <div style="background-color: #e2e8f0; border-radius: 20px; overflow: hidden;">
                            <div id="progress-bar" style="width: 0%; height: 8px; background-color: #3b82f6; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    <!-- 分析结果容器（图表 + 文本） -->
                    <div id="dashboard-result" style="margin-top: 20px;"></div>
                </div>
            </div>
        </div>
    `;

    // Tab 切换逻辑
    const tabDispatch = document.getElementById('tab-dispatch');
    const tabDashboard = document.getElementById('tab-dashboard');
    const dispatchPanel = document.getElementById('dispatch-panel');
    const dashboardPanel = document.getElementById('dashboard-panel');

    function setActiveTab(active) {
        tabDispatch.classList.toggle('active', active === 'dispatch');
        tabDashboard.classList.toggle('active', active === 'dashboard');
        dispatchPanel.style.display = active === 'dispatch' ? 'block' : 'none';
        dashboardPanel.style.display = active === 'dashboard' ? 'block' : 'none';
    }

    tabDispatch.onclick = () => setActiveTab('dispatch');
    tabDashboard.onclick = () => setActiveTab('dashboard');

    // AI 查询 - 调用 /agent/sql 接口
    document.getElementById('dispatch-btn').onclick = async () => {
        const model = document.getElementById('dispatch-model').value;
        const query = document.getElementById('dispatch-query').value.trim();
        if (!query) {
            showToast('请输入查询内容', 'error');
            return;
        }
        const resultDiv = document.getElementById('dispatch-result');
        resultDiv.innerHTML = '<p style="color:#64748b;">执行中...</p>';
        try {
            const res = await post('/agent/sql', { query, model });
            // 统一响应格式：res = { status, messages, datas, pagination }
            const data = res.datas && res.datas[0] ? res.datas[0] : {};
            
            // 检查后端返回的错误：status=0 表示失败
            if (res.status === 0) {
                const messages = res.messages || '未知错误';
                const errorMsg = Array.isArray(messages) ? messages.join('；') : messages;
                resultDiv.innerHTML = `
                    <div style="background:#fee2e2; padding:12px; border-radius:8px; color:#991b1b;">
                        <strong>❌ 后端错误</strong><br>
                        ${escapeHtml(errorMsg)}
                    </div>
                `;
                showToast('查询失败: ' + errorMsg, 'error');
                return;
            }
            
            // 检查是否查询失败（datas中可能包含错误信息）
            if (data.msg && !data.data) {
                resultDiv.innerHTML = `
                    <div style="background:#fee2e2; padding:12px; border-radius:8px; color:#991b1b;">
                        <strong>❌ 查询失败</strong><br>
                        错误信息：${escapeHtml(data.msg || '未知错误')}<br>
                        ${data.sql ? `SQL语句：<pre style="background:#f1f5f9; padding:8px; border-radius:4px; overflow-x:auto;">${escapeHtml(data.sql)}</pre>` : ''}
                    </div>
                `;
                showToast('查询失败: ' + (data.msg || '未知错误'), 'error');
                return;
            }

            // 显示数据表格
            let html = '';
            if (data.data && data.data.length > 0) {
                html = renderDataTable(data.data);
            } else {
                html = `<div style="background:#fef3c7; padding:12px; border-radius:8px;">⚠️ 查询成功，但没有返回数据</div>`;
            }

            resultDiv.innerHTML = html;
        } catch (err) {
            console.error('AI查询失败:', err);
            // 提取有意义的错误信息
            let errorMsg = err.message || '未知错误';
            if (errorMsg.includes('Network Error') || errorMsg.includes('fetch')) {
                errorMsg = '网络连接失败，请检查网络和代理设置';
            } else if (errorMsg.includes('timeout') || errorMsg.includes('Timeout')) {
                errorMsg = '请求超时，请重试';
            }
            
            resultDiv.innerHTML = `
                <div style="background:#fee2e2; padding:12px; border-radius:8px; color:#991b1b;">
                    <strong>❌ 请求失败</strong><br>
                    ${escapeHtml(errorMsg)}
                </div>
            `;
            showToast('查询失败: ' + errorMsg, 'error');
        }
    };

    // 渲染数据表格
    function renderDataTable(data) {
        if (!data || data.length === 0) {
            return '<p>暂无数据</p>';
        }

        // 获取列名（使用第一行的键）
        const columns = Object.keys(data[0]);

        // 计算合适的列宽：每列最少 100px
        const tableWidth = Math.max(1200, columns.length * 100);

        let html = `
            <div style="overflow-x: auto;">
                <table class="data-table" style="min-width: ${tableWidth}px;">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
        `;

        data.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = row[col];
                const displayValue = value === null || value === undefined ? '' : String(value);
                html += `<td>${escapeHtml(displayValue)}</td>`;
            });
            html += '</tr>';
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        return html;
    }

    // HTML 转义函数
    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // AI 分析流式 - 调用 /agent/dashboard
    document.getElementById('dashboard-btn').onclick = async () => {
        const model = document.getElementById('dashboard-model').value;
        const analysisLength = document.getElementById('dashboard-length').value;
        const query = document.getElementById('dashboard-query').value.trim();
        if (!query) {
            showToast('请输入分析问题', 'error');
            return;
        }

        const resultContainer = document.getElementById('dashboard-result');
        const progressContainer = document.getElementById('dashboard-progress');
        const progressStage = document.getElementById('progress-stage');
        const progressPercent = document.getElementById('progress-percent');
        const progressBar = document.getElementById('progress-bar');

        // 重置界面
        resultContainer.innerHTML = '';
        progressContainer.style.display = 'block';
        progressStage.innerText = '开始分析...';
        progressPercent.innerText = '0%';
        progressBar.style.width = '0%';

        // 用于累积数据和图表
        let fullAnalysis = '';
        let chartsData = [];
        let isComplete = false;

        try {
            const response = await fetch(`${API_BASE}/agent/dashboard`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, model, analysis_length: analysisLength })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            // 更新进度
                            if (data.percent !== undefined) {
                                const percent = Math.round(data.percent);
                                progressBar.style.width = percent + '%';
                                progressPercent.innerText = percent + '%';
                            }
                            if (data.message) {
                                progressStage.innerText = data.message;
                            }
                            // 累积文本块（支持多种字段名）
                            if (data.text) fullAnalysis += data.text;
                            if (data.content) fullAnalysis += data.content;
                            if (data.analysis) fullAnalysis += data.analysis;
                            // 累积图表
                            if (data.charts && data.charts.length) {
                                chartsData.push(...data.charts);
                            }
                            // 如果收到 complete 信号，标记完成
                            if (data.stage === 'complete') {
                                isComplete = true;
                            }
                        } catch (e) {
                            console.warn('解析事件失败', e, line);
                        }
                    }
                }
                // 可选：实时显示已累积的文本（如果需要流式打字效果，可在这里渲染）
                // 但为了性能，建议在 complete 后统一渲染
            }

            // 流结束后隐藏进度条
            progressContainer.style.display = 'none';

            // 显示最终总结文本
            if (fullAnalysis.trim()) {
                const analysisBox = document.createElement('div');
                analysisBox.className = 'ai-analysis-text';
                if (typeof marked !== 'undefined') {
                    analysisBox.innerHTML = marked.parse(fullAnalysis);
                } else {
                    analysisBox.innerHTML = fullAnalysis;
                }
                resultContainer.appendChild(analysisBox);
            } else if (!isComplete) {
                // 如果没有收到任何文本且没有 complete 信号，可能后端异常
                resultContainer.innerHTML = `<div class="ai-analysis-text" style="background:#fee2e2;">⚠️ 分析完成但未返回文本内容</div>`;
            }

            // 显示图表（如果有）
            if (chartsData.length) {
                const gridDiv = document.createElement('div');
                gridDiv.className = 'charts-grid';
                resultContainer.appendChild(gridDiv);
                chartsData.forEach((chart, idx) => {
                    const card = document.createElement('div');
                    card.className = 'chart-card';
                    
                    // 标题行 + 翻转按钮
                    const headerDiv = document.createElement('div');
                    headerDiv.style.display = 'flex';
                    headerDiv.style.justifyContent = 'space-between';
                    headerDiv.style.alignItems = 'center';
                    
                    const title = document.createElement('h3');
                    title.innerText = chart.title || `图表 ${idx + 1}`;
                    title.style.margin = '0';
                    headerDiv.appendChild(title);
                    
                    const flipBtn = document.createElement('button');
                    flipBtn.className = 'btn btn-small';
                    flipBtn.innerText = '📊 查看数据';
                    flipBtn.style.fontSize = '12px';
                    flipBtn.style.padding = '4px 8px';
                    headerDiv.appendChild(flipBtn);
                    
                    card.appendChild(headerDiv);
                    
                    // 图表容器
                    const chartDiv = document.createElement('div');
                    const chartId = `dashboard_chart_${idx}`;
                    chartDiv.id = chartId;
                    chartDiv.style.width = '100%';
                    chartDiv.style.height = '340px';
                    card.appendChild(chartDiv);
                    
                    // 表格容器（初始隐藏）
                    const tableDiv = document.createElement('div');
                    const tableId = `dashboard_table_${idx}`;
                    tableDiv.id = tableId;
                    tableDiv.style.display = 'none';
                    tableDiv.style.width = '100%';
                    tableDiv.style.maxHeight = '340px';
                    tableDiv.style.overflow = 'auto';
                    card.appendChild(tableDiv);
                    
                    gridDiv.appendChild(card);
                    
                    // 保存 chartId 和 tableId 供 setTimeout 使用
                    const savedChartId = chartId;
                    const savedTableId = tableId;
                    
                    // 渲染 ECharts
                    setTimeout(() => {
                        const option = chart.option;
                        if (option && typeof echarts !== 'undefined') {
                            const dom = document.getElementById(savedChartId);
                            if (dom) {
                                const myChart = echarts.init(dom);
                                if (option.series && !Array.isArray(option.series)) {
                                    option.series = [option.series];
                                }
                                myChart.setOption(option);
                                window.addEventListener('resize', () => myChart.resize());
                            }
                        }
                    }, 50);
                    
                    // 渲染原始表格数据
                    setTimeout(() => {
                        const tableContainer = document.getElementById(savedTableId);
                        console.log('Table container:', savedTableId, tableContainer, chart.table);
                        if (tableContainer && chart.table) {
                            tableContainer.innerHTML = renderChartTable(chart.table);
                        }
                    }, 50);
                    
                    // 翻转按钮点击事件
                    let isChartView = true;
                    flipBtn.onclick = () => {
                        isChartView = !isChartView;
                        chartDiv.style.display = isChartView ? 'block' : 'none';
                        tableDiv.style.display = isChartView ? 'none' : 'block';
                        flipBtn.innerText = isChartView ? '📊 查看数据' : '📈 查看图表';
                        // 切换时重置图表大小
                        if (isChartView && typeof echarts !== 'undefined') {
                            echarts.getInstanceByDom(chartDiv)?.resize();
                        }
                    };
                });
            }
            
            // 渲染图表对应的表格数据
            function renderChartTable(table) {
                if (!table || !table.columns || !table.rows) {
                    return '<p style="color:#64748b;">暂无数据</p>';
                }
                const columns = table.columns;
                const rows = table.rows;
                
                let html = `
                    <table class="data-table" style="font-size:12px; width:100%;">
                        <thead>
                            <tr>
                                ${columns.map(col => `<th style="padding:6px 8px; background:#f1f5f9;">${escapeHtml(col)}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                `;
                rows.forEach(row => {
                    html += '<tr>';
                    columns.forEach(col => {
                        const value = row[col];
                        const displayValue = value === null || value === undefined ? '' : String(value);
                        html += `<td style="padding:6px 8px; border-bottom:1px solid #e2e8f0;">${escapeHtml(displayValue)}</td>`;
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                return html;
            }
        } catch (err) {
            console.error(err);
            progressContainer.style.display = 'none';
            resultContainer.innerHTML = `<div class="ai-analysis-text" style="background:#fee2e2;">❌ 分析失败: ${err.message}</div>`;
        }
    };
}