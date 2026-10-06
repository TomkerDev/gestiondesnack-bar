<!-- I-INT · Layout global : thème, bandeau de connexion (OFF-1, piloté par session
   + événements navigateur online/offline), navigation tactile principale.
   Hors ligne → le client bascule et se resynchronise au retour du réseau (OFF-3). -->
<script>
  import "$lib/theme.css";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import { session, majConnexion } from "$lib/session.js";
  import { api } from "$lib/api.js";
  let enLigne = true;
  async function basculer(v) {
    enLigne = v;
    api.basculerLigne(v);
    majConnexion(v);
    if (v) await api.resynchroniser();
  }
  if (typeof window !== "undefined") {
    basculer(navigator.onLine);
    window.addEventListener("online", () => basculer(true));
    window.addEventListener("offline", () => basculer(false));
  }
  const LIENS = [
    ["/commande", "Prise de commande"], ["/commandes", "Mes commandes"],
    ["/cuisine", "Cuisine"], ["/paiement", "Paiement"],
    ["/ma-caisse", "Ma caisse"], ["/pc", "PC caisse"], ["/pc/stock", "Stock & prix"],
    ["/galerie", "Galerie"]
  ];
</script>
<svelte:head><meta name="theme-color" content="#1a1a2e" /></svelte:head>
<header class="layout-entete">
  <nav aria-label="Application">{#each LIENS as [href, lib]}<a class="zone-tactile" {href}>{lib}</a>{/each}</nav>
  <BandeauConnexion {enLigne} />
</header>
<main><slot /></main>
<style>
  .layout-entete { display: flex; justify-content: space-between; align-items: center; gap: 12px;
                   padding: 8px 12px; border-bottom: 1px solid var(--bordure, #ccc); flex-wrap: wrap; }
  nav { display: flex; gap: 4px; flex-wrap: wrap; }
  nav a { min-height: 48px; min-width: 48px; display: inline-flex; align-items: center;
          padding: 0 12px; border: 1px solid var(--bordure, #ccc); border-radius: 6px;
          text-decoration: none; color: inherit; font-size: 14px; }
</style>
