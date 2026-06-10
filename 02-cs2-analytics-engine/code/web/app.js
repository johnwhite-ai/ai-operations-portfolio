async function sendCmd(cmd) {
  const last = document.getElementById('last');
  last.textContent = 'Last: ' + cmd + ' ...';
  try {
    const res = await fetch('/exec', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cmd })
    });
    if (res.ok) {
      last.textContent = 'Last: ' + cmd + ' OK';
    } else {
      const err = await res.text();
      last.textContent = 'Last: ' + cmd + ' FAIL (' + res.status + '): ' + err;
    }
  } catch (e) {
    last.textContent = 'Last: ' + cmd + ' ERROR: ' + e.message;
  }
}

function showPresetInfo(desc) {
  document.getElementById('preset-info').textContent = desc;
}

async function checkHealth() {
  const status = document.getElementById('status');
  try {
    const res = await fetch('/health');
    const data = await res.json();
    status.textContent = 'CS2: ' + (data.cs2_running ? 'running' : 'NOT running');
    status.className = data.cs2_running ? 'ok' : 'bad';
  } catch {
    status.textContent = 'Daemon unreachable';
    status.className = 'bad';
  }
}

document.querySelectorAll('button[data-cmd]').forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn.dataset.desc) {
      showPresetInfo(btn.dataset.desc);
    }
    sendCmd(btn.dataset.cmd);
  });
});

document.getElementById('redeploy').addEventListener('click', async () => {
  const last = document.getElementById('last');
  last.textContent = 'Redeploying...';
  try {
    const res = await fetch('/redeploy', { method: 'POST' });
    const data = await res.json();
    last.textContent = data.error
      ? 'Redeploy FAILED: ' + data.error
      : 'Redeployed: ' + data.deployed.join(', ');
  } catch (e) {
    last.textContent = 'Redeploy ERROR: ' + e.message;
  }
});

function renderRec(s) {
  return s
    .replace(/^- /, "")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

let drillCatalog = [];

async function loadDrills() {
  const target = document.getElementById("refrag-drills-list");
  try {
    const res = await fetch("/refrag_drills.json");
    if (!res.ok) {
      target.innerHTML = "<em>No drill catalog yet.</em>";
      return;
    }
    const data = await res.json();
    drillCatalog = data.drills || [];
    if (drillCatalog.length === 0) {
      target.innerHTML =
        '<em>No Refrag drills configured. Add them in <code>web/refrag_drills.json</code>.</em>';
      return;
    }
    target.innerHTML = drillCatalog
      .map(
        (d) => `
        <a class="refrag-drill" href="${d.url}" target="_blank" rel="noopener">
          <div class="refrag-drill-title">${d.title}</div>
          <div class="refrag-drill-summary">${d.weakness_summary || ""}</div>
          <div class="refrag-drill-tags">${(d.tags || [])
            .map((t) => `<span class="refrag-tag">${t}</span>`)
            .join("")}</div>
        </a>`
      )
      .join("");
  } catch (e) {
    target.innerHTML = "Failed to load drills: " + e.message;
  }
}

function matchDrillToRec(recText) {
  const lower = recText.toLowerCase();
  for (const drill of drillCatalog) {
    for (const kw of drill.matches_keywords || []) {
      if (lower.includes(kw.toLowerCase())) {
        return drill;
      }
    }
  }
  return null;
}

async function loadReport() {
  const target = document.getElementById("drill-info");
  try {
    const res = await fetch("/report");
    if (!res.ok) {
      target.innerHTML =
        '<em>No weekly report yet. Run <code>python -m analyzer.run_report</code> to generate one.</em>';
      return;
    }
    const data = await res.json();
    const top = data.recommendations[0] || "No recommendations.";
    const m = data.top_metrics;
    // Match each rec to a Refrag drill if available
    const matchedDrill = matchDrillToRec(top);
    const drillButton = matchedDrill
      ? `<a class="practice-cta" href="${matchedDrill.url}" target="_blank" rel="noopener">▶ Practice in Refrag: ${matchedDrill.title}</a>`
      : "";
    target.innerHTML = `
      <div class="drill-meta">${data.generated_at} · ${data.demos_analyzed} demos · ${data.rounds} rounds</div>
      <div class="drill-quick-stats">
        K/D <strong>${m.kd}</strong> ·
        HS% <strong>${m.hs_pct}%</strong> ·
        T <strong>${m.t_kd}</strong> /
        CT <strong>${m.ct_kd}</strong> ·
        Clutch <strong>${m.clutch_win_rate}%</strong>
      </div>
      <div class="drill-top-rec">
        <div class="drill-label">Top recommendation</div>
        <div class="drill-body">${renderRec(top)}</div>
        ${drillButton}
      </div>
      <details>
        <summary>All ${data.recommendations.length} recommendations</summary>
        <ul>
          ${data.recommendations
            .map((r) => {
              const md = matchDrillToRec(r);
              const link = md
                ? ` <a class="inline-drill" href="${md.url}" target="_blank" rel="noopener">▶ ${md.title}</a>`
                : "";
              return `<li>${renderRec(r)}${link}</li>`;
            })
            .join("")}
        </ul>
      </details>
    `;
  } catch (e) {
    target.innerHTML = "Failed to load report: " + e.message;
  }
}

checkHealth();
setInterval(checkHealth, 3000);
(async () => {
  await loadDrills();
  await loadReport();
})();
