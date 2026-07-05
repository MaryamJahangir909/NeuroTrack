document.addEventListener('DOMContentLoaded', function () {
  loadHome();
});

function loadHome() {
  fetch(API_URL + '/api/dashboard')
    .then((r) => r.json())
    .then((data) => {
      if (!data.success) return;

      // Live stats
      setText('total-scans', data.stats.total_scans);
      setText('total-patients', data.stats.total_patients);
      setText('tumor-detected', data.stats.tumor_detected);
      setText('no-tumor', data.stats.no_tumor);

      // Recent scans (use same api/dashboard response)
      const container = document.getElementById('recent-scans');
      container.innerHTML = '';

      const scans = data.recent_scans || [];
      if (scans.length === 0) {
        container.innerHTML = '<div class="recent-item muted">No scans yet.</div>';
        return;
      }

      scans.slice(0, 4).forEach((s) => {
        const isTumor = s.predicted_class !== 'notumor';
        const pillClass = isTumor ? 'pill pill-danger' : 'pill pill-safe';
        const pillText = isTumor ? 'Tumor' : 'Clear';

        const div = document.createElement('div');
        div.className = 'recent-item';
        div.innerHTML = `
          <div class="recent-left">
            <div class="recent-title">${escapeHtml(s.patient_name)} • Scan #${s.id}</div>
            <div class="recent-sub">${escapeHtml(s.predicted_class.toUpperCase())} • ${s.confidence_score}% • ${escapeHtml(s.scan_date)}</div>
          </div>
          <div class="${pillClass}">${pillText}</div>
        `;
        container.appendChild(div);
      });
    })
    .catch(() => {
      const container = document.getElementById('recent-scans');
      if (container) container.innerHTML = '<div class="recent-item muted">Unable to load recent scans.</div>';
    });
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function escapeHtml(str) {
  return String(str || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}