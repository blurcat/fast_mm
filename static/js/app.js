(() => {
  // Elements
  const tabs = document.querySelectorAll('.tab');
  const modelSelect = document.getElementById('model-select');
  const logTextarea = document.getElementById('log-textarea');
  const fileInput = document.getElementById('file-input');
  const uploadZone = document.getElementById('upload-zone');
  const fileInfo = document.getElementById('file-info');
  const fileNameEl = document.getElementById('file-name');
  const clearFileBtn = document.getElementById('clear-file');
  const analyzeBtn = document.getElementById('analyze-btn');
  const charCount = document.getElementById('char-count');
  const loading = document.getElementById('loading');
  const errorMsg = document.getElementById('error-msg');
  const results = document.getElementById('results');

  let activeTab = 'paste';
  let uploadedText = '';
  let uploadedFile = null;

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeTab = tab.dataset.tab;
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      document.getElementById(`tab-${activeTab}`).classList.add('active');
      updateAnalyzeBtn();
    });
  });

  // Textarea input
  logTextarea.addEventListener('input', () => {
    const len = logTextarea.value.length;
    charCount.textContent = `${len.toLocaleString()} 字符`;
    updateAnalyzeBtn();
  });

  // File upload - click
  uploadZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) loadFile(fileInput.files[0]);
  });

  // File upload - drag & drop
  uploadZone.addEventListener('dragover', e => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
  uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) loadFile(file);
  });

  function loadFile(file) {
    uploadedFile = file;
    const reader = new FileReader();
    reader.onload = e => {
      uploadedText = e.target.result;
      fileNameEl.textContent = `${file.name} (${formatBytes(file.size)})`;
      fileInfo.classList.remove('hidden');
      uploadZone.classList.add('hidden');
      updateAnalyzeBtn();
    };
    reader.readAsText(file, 'utf-8');
  }

  clearFileBtn.addEventListener('click', () => {
    uploadedText = '';
    uploadedFile = null;
    fileInput.value = '';
    fileNameEl.textContent = '';
    fileInfo.classList.add('hidden');
    uploadZone.classList.remove('hidden');
    updateAnalyzeBtn();
  });

  function updateAnalyzeBtn() {
    const hasContent = activeTab === 'paste'
      ? logTextarea.value.trim().length > 0
      : uploadedText.length > 0;
    analyzeBtn.disabled = !hasContent;
  }

  // Analyze
  analyzeBtn.addEventListener('click', async () => {
    const logText = activeTab === 'paste' ? logTextarea.value : uploadedText;
    if (!logText.trim()) return;

    setLoading(true);
    hideResults();
    hideError();

    const model = modelSelect.value;

    try {
      let res;
      if (activeTab === 'upload' && uploadedFile) {
        const form = new FormData();
        form.append('file', uploadedFile);
        form.append('model', model);
        res = await fetch('/api/upload', { method: 'POST', body: form });
      } else {
        res = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ log_text: logText, model }),
        });
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `请求失败 (${res.status})`);
      }

      const data = await res.json();
      renderResults(data);
    } catch (err) {
      showError(err.message || '分析失败，请检查网络或 API Key 配置');
    } finally {
      setLoading(false);
    }
  });

  function renderResults(data) {
    // Stats bar
    const stats = data.log_stats || {};
    document.getElementById('stats-bar').innerHTML = `
      <div class="stat-item total">
        <div class="stat-value">${(stats.total_lines || 0).toLocaleString()}</div>
        <div class="stat-label">总行数</div>
      </div>
      <div class="stat-item error">
        <div class="stat-value">${stats.error_count || 0}</div>
        <div class="stat-label">错误</div>
      </div>
      <div class="stat-item warn">
        <div class="stat-value">${stats.warning_count || 0}</div>
        <div class="stat-label">警告</div>
      </div>
      <div class="stat-item info">
        <div class="stat-value">${stats.info_count || 0}</div>
        <div class="stat-label">信息</div>
      </div>
    `;

    // Summary
    document.getElementById('summary-text').textContent = data.summary || '无摘要';

    // Errors
    const errorsSection = document.getElementById('errors-section');
    const errorsList = document.getElementById('errors-list');
    if (data.errors && data.errors.length > 0) {
      errorsList.innerHTML = data.errors.map(e => `
        <div class="error-item">
          <div class="error-header">
            <span class="error-type">${escHtml(e.type || '')}</span>
            <span class="badge badge-${e.severity || 'low'}">${e.severity || ''}</span>
            ${e.count > 1 ? `<span class="error-count">x${e.count}</span>` : ''}
          </div>
          <p class="error-desc">${escHtml(e.description || '')}</p>
          ${e.context ? `<p class="error-context">${escHtml(e.context)}</p>` : ''}
        </div>
      `).join('');
      errorsSection.classList.remove('hidden');
    } else {
      errorsSection.classList.add('hidden');
    }

    // Anomalies
    const anomaliesSection = document.getElementById('anomalies-section');
    const anomaliesList = document.getElementById('anomalies-list');
    if (data.anomalies && data.anomalies.length > 0) {
      anomaliesList.innerHTML = data.anomalies.map(a =>
        `<li class="warn-item">${escHtml(a)}</li>`
      ).join('');
      anomaliesSection.classList.remove('hidden');
    } else {
      anomaliesSection.classList.add('hidden');
    }

    // Performance
    const perfSection = document.getElementById('perf-section');
    const perfList = document.getElementById('perf-list');
    if (data.performance_issues && data.performance_issues.length > 0) {
      perfList.innerHTML = data.performance_issues.map(p =>
        `<li class="perf-item">${escHtml(p)}</li>`
      ).join('');
      perfSection.classList.remove('hidden');
    } else {
      perfSection.classList.add('hidden');
    }

    // Suggestions
    const suggestionsSection = document.getElementById('suggestions-section');
    const suggestionsList = document.getElementById('suggestions-list');
    if (data.suggestions && data.suggestions.length > 0) {
      suggestionsList.innerHTML = data.suggestions.map(s => `
        <div class="suggestion-item">
          <div class="suggestion-header">
            <span class="suggestion-issue">${escHtml(s.issue || '')}</span>
            <span class="badge badge-${s.priority || 'low'}">${s.priority || ''}</span>
          </div>
          <div class="suggestion-text">${escHtml(s.suggestion || '')}</div>
        </div>
      `).join('');
      suggestionsSection.classList.remove('hidden');
    } else {
      suggestionsSection.classList.add('hidden');
    }

    // Report (markdown)
    const reportEl = document.getElementById('report-content');
    if (data.report && typeof marked !== 'undefined') {
      reportEl.innerHTML = marked.parse(data.report);
    } else {
      reportEl.textContent = data.report || '';
    }

    // Token info
    if (data.tokens_used) {
      const modelName = modelSelect.options[modelSelect.selectedIndex].text;
      document.getElementById('token-info').textContent =
        `模型：${modelName} · 本次消耗 Token：${data.tokens_used.toLocaleString()}`;
    }

    results.classList.remove('hidden');
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function setLoading(on) {
    loading.classList.toggle('hidden', !on);
    analyzeBtn.disabled = on;
  }

  function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove('hidden');
  }

  function hideError() { errorMsg.classList.add('hidden'); }
  function hideResults() { results.classList.add('hidden'); }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }
})();
