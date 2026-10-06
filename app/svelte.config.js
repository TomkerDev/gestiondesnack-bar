import adapter from "@sveltejs/adapter-static";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // PWA installable : SPA avec fallback (le PC caisse sert l'app),
    // chemins relatifs possibles pour usage hors ligne.
    adapter: adapter({ fallback: "index.html" })
  }
};

export default config;
