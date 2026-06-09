/**
 * POC HTMX — interactions client minimales pour les pages rendues
 * côté serveur (cf. docs/poc-htmx-a-propos.md).
 *
 * Reproduit deux comportements du Header.tsx Next.js :
 *  1. Classe "header--scrolled" appliquée quand window.scrollY > 50.
 *  2. Toggle du menu mobile (data-menu-toggle) avec verrouillage du
 *     scroll body et fermeture sur Escape.
 *
 * ~30 lignes vs 110 lignes pour le composant Header.tsx (qui inclut
 * aussi la récupération de l'auth et du logo, faits côté serveur ici).
 */

const SCROLL_THRESHOLD = 50;

document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("[data-scroll-aware]");
  if (header) {
    const onScroll = () => {
      header.classList.toggle("header--scrolled", window.scrollY > SCROLL_THRESHOLD);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  if (toggle && menu) {
    const close = () => {
      menu.classList.remove("header-nav--open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Ouvrir le menu");
      toggle.querySelector("span").textContent = "☰";
      document.body.style.overflow = "";
    };
    const open = () => {
      menu.classList.add("header-nav--open");
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "Fermer le menu");
      toggle.querySelector("span").textContent = "✕";
      document.body.style.overflow = "hidden";
    };
    toggle.addEventListener("click", () => {
      menu.classList.contains("header-nav--open") ? close() : open();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
    menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
  }
});
