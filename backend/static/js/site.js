/**
 * Socle JS du site rendu côté serveur.
 *
 * Enregistre le composant Alpine « header » (référencé par `x-data="header"`
 * dans templates/_header.html). Reproduit, sans dépendance React, les deux
 * comportements du Header.tsx Next.js :
 *   1. Classe "header--scrolled" appliquée quand window.scrollY > 50.
 *   2. Menu mobile : ouverture/fermeture, verrouillage du scroll du body,
 *      fermeture sur Escape ou au clic sur un lien de navigation.
 *
 * Chargé avant alpine.min.js (cf. base.html) pour que l'écouteur
 * `alpine:init` soit enregistré avant le démarrage d'Alpine.
 */

const SCROLL_THRESHOLD = 50;

/**
 * Initialise AOS (Animate On Scroll) : les éléments portant un attribut
 * `data-aos` (ex. data-aos="fade-right") s'animent à leur entrée dans le
 * viewport. L'animation ne se joue qu'une fois (`once: true`) et est
 * désactivée si l'utilisateur préfère réduire les animations.
 */
if (window.AOS) {
  AOS.init({
    once: true,
    duration: 700,
    easing: "ease-out-cubic",
    disable: () =>
      window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  });
}

document.addEventListener("alpine:init", () => {
  Alpine.data("header", () => ({
    scrolled: false,
    menuOpen: false,

    init() {
      this.onScroll();
    },
    onScroll() {
      this.scrolled = window.scrollY > SCROLL_THRESHOLD;
    },
    open() {
      this.menuOpen = true;
      document.body.style.overflow = "hidden";
    },
    close() {
      this.menuOpen = false;
      document.body.style.overflow = "";
    },
    toggle() {
      this.menuOpen ? this.close() : this.open();
    },
  }));
});
