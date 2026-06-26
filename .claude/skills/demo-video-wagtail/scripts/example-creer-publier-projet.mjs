import { chromium } from 'playwright';

const OUT_DIR = process.argv[2] || '.';
const BASE = 'http://localhost:8000';
const CULTURALL_ID = 3; // HomePage "Cultur'all" (child of Root)
const PARENT_ID = 7; // ProjectsIndexPage "Nos réalisations" (child of "Cultur'all")
const NEW_TITLE = 'Festival Cultur\'all 2026';
const YOUTUBE = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';

// Injected on every document (survives navigation): animated cursor, click ripple, caption box.
const initScript = () => {
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
    window.__pwIntro = (title, lines) => {
      const back = document.createElement('div');
      back.id = '__pw_intro';
      back.style.cssText =
        'position:fixed;inset:0;z-index:2147483647;pointer-events:none;' +
        'background:rgba(10,10,14,.78);display:flex;align-items:center;justify-content:center;' +
        'opacity:0;transition:opacity .4s ease;';
      const items = lines.map((l) =>
        `<li style="margin:8px 0;padding-left:6px;">${l}</li>`).join('');
      back.innerHTML =
        '<div style="max-width:680px;background:#fff;border-radius:16px;padding:34px 40px;' +
        'box-shadow:0 20px 60px rgba(0,0,0,.45);border-top:6px solid #ff7a00;' +
        'font:400 18px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#15151a;">' +
        `<div style="font-size:26px;font-weight:800;margin-bottom:6px;">${title}</div>` +
        '<div style="color:#ff7a00;font-weight:700;letter-spacing:.5px;font-size:13px;margin-bottom:16px;">TUTORIEL — ADMINISTRATION WAGTAIL</div>' +
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

const sleep = (p, ms) => p.waitForTimeout(ms);

// Smoothly scroll the window by `total` px over several steps (visible in the video).
async function smoothScroll(page, total, steps = 24) {
  const per = total / steps;
  for (let i = 0; i < steps; i++) {
    await page.evaluate((d) => window.scrollBy(0, d), per);
    await page.waitForTimeout(40);
  }
}

async function glide(page, from, to, steps = 28) {
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    const x = from.x + (to.x - from.x) * ease;
    const y = from.y + (to.y - from.y) * ease;
    await page.mouse.move(x, y);
    await page.evaluate(([x, y]) => window.__pwMoveCursor && window.__pwMoveCursor(x, y), [x, y]);
    await page.waitForTimeout(16);
  }
}

const state = { pos: { x: 90, y: 90 } };

async function moveToEl(page, locator) {
  await locator.scrollIntoViewIfNeeded().catch(() => {});
  const box = await locator.boundingBox();
  if (!box) throw new Error('element not found / no bounding box');
  const target = { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  await glide(page, state.pos, target);
  state.pos = target;
  return target;
}

async function clickEl(page, locator) {
  const t = await moveToEl(page, locator);
  await sleep(page, 250);
  await page.evaluate(([x, y]) => window.__pwClickFx(x, y), [t.x, t.y]);
  await sleep(page, 180);
  await locator.click();
}

async function caption(page, text, step) {
  await page.evaluate(([t, s]) => window.__pwCaption && window.__pwCaption(t, s), [text, step || '']);
}

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1366, height: 850 },
    recordVideo: { dir: OUT_DIR, size: { width: 1366, height: 850 } },
  });
  await context.addInitScript(initScript);
  const page = await context.newPage();

  // ---- 0. Intro card -------------------------------------------------------
  await page.goto(`${BASE}/admin/login/`, { waitUntil: 'load' });
  await page.evaluate(([x, y]) => window.__pwMoveCursor && window.__pwMoveCursor(x, y), [state.pos.x, state.pos.y]);
  await page.evaluate(([title, lines]) => window.__pwIntro(title, lines), [
    'Créer et publier une page « Projet »',
    [
      'Se connecter à l\'administration Wagtail',
      'Naviguer dans l\'arbre jusqu\'à <b>« Nos réalisations »</b>',
      'Ajouter une page enfant de type <b>« Projet »</b>',
      'Renseigner le titre et le lien YouTube',
      'Publier la page',
    ],
  ]);
  await sleep(page, 6500);
  await page.evaluate(() => window.__pwIntroHide());
  await sleep(page, 600);

  // ---- 1. Login ------------------------------------------------------------
  await caption(page, 'Saisissez votre identifiant et votre mot de passe, puis validez', 'Étape 1');
  await sleep(page, 1200);

  const user = page.locator('#id_username');
  await clickEl(page, user);
  await user.type('admin', { delay: 110 });
  await sleep(page, 400);

  const pass = page.locator('#id_password');
  await clickEl(page, pass);
  await pass.type('admin', { delay: 110 });
  await sleep(page, 500);

  await caption(page, 'Cliquez sur « Se connecter »', 'Étape 1');
  await clickEl(page, page.locator('button[type="submit"]').first());
  await page.waitForLoadState('load');
  await sleep(page, 1500);

  // ---- 2. Navigate the page tree: Cultur'all → Nos réalisations ------------
  await page.goto(`${BASE}/admin/pages/${CULTURALL_ID}/`, { waitUntil: 'load' });
  await caption(page, 'Arborescence : page racine « Cultur\'all » et ses enfants', 'Étape 2');
  await page.evaluate(([x, y]) => window.__pwMoveCursor && window.__pwMoveCursor(x, y), [state.pos.x, state.pos.y]);
  await sleep(page, 2200);

  await caption(page, 'Cliquez sur « Nos réalisations » pour ouvrir la page', 'Étape 2');
  const intoRealisations = page.locator(`a[href="/admin/pages/${PARENT_ID}/"]`).first();
  await clickEl(page, intoRealisations);
  await page.waitForLoadState('load');
  await caption(page, 'Page « Nos réalisations » (enfant de « Cultur\'all »)', 'Étape 2');
  await sleep(page, 1800);

  // ---- 3. Add child page ---------------------------------------------------
  await caption(page, 'Cliquez sur le « + » pour ajouter une page enfant', 'Étape 3');
  const addBtn = page.locator(`a[href="/admin/pages/${PARENT_ID}/add_subpage/"]`).first();
  await clickEl(page, addBtn);
  await page.waitForLoadState('load');
  await sleep(page, 1200);

  // Wagtail may show a page-type chooser if several child types are allowed.
  const projetChoice = page.getByRole('link', { name: /^Projet$/i }).first();
  if (await projetChoice.isVisible().catch(() => false)) {
    await caption(page, 'Sélectionnez le type de page « Projet »', 'Étape 3');
    await clickEl(page, projetChoice);
    await page.waitForLoadState('load');
    await sleep(page, 1000);
  }

  // ---- 4. Fill the form ----------------------------------------------------
  await caption(page, 'Renseignez le titre du projet', 'Étape 4');
  const title = page.locator('#id_title');
  await clickEl(page, title);
  await title.type(NEW_TITLE, { delay: 70 });
  await sleep(page, 600);

  await caption(page, 'Faites défiler pour parcourir les champs du formulaire', 'Étape 4');
  await sleep(page, 500);
  await smoothScroll(page, 360);
  await sleep(page, 900);

  await caption(page, 'Renseignez le lien YouTube (champ obligatoire)', 'Étape 4');
  const yt = page.locator('#id_youtube_url');
  await clickEl(page, yt);
  await yt.type(YOUTUBE, { delay: 45 });
  await sleep(page, 800);

  await caption(page, 'Descendez jusqu\'au bas du formulaire', 'Étape 4');
  await sleep(page, 400);
  await smoothScroll(page, 600);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await sleep(page, 1000);

  // ---- 5. Publish ----------------------------------------------------------
  await caption(page, 'Ouvrez le menu « Plus d\'actions »', 'Étape 5');
  let publishBtn = page.locator('button[name="action-publish"]').first();
  if (!(await publishBtn.isVisible().catch(() => false))) {
    // "Publier" lives inside the "Plus d'actions" dropdown — reveal it first
    const toggle = page.getByRole('button', { name: /Plus d'actions|More actions/i }).first();
    await clickEl(page, toggle);
    await sleep(page, 700);
  }
  await caption(page, 'Cliquez sur « Publier »', 'Étape 5');
  await clickEl(page, publishBtn);
  await page.waitForLoadState('load');
  await sleep(page, 1500);

  await caption(page, '✓ Page « ' + NEW_TITLE + ' » publiée sous « Nos réalisations »', 'Terminé');
  await page.evaluate(([x, y]) => window.__pwMoveCursor && window.__pwMoveCursor(x, y), [state.pos.x, state.pos.y]);
  await sleep(page, 2600);

  console.log('Final URL:', page.url());
  await context.close();
  await browser.close();
  const vpath = await (await page.video()).path();
  console.log('VIDEO_PATH=' + vpath);
})().catch((e) => { console.error('ERROR:', e.message); console.error(e.stack); process.exit(1); });
