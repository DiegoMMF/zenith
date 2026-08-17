(function () {
  const STORAGE_PREFIX = 'docs-html-check-';

  document.querySelectorAll('.tab-list').forEach((list) => {
    const panels = list.parentElement.querySelectorAll('.tab-panel');
    list.querySelectorAll('.tab-btn').forEach((btn, i) => {
      btn.addEventListener('click', () => {
        list.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
        panels.forEach((p) => p.classList.remove('active'));
        btn.classList.add('active');
        panels[i]?.classList.add('active');
      });
    });
  });

  document.querySelectorAll('.checklist[data-persist]').forEach((list) => {
    const key = STORAGE_PREFIX + list.dataset.persist;
    let saved = {};
    try {
      saved = JSON.parse(localStorage.getItem(key) || '{}');
    } catch (_) {}

    const inputs = list.querySelectorAll('input[type="checkbox"]');
    inputs.forEach((input, i) => {
      const id = input.id || `item-${i}`;
      input.id = id;
      if (saved[id]) {
        input.checked = true;
        input.closest('label')?.classList.add('done');
      }
      input.addEventListener('change', () => {
        input.closest('label')?.classList.toggle('done', input.checked);
        saved[id] = input.checked;
        localStorage.setItem(key, JSON.stringify(saved));
        updateProgress(list);
      });
    });
    updateProgress(list);
  });

  function updateProgress(list) {
    const bar = list.parentElement.querySelector('.progress-bar span');
    if (!bar) return;
    const inputs = list.querySelectorAll('input[type="checkbox"]');
    const done = [...inputs].filter((i) => i.checked).length;
    const pct = inputs.length ? Math.round((done / inputs.length) * 100) : 0;
    bar.style.width = pct + '%';
    const label = list.parentElement.querySelector('[data-progress-label]');
    if (label) label.textContent = `${done}/${inputs.length} (${pct}%)`;
  }

  const sections = document.querySelectorAll('.section[id], .hero[id]');
  const navLinks = document.querySelectorAll('.sidebar nav a[href^="#"]');
  if (sections.length && navLinks.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            navLinks.forEach((a) => {
              a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
            });
          }
        });
      },
      { rootMargin: '-20% 0px -70% 0px' }
    );
    sections.forEach((s) => observer.observe(s));
  }

  // Copy buttons on <pre>
  document.querySelectorAll('main pre').forEach((pre) => {
    if (pre.classList.contains('mermaid')) return;
    if (pre.closest('.pre-wrap')) return;
    const wrap = document.createElement('div');
    wrap.className = 'pre-wrap';
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-btn';
    btn.textContent = 'Copiar';
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(pre.textContent || '');
        btn.textContent = 'Copiado';
        setTimeout(() => {
          btn.textContent = 'Copiar';
        }, 1500);
      } catch (_) {
        btn.textContent = 'Error';
        setTimeout(() => {
          btn.textContent = 'Copiar';
        }, 1500);
      }
    });
    wrap.appendChild(btn);
  });

  // Mermaid diagrams (lazy CDN)
  const mermaidNodes = document.querySelectorAll('pre.mermaid, .mermaid');
  if (mermaidNodes.length) {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';
    s.onload = () => {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
      });
      window.mermaid.run({ nodes: mermaidNodes });
    };
    document.head.appendChild(s);
  }
})();
