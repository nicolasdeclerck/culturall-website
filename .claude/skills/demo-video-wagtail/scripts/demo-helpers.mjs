// Reusable helpers for recording Wagtail admin demo videos with Playwright.
//
//   import { chromium } from 'playwright';
//   import { initScript, makeDemo } from './demo-helpers.mjs';
//
//   const browser = await chromium.launch();
//   const context = await browser.newContext({
//     viewport: { width: 1366, height: 850 },
//     recordVideo: { dir: process.argv[2] || '.', size: { width: 1366, height: 850 } },
//   });
//   await context.addInitScript(initScript);   // <-- MUST be before newPage()
//   const page = await context.newPage();
//   const d = makeDemo(page);                   // d.glide / d.clickEl / d.caption / d.intro / d.scroll ...
//
// All overlays (cursor, caption, intro) are re-injected on every navigation because
// initScript is registered with addInitScript — so call them again after each page load.

// Injected into every document. Defines window.__pw* overlay helpers.
export const initScript = () => {
  const install = () => {
    if (!document.body) return;
    if (!document.getElementById('__pw_cursor')) {
      const c = document.createElement('div');
      c.id = '__pw_cursor';
      c.style.cssText =
        'position:fixed;left:0;top:0;width:22px;height:22px;z-index:2147483647;' +
        'pointer-events:none;transform:translate(-100px,-100px);will-change:transform;' +
        'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));';
      c.innerHTML =
        '<svg width="22" height="22" viewBox="0 0 22 22" xmlns="http://www.w3.org/2000/svg">' +
        '<path d="M2 2 L2 17 L6.5 13 L9.5 19.5 L12 18.3 L9 12 L15 12 Z" ' +
        'fill="#fff" stroke="#000" stroke-width="1.3" stroke-linejoin="round"/></svg>';
      document.body.appendChild(c);
    }
    window.__pwMoveCursor = (x, y) => {
      const c = document.getElementById('__pw_cursor');
      if (c) c.style.transform = `translate(${x}px,${y}px)`;
    };
    window.__pwClickFx = (x, y) => {
      const r = document.createElement('div');
      r.style.cssText =
        `position:fixed;left:${x}px;top:${y}px;width:14px;height:14px;z-index:2147483646;` +
        'pointer-events:none;border:2px solid #ff7a00;border-radius:50%;' +
        'transform:translate(-50%,-50%) scale(0.2);opacity:1;' +
        'transition:transform .45s ease-out,opacity .45s ease-out;';
      document.body.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'translate(-50%,-50%) scale(3)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 500);
    };
    window.__pwCaption = (text, step) => {
      let box = document.getElementById('__pw_caption');
      if (!box) {
        box = document.createElement('div');
        box.id = '__pw_caption';
        box.style.cssText =
          'position:fixed;top:18px;left:50%;transform:translateX(-50%);z-index:2147483647;' +
          'pointer-events:none;max-width:78%;padding:12px 20px;border-radius:10px;' +
          'background:rgba(17,17,20,.92);color:#fff;font:600 17px/1.35 -apple-system,Segoe UI,Roboto,sans-serif;' +
          'box-shadow:0 6px 24px rgba(0,0,0,.35);border-left:4px solid #ff7a00;text-align:center;';
        document.body.appendChild(box);
      }
      const badge = step ? `<span style="display:inline-block;background:#ff7a00;color:#fff;border-radius:6px;padding:1px 9px;margin-right:10px;font-weight:700;">${step}</span>` : '';
      box.innerHTML = badge + `<span>${text}</span>`;
    };
    window.__pwIntro = (title, lines, subtitle) => {
      const back = document.createElement('div');
      back.id = '__pw_intro';
      back.style.cssText =
        'position:fixed;inset:0;z-index:2147483647;pointer-events:none;' +
        'background:rgba(10,10,14,.78);display:flex;align-items:center;justify-content:center;' +
        'opacity:0;transition:opacity .4s ease;';
      const items = lines.map((l) => `<li style="margin:8px 0;padding-left:6px;">${l}</li>`).join('');
      back.innerHTML =
        '<div style="max-width:680px;background:#fff;border-radius:16px;padding:34px 40px;' +
        'box-shadow:0 20px 60px rgba(0,0,0,.45);border-top:6px solid #ff7a00;' +
        'font:400 18px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#15151a;">' +
        `<div style="font-size:26px;font-weight:800;margin-bottom:6px;">${title}</div>` +
        `<div style="color:#ff7a00;font-weight:700;letter-spacing:.5px;font-size:13px;margin-bottom:16px;">${subtitle || 'TUTORIEL'}</div>` +
        `<ol style="margin:0;padding-left:22px;">${items}</ol></div>`;
      document.body.appendChild(back);
      requestAnimationFrame(() => { back.style.opacity = '1'; });
    };
    window.__pwIntroHide = () => {
      const b = document.getElementById('__pw_intro');
      if (b) { b.style.opacity = '0'; setTimeout(() => b.remove(), 400); }
    };
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
};

// Returns helpers bound to a page, sharing a single cursor position.
export function makeDemo(page, startPos = { x: 90, y: 90 }) {
  const state = { pos: { ...startPos } };
  const sleep = (ms) => page.waitForTimeout(ms);

  async function syncCursor() {
    await page.evaluate(([x, y]) => window.__pwMoveCursor && window.__pwMoveCursor(x, y), [state.pos.x, state.pos.y]);
  }
  async function glide(to, steps = 28) {
    const from = state.pos;
    for (let i = 1; i <= steps; i++) {
      const t = i / steps;
      const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      const x = from.x + (to.x - from.x) * ease;
      const y = from.y + (to.y - from.y) * ease;
      await page.mouse.move(x, y);
      await page.evaluate(([x, y]) => window.__pwMoveCursor && window.__pwMoveCursor(x, y), [x, y]);
      await page.waitForTimeout(16);
    }
    state.pos = { ...to };
  }
  async function moveToEl(locator) {
    await locator.scrollIntoViewIfNeeded().catch(() => {});
    const box = await locator.boundingBox();
    if (!box) throw new Error('element not found / no bounding box');
    const target = { x: box.x + box.width / 2, y: box.y + box.height / 2 };
    await glide(target);
    return target;
  }
  async function clickEl(locator) {
    const t = await moveToEl(locator);
    await sleep(250);
    await page.evaluate(([x, y]) => window.__pwClickFx(x, y), [t.x, t.y]);
    await sleep(180);
    await locator.click();
  }
  async function caption(text, step) {
    await page.evaluate(([t, s]) => window.__pwCaption && window.__pwCaption(t, s), [text, step || '']);
  }
  async function intro(title, lines, { subtitle, holdMs = 6500 } = {}) {
    await page.evaluate(([t, l, s]) => window.__pwIntro(t, l, s), [title, lines, subtitle]);
    await sleep(holdMs);
    await page.evaluate(() => window.__pwIntroHide());
    await sleep(600);
  }
  // The Wagtail admin scrolls inside <main id="main">, NOT the window — scroll that.
  async function smoothScroll(total, steps = 24) {
    const per = total / steps;
    for (let i = 0; i < steps; i++) {
      await page.evaluate((d) => {
        const s = document.querySelector('#main') || document.scrollingElement;
        s.scrollTop += d;
      }, per);
      await page.waitForTimeout(45);
    }
  }
  async function scrollToBottom() {
    await page.evaluate(() => {
      const s = document.querySelector('#main') || document.scrollingElement;
      s.scrollTop = s.scrollHeight;
    });
  }
  async function typeInto(locator, text, delay = 80) {
    await clickEl(locator);
    await locator.type(text, { delay });
  }

  return { state, sleep, syncCursor, glide, moveToEl, clickEl, caption, intro, smoothScroll, scrollToBottom, typeInto };
}
