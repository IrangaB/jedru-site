// Jedru marketing site — small vanilla JS: nav, video modal, pricing toggle, reveal.
(function () {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  document.documentElement.classList.add('js');
  const rv = $$('.reveal'); if (rv.length && 'IntersectionObserver' in window) { const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' }); rv.forEach(el => io.observe(el)); setTimeout(() => rv.forEach(el => el.classList.add('in')), 2500); } else rv.forEach(el => el.classList.add('in'));
  // mobile nav
  const mb = $('.menu-btn'); if (mb) mb.addEventListener('click', () => { const n = $('.topnav nav'); n.classList.toggle('open'); mb.setAttribute('aria-expanded', n.classList.contains('open')); });
  // video modal
  const modal = $('#video-modal'); const mv = modal && $('video', modal);
  const openVideo = (src) => { if (!modal) return; mv.src = src; modal.classList.add('open'); mv.play().catch(() => {
  document.documentElement.classList.add('js');
  const rv = $$('.reveal'); if (rv.length && 'IntersectionObserver' in window) { const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' }); rv.forEach(el => io.observe(el)); setTimeout(() => rv.forEach(el => el.classList.add('in')), 2500); } else rv.forEach(el => el.classList.add('in'));}); };
  const closeVideo = () => { if (!modal) return; modal.classList.remove('open'); mv.pause(); mv.removeAttribute('src'); mv.load(); };
  $$('[data-video]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); openVideo(b.dataset.video); }));
  if (modal) { $('.close', modal).addEventListener('click', closeVideo); modal.addEventListener('click', e => { if (e.target === modal) closeVideo(); }); document.addEventListener('keydown', e => { if (e.key === 'Escape') closeVideo(); }); }
  // hover-to-play previews on product cards
  $$('.product .vid video, .hero-media video').forEach(v => { v.muted = true; });
  $$('.product .vid').forEach(box => { const v = $('video', box); if (!v) return; box.addEventListener('mouseenter', () => v.play().catch(() => {})); box.addEventListener('mouseleave', () => { v.pause(); }); });
  // pricing: product tabs + monthly/annual with savings
  let per = 'y';
  const fmt = v => '$' + Number(v).toLocaleString('en-US');
  const price = () => { $$('.plan .price').forEach(el => { const m = +el.dataset.monthly, a = +el.dataset.annual, save = +el.dataset.save, pct = el.dataset.pct, unit = el.dataset.unit;
      if (per === 'y') { $('.amt', el).textContent = fmt(a); $('small', el).textContent = unit + ' / year'; $('.sub', el).textContent = save > 0 ? `≈ ${fmt(Math.round(a / 12))}/month · save ${fmt(save)} a year (${pct}%)` : ''; }
      else { $('.amt', el).textContent = fmt(m); $('small', el).textContent = unit + ' / month'; $('.sub', el).textContent = save > 0 ? `or ${fmt(a)}/year and save ${fmt(save)}` : ''; } }); };
  $$('#per button').forEach(b => b.addEventListener('click', () => { per = b.dataset.per; $$('#per button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); price(); }));
  $$('#ptabs button').forEach(b => b.addEventListener('click', () => { $$('#ptabs button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); $$('.tierset').forEach(t => t.hidden = t.id !== 'tiers-' + b.dataset.product); }));
  if ($('#per')) { price(); const h = location.hash.replace('#', ''); const tab = $$('#ptabs button').find(b => h.startsWith(b.dataset.product)); if (tab) tab.click(); }
  // quote page: ?product=vortex preselects the checkbox; ?trial=1 preselects "free trial" (used while the portal is not live)
  const qs = new URLSearchParams(location.search);
  if (qs.get('trial') === '1') { const r = $('input[name=intent][value="Free trial request"]'); if (r) r.checked = true; }
  const qp = qs.get('product');
  if (qp) { const map = { vortex: 'Vortex', imonitor: 'iMonitor', craftstudio: 'Craft Studio' }; const cb = $$('input[name=products]').find(c => c.value === map[qp]); if (cb) cb.checked = true; }
  // contact / quote form -> POST /api/contact (Cloudflare Pages Function -> Resend -> support@jedru.com)
  const cf = $('#contact-form');
  const showErr = (el, msg) => { el.setAttribute('aria-invalid', 'true'); let m = el.closest('.field, fieldset')?.querySelector('.ferr'); if (!m) { m = document.createElement('small'); m.className = 'ferr'; el.closest('.field, fieldset')?.appendChild(m); } m.textContent = msg; };
  const clearErr = el => { el.removeAttribute('aria-invalid'); el.closest('.field, fieldset')?.querySelector('.ferr')?.remove(); };
  const digits = v => (v.match(/\d/g) || []).length;
  const validate = form => {
    let first = null;
    $$('input, textarea, select', form).forEach(el => { if (el.name !== 'website') clearErr(el); });
    $$('input, textarea', form).forEach(el => {
      if (el.type === 'checkbox' || el.type === 'hidden' || el.name === 'website') return;
      el.value = el.value.trim();
      let bad = !el.checkValidity();
      if (!bad && el.type === 'tel' && el.value && (digits(el.value) < 7 || digits(el.value) > 15)) bad = true;
      if (bad) { showErr(el, el.dataset.msg || 'Please check this field.'); first = first || el; }
    });
    const boxes = $$('input[name=products]', form);
    if (boxes.length && !boxes.some(b => b.checked)) { showErr(boxes[0], 'Please tick at least one product.'); first = first || boxes[0]; }
    if (first) { first.focus(); first.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
    return !first;
  };
  if (cf) { $$('input, textarea', cf).forEach(el => el.addEventListener('input', () => clearErr(el))); $$('input[name=products]', cf).forEach(b => b.addEventListener('change', () => clearErr(b))); }
  if (cf) cf.addEventListener('submit', async e => {
    e.preventDefault(); const btn = $('button[type=submit]', cf), done = $('#contact-done'), err = $('#contact-error');
    done.hidden = true; err.hidden = true;
    if (!validate(cf)) return;
    const label = btn.dataset.label || (btn.dataset.label = btn.textContent);
    btn.disabled = true; btn.textContent = 'Sending…';
    const fd = new FormData(cf), d = Object.fromEntries(fd.entries());
    const prods = fd.getAll('products'); if (prods.length) d.products = prods.join(', ');
    d.kind = d.intent || cf.dataset.kind || 'Enquiry'; delete d.intent;
    // Fallback when the API is unavailable (Function not deployed / network down): open the visitor's email app with everything filled in.
    const mailto = () => { const lines = Object.entries(d).filter(([k]) => k !== 'website').map(([k, v]) => `${k}: ${v}`).join('\n');
      location.href = 'mailto:support@jedru.com?subject=' + encodeURIComponent(`[Jedru] ${d.kind || 'Enquiry'} — ${d.name || ''}`) + '&body=' + encodeURIComponent(lines);
      err.textContent = 'Our form service is temporarily unavailable, so we opened your email app with your message ready to send to support@jedru.com.'; err.hidden = false; };
    try { const r = await fetch('/api/contact', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(d) });
      const isJson = (r.headers.get('content-type') || '').includes('application/json'); const j = isJson ? await r.json().catch(() => ({})) : null;
      if (r.ok && j && j.ok) { cf.reset(); done.hidden = false; done.scrollIntoView({ block: 'center', behavior: 'smooth' }); }
      else if (!j || r.status === 404 || r.status === 405) mailto();
      else { err.textContent = j.error || 'Could not send. Please email support@jedru.com.'; err.hidden = false; }
    } catch { mailto(); }
    btn.disabled = false; btn.textContent = label;
  });

})();
