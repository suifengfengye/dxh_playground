'use strict';

/* 一个 EventSource 收全部事件：
   status → 预热中 / start → 开始计时 / progress → 推进度 / side_done → 冻住数字
   / done → 出结论 / side_error → 报错 */

const SIDES = ['jev', 'llm'];

const VERDICT = {
  yes: { glyph: '✓', text: '匹配' },
  no: { glyph: '✕', text: '不匹配' },
  err: { glyph: '!', text: '解析失败' },
};

const $ = (id) => document.getElementById(id);
const fmtInt = (n) => Math.round(n).toLocaleString('en-US');

const ui = {
  run: $('run'),
  copy: $('copy'),
  status: $('status'),
  verdict: $('verdict'),
  speedup: $('speedup'),
  kpiJev: $('kpi-jev'),
  kpiLlm: $('kpi-llm'),
  kpiAvg: $('kpi-avg'),
  sides: {},
};

for (const side of SIDES) {
  ui.sides[side] = {
    time: $(`${side}-time`),
    bar: $(`${side}-bar`),
    meter: $(`${side}-meter`),
    count: $(`${side}-count`),
    avg: $(`${side}-avg`),
    list: $(`${side}-results`),
  };
}

let source = null;
let rafId = null;
let startedAt = 0;
let total = 6;
let frozen = {};
let collected = { jev: [], llm: [] };
let payload = null;

/* ---------- 计时器：数字肉眼可见地滚 ---------- */

function tick() {
  const elapsed = performance.now() - startedAt;
  for (const side of SIDES) {
    if (!frozen[side]) ui.sides[side].time.textContent = fmtInt(elapsed);
  }
  rafId = requestAnimationFrame(tick);
}

function startTicking() {
  stopTicking();
  startedAt = performance.now();
  rafId = requestAnimationFrame(tick);
}

function stopTicking() {
  if (rafId !== null) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
}

/* ---------- 渲染 ---------- */

function setStatus(text, state) {
  ui.status.textContent = text;
  ui.status.dataset.state = state || '';
}

function reset() {
  stopTicking();
  frozen = {};
  collected = { jev: [], llm: [] };
  payload = null;

  ui.verdict.hidden = true;
  ui.copy.disabled = true;

  for (const side of SIDES) {
    const s = ui.sides[side];
    s.time.textContent = '0';
    s.bar.style.width = '0%';
    s.count.textContent = `0 / ${total} 岗位`;
    s.avg.textContent = '—';
    s.list.replaceChildren();
    s.meter.setAttribute('aria-valuenow', '0');
  }
}

function renderRow(side, result) {
  const kind = result.error ? 'err' : result.match ? 'yes' : 'no';

  const job = document.createElement('span');
  job.className = 'job';
  job.textContent = `${result.id} · ${result.title}`;

  const verdict = document.createElement('span');
  verdict.className = 'badge';
  verdict.dataset.ok = kind;
  verdict.textContent = `${VERDICT[kind].glyph} ${VERDICT[kind].text}`;

  const num = document.createElement('span');
  num.className = 'num';
  // JEV 的 6 个判断共用一次请求，各自的毫秒数没有区分度，所以显示匹配概率；
  // LLM 每个判断都有自己的一次调用，显示这一次的耗时更有信息量。
  num.textContent =
    side === 'jev' && result.prob != null ? result.prob.toFixed(2) : `${fmtInt(result.ms)} ms`;

  const row = document.createElement('li');
  row.append(job, verdict, num);

  // hover 层：鼠标停上去能看到模型原始输出 / 概率
  if (result.error) row.title = result.error;
  else if (result.prob != null) row.title = `匹配概率 ${result.prob.toFixed(3)}`;
  else if (result.raw) row.title = `模型原始输出：${result.raw}`;

  return row;
}

function renderProgress(side, data) {
  const s = ui.sides[side];
  s.bar.style.width = `${(data.done / data.total) * 100}%`;
  s.meter.setAttribute('aria-valuenow', String(data.done));
  s.count.textContent = `${data.done} / ${data.total} 岗位`;
  s.time.textContent = fmtInt(data.elapsed_ms);

  for (const result of data.results) {
    collected[side].push(result);
    s.list.appendChild(renderRow(side, result));
  }
}

function renderSideDone(side, data) {
  frozen[side] = true;
  const s = ui.sides[side];
  s.time.textContent = fmtInt(data.total_ms);
  s.avg.textContent = `平均 ${fmtInt(data.per_item_ms)} ms / 判断`;
  s.bar.style.width = '100%';
  s.count.textContent = `${total} / ${total} 岗位`;
}

function renderDone(data) {
  const { summaries, speedup } = data;
  const jev = summaries.jev || {};
  const llm = summaries.llm || {};

  if (speedup != null) {
    ui.speedup.textContent = speedup.toFixed(1);
    ui.verdict.hidden = false;
  }

  ui.kpiJev.textContent = jev.total_ms != null ? `${fmtInt(jev.total_ms)} ms` : '—';
  ui.kpiLlm.textContent = llm.total_ms != null ? `${fmtInt(llm.total_ms)} ms` : '—';
  ui.kpiAvg.textContent =
    jev.per_item_ms != null && llm.per_item_ms != null
      ? `${fmtInt(jev.per_item_ms)} vs ${fmtInt(llm.per_item_ms)} ms`
      : '—';

  payload = {
    generated_at: new Date().toISOString(),
    job_count: total,
    jev: { calls: 1, ...jev, results: collected.jev },
    llm: { calls: total, ...llm, results: collected.llm },
    speedup,
  };
  ui.copy.disabled = false;

  if (speedup != null) {
    setStatus(`完成 —— JEV 快 ${speedup.toFixed(1)} 倍`, 'done');
  } else {
    setStatus('完成（有一侧未成功返回）', 'error');
  }
}

/* ---------- 运行 ---------- */

function finish() {
  stopTicking();
  ui.run.disabled = false;
  if (source) {
    source.close();
    source = null;
  }
}

function start() {
  if (source) source.close();
  reset();
  ui.run.disabled = true;
  ui.run.textContent = '对比中…';
  setStatus('预热中，不计入耗时…', 'busy');

  source = new EventSource('/api/run');

  source.addEventListener('status', (event) => {
    setStatus(JSON.parse(event.data).message, 'busy');
  });

  source.addEventListener('start', (event) => {
    const data = JSON.parse(event.data);
    total = data.total;
    setStatus('计时中…', 'busy');
    startTicking();
  });

  source.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data);
    renderProgress(data.side, data);
  });

  source.addEventListener('side_done', (event) => {
    const data = JSON.parse(event.data);
    renderSideDone(data.side, data);
  });

  source.addEventListener('side_error', (event) => {
    const data = JSON.parse(event.data);
    frozen[data.side] = true;
    setStatus(`${data.side === 'jev' ? 'JEV' : 'DeepSeek'} 出错：${data.message}`, 'error');
  });

  source.addEventListener('done', (event) => {
    renderDone(JSON.parse(event.data));
    ui.run.textContent = '重新对比';
    finish();
  });

  source.onerror = () => {
    // 正常结束时我们已经主动 close 了，这里只在真的断线时兜底
    if (!source || source.readyState === EventSource.CLOSED) {
      finish();
      ui.run.textContent = '重新对比';
      if (!payload) setStatus('连接断开，请重试', 'error');
    }
  };
}

/* ---------- 复制结果 ---------- */

async function copyResult() {
  if (!payload) return;
  const text = JSON.stringify(payload, null, 2);
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const area = document.createElement('textarea');
    area.value = text;
    document.body.appendChild(area);
    area.select();
    document.execCommand('copy');
    area.remove();
  }
  ui.copy.textContent = '已复制';
  setTimeout(() => {
    ui.copy.textContent = '复制结果 JSON';
  }, 1500);
}

/* ---------- 初始化 ---------- */

ui.run.addEventListener('click', start);
ui.copy.addEventListener('click', copyResult);

fetch('/api/jobs')
  .then((response) => response.json())
  .then((jobs) => {
    total = jobs.length;
    for (const side of SIDES) {
      ui.sides[side].count.textContent = `0 / ${total} 岗位`;
    }
  })
  .catch(() => {});

// 录屏用：URL 后面加 ?autorun 会自动开跑，省得手点
if (new URLSearchParams(location.search).has('autorun')) {
  start();
}
