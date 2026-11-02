(() => {
  const V = window.VF, $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;

  // заголовок: буквы вылетают по одной
  const h1 = $('.hero h1');
  if (h1 && !calm) {
    let i = 0;
    h1.innerHTML = h1.textContent.split(/[  ]+/).map(w =>
      '<span class="w">' + [...w].map(c => `<span class="c" style="--i:${i++}">${c}</span>`).join('') + '</span>').join(' ');
  }

  // лепестки: падают, кружатся, разлетаются от курсора
  const cv = $('#petals');
  if (cv && !calm) {
    const ctx = cv.getContext('2d'), dpr = Math.min(devicePixelRatio || 1, 2);
    const cols = ['#ffb3c7', '#ff7aa2', '#ffd6e2', '#ffc38f', '#fff0f4'];
    let W, H, P = [], mx = -999, my = -999;
    const size = () => { W = cv.width = innerWidth * dpr; H = cv.height = innerHeight * dpr; };
    const make = top => ({ x: Math.random() * W, y: top ? -20 * dpr : Math.random() * H, r: (5 + Math.random() * 8) * dpr,
      vy: (.4 + Math.random() * .9) * dpr, vx: (Math.random() - .5) * .6 * dpr, a: Math.random() * 6.3, va: (Math.random() - .5) * .04,
      sw: Math.random() * 6.3, c: cols[Math.random() * cols.length | 0], o: .55 + Math.random() * .4 });
    size(); addEventListener('resize', size);
    const N = innerWidth < 760 ? 22 : 45;
    for (let i = 0; i < N; i++) P.push(make(false));
    addEventListener('pointermove', e => { mx = e.clientX * dpr; my = e.clientY * dpr; }, { passive: true });
    const tick = () => {
      ctx.clearRect(0, 0, W, H);
      for (const p of P) {
        p.sw += .02; p.a += p.va;
        const dx = p.x - mx, dy = p.y - my, d2 = dx * dx + dy * dy, R = 120 * dpr;
        if (d2 < R * R) { const f = (1 - Math.sqrt(d2) / R) * 2.2; p.vx += dx / R * f; p.vy += dy / R * f * .5; }
        p.vx *= .97; p.vy += (.6 * dpr - p.vy) * .02;
        p.x += p.vx + Math.sin(p.sw) * .6 * dpr; p.y += p.vy;
        if (p.y > H + 30 || p.x < -40 || p.x > W + 40) Object.assign(p, make(true));
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a); ctx.scale(1, .55 + Math.sin(p.sw * 2) * .35);
        ctx.globalAlpha = p.o; ctx.fillStyle = p.c;
        ctx.beginPath(); ctx.moveTo(0, -p.r);
        ctx.bezierCurveTo(p.r, -p.r * .6, p.r * .7, p.r * .8, 0, p.r);
        ctx.bezierCurveTo(-p.r * .7, p.r * .8, -p.r, -p.r * .6, 0, -p.r); ctx.fill(); ctx.restore();
      }
      if (!document.hidden) requestAnimationFrame(tick); else setTimeout(() => requestAnimationFrame(tick), 500);
    };
    requestAnimationFrame(tick);
  }

  // шапка, нижняя панель, параллакс видео
  const top = $('.top'), bar = $('.bar'), bg = $('.bg video');
  let ticking = false;
  const onScroll = () => {
    const y = scrollY;
    top.classList.toggle('s', y > 40);
    bar.classList.toggle('on', y > innerHeight * .6);
    if (bg && !calm) bg.style.setProperty('--py', (y * -.08).toFixed(1) + 'px');
    ticking = false;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  // появление блоков при прокрутке, с лесенкой внутри группы
  if ('IntersectionObserver' in window && !calm) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    const group = (sel, step) => $$(sel).forEach((el, i) => { el.classList.add('rv'); el.style.setProperty('--d', (i % 6) * step + 'ms'); io.observe(el); });
    group('.panel > h2, .panel > .sub, .chips, .zones, #of, .rel, .panel > details', 60);
    group('.card', 70); group('.steps li', 120); group('.adv li', 90);
  }

  // наклон карточки за курсором
  if (fine && !calm) $$('.card').forEach(c => {
    c.addEventListener('pointermove', e => {
      const b = c.getBoundingClientRect(), x = (e.clientX - b.left) / b.width - .5, y = (e.clientY - b.top) / b.height - .5;
      c.style.setProperty('--ry', (x * 10).toFixed(2) + 'deg'); c.style.setProperty('--rx', (y * -10).toFixed(2) + 'deg');
    });
    c.addEventListener('pointerleave', () => { c.style.setProperty('--ry', '0deg'); c.style.setProperty('--rx', '0deg'); });
  });

  // фильтр категорий с анимацией
  $$('.chip').forEach(ch => ch.addEventListener('click', () => {
    $$('.chip').forEach(x => x.classList.toggle('on', x === ch));
    let k = 0;
    $$('.card').forEach(c => {
      const show = ch.dataset.f === 'all' || c.dataset.cat === ch.dataset.f;
      c.classList.toggle('hide', !show); c.classList.remove('pop', 'rv');
      if (show) { c.style.setProperty('--k', k++); void c.offsetWidth; c.classList.add('pop'); }
    });
  }));

  // форма заказа → готовое сообщение в WhatsApp / Telegram
  const sel = $('#o-item'), date = $('#o-date');
  if (date) { const d = new Date(); date.value = new Date(d - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10); }
  $$('.pick').forEach(b => b.addEventListener('click', () => {
    if (sel) sel.value = b.dataset.item;
    $('#order').scrollIntoView({ behavior: calm ? 'auto' : 'smooth' });
    const o = $('#order'); o.classList.remove('flash'); void o.offsetWidth; o.classList.add('flash');
  }));
  const msg = () => {
    const t = V.t, v = id => ($('#o-' + id) || {}).value?.trim() || '';
    const lines = [t.m_hello];
    if (sel && sel.value) lines.push(t.m_item + t.items[sel.value]);
    const when = [v('date'), v('time')].filter(Boolean).join(' ');
    if (when) lines.push(t.m_date + when);
    if (v('addr')) lines.push(t.m_addr + v('addr'));
    if (v('to')) lines.push(t.m_to + v('to'));
    if (v('card')) lines.push(t.m_card + v('card'));
    if (v('from')) lines.push(t.m_from + v('from'));
    return lines.join('\n');
  };
  // копия заявки уходит в бот владельцу — даже если клиент не дожмёт «Отправить» в мессенджере
  const lead = via => {
    const v = id => ($('#o-' + id) || {}).value?.trim() || '';
    if (!V.lead || v('hp')) return Promise.resolve(false);
    const body = { item: sel && sel.value ? V.t.items[sel.value] : '', when: [v('date'), v('time')].filter(Boolean).join(' '),
      addr: v('addr'), to: v('to'), card: v('card'), name: v('from'), phone: v('phone'), via, lang: V.lang };
    return fetch(V.lead, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), keepalive: true })
      .then(r => r.ok).catch(() => false);
  };
  const hint = (txt, ok) => { const h = $('#o-hint'); if (h) { h.textContent = txt; h.hidden = false; h.style.color = ok === false ? '#ffb3b3' : ''; } };
  $('#o-wa')?.addEventListener('click', () => { lead('whatsapp'); window.open('https://wa.me/' + V.wa + '?text=' + encodeURIComponent(msg()), '_blank'); });
  $('#o-tg')?.addEventListener('click', () => {
    const m = msg(); lead('telegram');
    navigator.clipboard?.writeText(m).catch(() => {});
    window.open('https://t.me/' + V.tg + '?text=' + encodeURIComponent(m), '_blank');
    hint(V.t.f_hint);
  });
  $('#o-lead')?.addEventListener('click', async e => {
    const ph = $('#o-phone');
    if (!ph.value.trim()) { hint(V.t.f_need, false); ph.focus(); return; }
    const b = e.currentTarget; b.disabled = true;
    const ok = await lead('form');
    b.disabled = false;
    hint(ok ? V.t.f_ok : V.t.f_err, ok);
    if (ok) b.classList.add('sent');
  });

  // мышка на hero: стрелка «листай»
  const hero = $('.hero:not(.small)');
  if (hero) { hero.style.position = 'relative'; hero.insertAdjacentHTML('beforeend', '<span class="scroll" aria-hidden="true"></span>'); }
})();
