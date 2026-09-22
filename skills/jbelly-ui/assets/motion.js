/* jbelly-ui identity module. No dependencies. Optional: a page without it is
   correct, just not animated on re-sort and re-filter.
   Contract: an object that can appear in more than one place or order carries
   data-vt-key, whose value is a STABLE domain id — never a loop index, never a
   row number, because a position-derived key cannot survive the one change it
   exists to survive. */
window.JBMotion = (function () {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const css = n => getComputedStyle(root).getPropertyValue(n).trim();
  const ms = (n, d) => { const v = css(n);
    return v.endsWith('ms') ? parseFloat(v) : v.endsWith('s') ? parseFloat(v) * 1000 : d; };
  const CAP = 24, MARGIN = 200;          // snapshot layers are not free
  const held = new Set(); let running = null, busy = false;

  function release() { for (const el of held) el.style.viewTransitionName = ''; held.clear(); }
  addEventListener('pageshow', e => { if (e.persisted) release(); });  // bfcache restores stale names

  /* Lease names only to RENDERED members near the action, capped. A duplicate
     name rejects ViewTransition.ready and silently skips the whole transition,
     so first claim wins and there is never a second. */
  function lease(scope, anchor) {
    release();
    const seen = new Set(), vh = innerHeight, out = [];
    for (const el of scope.querySelectorAll('[data-vt-key]')) {
      const r = el.getBoundingClientRect();
      if (!r.width || r.bottom < -MARGIN || r.top > vh + MARGIN) continue;
      out.push([el, r.top + r.height / 2]);
    }
    if (anchor) {
      const a = anchor.getBoundingClientRect(), mid = a.top + a.height / 2;
      out.sort((p, q) => Math.abs(p[1] - mid) - Math.abs(q[1] - mid));
    }
    for (const [el] of out.slice(0, CAP)) {
      const name = 'vt-' + el.dataset.vtKey.replace(/[^A-Za-z0-9_-]/g, '-');
      if (seen.has(name)) continue;
      seen.add(name); held.add(el); el.style.viewTransitionName = name;
    }
  }

  /* reorder(): the nodes may be replaced, so the engine derives the motion from
     the real geometry delta. An element that did not move produces no motion,
     because there is nothing to interpolate. */
  function reorder(scope, mutate, o = {}) {
    if (busy) return Promise.resolve();
    if (!document.startViewTransition || document.visibilityState === 'hidden') {
      mutate(); return Promise.resolve();
    }
    busy = true;
    if (running) running.skipTransition();
    lease(scope, o.anchor);
    const t = running = document.startViewTransition({
      update: () => { mutate(); lease(scope, o.anchor); },
      types: o.types || [],
    });
    return t.finished.catch(() => {}).finally(() => { release(); running = null; busy = false; });
  }

  /* reflow(): the nodes survive, so two measurements are enough — and unlike a
     view transition the page stays fully interactive. Preferred for anything
     the user repeats. */
  function reflow(scope, mutate, o = {}) {
    if (reduce.matches) { mutate(); return Promise.resolve(); }
    const first = new Map();
    for (const el of scope.querySelectorAll('[data-vt-key]')) {
      const r = el.getBoundingClientRect();
      if (r.width) first.set(el.dataset.vtKey, r);
    }
    mutate();                                 // layout is final immediately after
    const duration = ms('--t-move', 260), easing = css('--spring-ui') || 'ease-out';
    const done = [];
    for (const el of scope.querySelectorAll('[data-vt-key]')) {
      const a = first.get(el.dataset.vtKey); if (!a) continue;
      for (const x of el.getAnimations()) if (x.id === 'jb-flip') x.cancel();
      const b = el.getBoundingClientRect(); if (!b.width) continue;
      const dx = a.left - b.left, dy = a.top - b.top;
      if (!dx && !dy) continue;               // <- did not change, so does not move
      // dx is REAL SCREEN COORDINATES and is already correct in RTL. Multiplying
      // it by --flow-x here is the double-mirror bug; M07 fails it.
      const an = el.animate(
        [{ translate: dx + 'px ' + dy + 'px' }, { translate: '0px 0px' }],
        { duration, easing, fill: 'none' });  // fill:'none': a forwards fill would
      an.id = 'jb-flip'; done.push(an.finished.catch(() => {}));   // override styles forever
    }
    return Promise.all(done);
  }

  /* leave(): the departure report. The only timer in the system, and it waits
     on the animation rather than guessing at it. */
  function leave(el) {
    el.dataset.leaving = '';
    return Promise.allSettled(el.getAnimations().map(a => a.finished))
      .then(() => el.remove());
  }

  addEventListener('load', () => root.setAttribute('data-ready', ''));
  return { reorder, reflow, leave };
})();
