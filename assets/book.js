(() => {
  'use strict';
  const sidebar = document.querySelector('.sidebar');
  const menu = document.querySelector('.menu-toggle');
  const scrim = document.querySelector('.mobile-scrim');
  function toggleMenu(open) {
    sidebar.classList.toggle('is-open', open);
    scrim.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
  }
  menu?.addEventListener('click', () => toggleMenu(!sidebar.classList.contains('is-open')));
  scrim?.addEventListener('click', () => toggleMenu(false));
  sidebar?.addEventListener('click', event => {
    if (event.target.closest('a[href]')) toggleMenu(false);
  });
  const active = sidebar?.querySelector('[aria-current="page"]');
  if (active) { for (let p = active.parentElement; p; p = p.parentElement) if (p.tagName === 'DETAILS') p.open = true; }
  const progress = document.querySelector('.reading-progress span');
  function updateProgress() {
    const max = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = `${max > 0 ? Math.min(100, scrollY / max * 100) : 100}%`;
  }
  addEventListener('scroll', updateProgress, {passive: true});
  addEventListener('resize', updateProgress);
  updateProgress();
  const headings = document.querySelectorAll('main h2[id], main h3[id]');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        document.querySelectorAll('.on-this-page a').forEach(a => a.classList.toggle('is-active', a.hash === '#' + entry.target.id));
      }
    }, {rootMargin: '-90px 0px -65% 0px'});
    headings.forEach(h => observer.observe(h));
  }
  document.querySelectorAll('.copy-code').forEach(button => button.addEventListener('click', async () => {
    const code = button.parentElement.querySelector('pre').textContent;
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(code);
      else {
        const area = document.createElement('textarea'); area.value = code;
        area.style.cssText = 'position:fixed;opacity:0'; document.body.append(area);
        area.select(); if (!document.execCommand('copy')) throw new Error('Copy unavailable'); area.remove();
      }
      button.textContent = 'Copied'; setTimeout(() => button.textContent = 'Copy', 1600);
    } catch { button.textContent = 'Select to copy'; }
  }));
  const dialog = document.querySelector('#search-dialog');
  const input = document.querySelector('#book-search');
  const results = document.querySelector('#search-results');
  const status = document.querySelector('#search-status');
  results.addEventListener('click', event => { if (event.target.closest('a')) dialog.close(); });
  let searchLoad;
  function loadSearch() {
    if (!searchLoad) searchLoad = new Promise((resolve, reject) => {
      const script = document.createElement('script'); script.src = 'assets/search-index.js';
      script.onload = resolve; script.onerror = reject; document.head.append(script);
    });
    return searchLoad;
  }
  async function openSearch() {
    dialog.showModal(); input.focus();
    try { await loadSearch(); search(); } catch { status.textContent = 'Search could not be loaded. Use the table of contents.'; }
  }
  document.querySelectorAll('[data-search]').forEach(button => button.addEventListener('click', openSearch));
  document.querySelector('[data-close-search]')?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
  addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); if (!dialog.open) openSearch(); }
    if (event.key === 'Escape') toggleMenu(false);
  });
  function search() {
    const query = input.value.trim().toLocaleLowerCase(); results.replaceChildren();
    if (query.length < 2) { status.textContent = 'Search chapters, definitions and examples.'; return; }
    if (!window.BOOK_SEARCH) return;
    const words = query.split(/\s+/);
    const matches = window.BOOK_SEARCH.map(item => {
      const text = (item.title + ' ' + item.text).toLocaleLowerCase();
      if (!words.every(word => text.includes(word))) return null;
      const title = item.title.toLocaleLowerCase();
      return {item, score: (title.includes(query) ? 100 : 0) + words.filter(word => title.includes(word)).length * 10};
    }).filter(Boolean).sort((a, b) => b.score - a.score);
    status.textContent = matches.length ? `${matches.length} matching sections${matches.length > 40 ? ' · showing the first 40' : ''}` : 'No matching sections.';
    for (const {item} of matches.slice(0, 40)) {
      const a = document.createElement('a'); a.href = item.url;
      const title = document.createElement('strong'); title.textContent = item.title;
      const p = document.createElement('p'); const lower = item.text.toLocaleLowerCase();
      const match = Math.max(0, lower.indexOf(query) >= 0 ? lower.indexOf(query) : lower.indexOf(words[0]));
      const start = Math.max(0, match - 65);
      p.textContent = (start ? '…' : '') + item.text.slice(start, start + 210) + (item.text.length > start + 210 ? '…' : '');
      a.append(title, p); results.append(a);
    }
  }
  let timer;
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(search, 120); });
})();
