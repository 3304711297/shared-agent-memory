(() => {
  // Companion probe for snapshot.js: map every element in window.__jevFast.nodes
  // to a CSS selector that resolves back to EXACTLY that node, so callers that
  // accept CSS (e.g. `bsk click --selector`) can act on the numbered table.
  //
  // Read-only; run AFTER snapshot.js.
  const c = window.__jevFast;
  if (!c) return null;

  const esc = s => (window.CSS && CSS.escape) ? CSS.escape(s) : s.replace(/[^a-zA-Z0-9_-]/g, ch => '\\' + ch);
  const hitsOf = sel => { try { return document.querySelectorAll(sel); } catch (e) { return null; } };

  // Accept a candidate ONLY when it resolves to exactly this node.
  // Uniqueness alone is insufficient: a structurally derived selector can be
  // unique yet point at a different element (measured 25/81 wrong on a GitHub page).
  const good = (sel, node) => {
    const hits = hitsOf(sel);
    return hits && hits.length === 1 && hits[0] === node;
  };

  const pathFor = e => {
    if (e.id) {
      const sel = '#' + esc(e.id);
      if (good(sel, e)) return sel;
    }
    const attrs = ['data-testid', 'data-test', 'name', 'aria-label', 'href'];
    for (let i = 0; i < attrs.length; i++) {
      const a = attrs[i];
      const v = e.getAttribute && e.getAttribute(a);
      if (!v || v.length > 120) continue;
      const sel = e.tagName.toLowerCase() + '[' + a + '="' + v.replace(/"/g, '\\"') + '"]';
      if (good(sel, e)) return sel;
    }
    // Structural: build the full path to a body child, then shorten only while
    // identity still holds.
    const parts = [];
    let n = e;
    while (n && n.nodeType === 1 && n.parentElement && n.tagName.toLowerCase() !== 'body') {
      let part = n.tagName.toLowerCase();
      const parent = n.parentElement;
      const sibs = Array.prototype.filter.call(parent.children, x => x.tagName === n.tagName);
      if (sibs.length > 1) part += ':nth-of-type(' + (sibs.indexOf(n) + 1) + ')';
      parts.unshift(part);
      n = parent;
    }
    for (let cut = 0; cut < parts.length; cut++) {
      const sel = 'body > ' + parts.slice(cut).join(' > ');
      if (good(sel, e)) return sel;
    }
    return null;
  };

  const map = {};
  let matched = 0, stale = 0;
  const unmatched = [];
  for (const entry of c.nodes) {
    const id = entry[0], node = entry[1];
    if (!node || !node.isConnected) { stale++; continue; }
    const sel = pathFor(node);
    if (sel) { map[id] = sel; matched++; }
    else unmatched.push(id);
  }
  return { map: map, cached: c.nodes.size, matched: matched, stale: stale, unmatched: unmatched };
})()
