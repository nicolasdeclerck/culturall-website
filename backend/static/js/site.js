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

/**
 * Initialise chaque carrousel « galerie miniatures » (bloc Wagtail
 * « Carrousel », cf. templates/home/blocks/carousel_block.html).
 *
 * Reproduit l'exemple « Thumbs gallery » de SwiperJS : un carrousel principal
 * (.carousel-block__main) piloté par une bande de miniatures
 * (.carousel-block__thumbs) qui lui reste synchronisée. On boucle sur chaque
 * `.carousel-block` en ciblant ses sous-éléments par sélecteur relatif, afin
 * de supporter plusieurs carrousels sur une même page sans collision d'ID.
 */
if (window.Swiper) {
  document.querySelectorAll(".carousel-block").forEach((root) => {
    const mainEl = root.querySelector(".carousel-block__main");
    const thumbsEl = root.querySelector(".carousel-block__thumbs");
    if (!mainEl || !thumbsEl) return;

    const thumbs = new Swiper(thumbsEl, {
      spaceBetween: 10,
      slidesPerView: 4,
      freeMode: true,
      watchSlidesProgress: true,
    });

    new Swiper(mainEl, {
      spaceBetween: 10,
      navigation: {
        nextEl: mainEl.querySelector(".swiper-button-next"),
        prevEl: mainEl.querySelector(".swiper-button-prev"),
      },
      thumbs: { swiper: thumbs },
    });
  });
}

/**
 * Anime les « chiffres clés » (bloc Wagtail « Chiffres clés », cf.
 * templates/home/blocks/key_figures_block.html) avec CountUp.js : chaque
 * `[data-countup]` compte de 0 jusqu'à sa valeur (`data-value`), formatée à la
 * française (espace pour les milliers, virgule décimale) avec préfixe/suffixe
 * optionnels. L'animation se déclenche à l'entrée dans le viewport via un
 * IntersectionObserver. Si l'utilisateur préfère réduire les animations, la
 * valeur finale est affichée d'emblée, sans compteur.
 */
if (window.countUp && window.countUp.CountUp) {
  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  const makeCounter = (el) => {
    const raw = el.dataset.value || "0";
    const value = parseFloat(raw);
    if (Number.isNaN(value)) return null;
    const counter = new countUp.CountUp(el, value, {
      startVal: 0,
      // nombre de décimales déduit de la valeur saisie (ex. "98.5" → 1)
      decimalPlaces: (raw.split(".")[1] || "").length,
      duration: reduceMotion ? 0 : 2,
      separator: " ",
      decimal: ",",
      prefix: el.dataset.prefix || "",
      suffix: el.dataset.suffix || "",
    });
    return counter.error ? null : counter;
  };

  const els = document.querySelectorAll("[data-countup]");
  if (els.length) {
    // Sans animation : on fige la valeur finale immédiatement.
    if (reduceMotion) {
      els.forEach((el) => {
        const counter = makeCounter(el);
        if (counter) counter.start();
      });
    } else {
      const observer = new IntersectionObserver(
        (entries, obs) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const counter = makeCounter(entry.target);
            if (counter) counter.start();
            obs.unobserve(entry.target);
          });
        },
        // threshold 0 + rootMargin bas positif : on étend la zone de détection
        // ~200px sous le viewport, pour que le comptage soit déjà lancé au
        // moment où le bloc apparaît à l'écran (et non une fois remonté).
        { threshold: 0, rootMargin: "0px 0px 200px 0px" },
      );
      els.forEach((el) => observer.observe(el));
    }
  }
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
