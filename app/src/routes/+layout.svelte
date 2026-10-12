<!-- I-INT · Layout global : thème, bandeau de connexion (OFF-1, piloté par session
   + événements navigateur online/offline), navigation tactile principale.
   Hors ligne → le client bascule et se resynchronise au retour du réseau (OFF-3).
   Scopes §3 (module lib/droits.js) : /commande /commandes /cuisine /paiement
   /ma-caisse (serveur+) ; /pc /pc/stock (gérant/proprio seuls, R3). -->
<script>
  import "$lib/theme.css";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import Marque from "$lib/components/Marque.svelte";
  import { session, majConnexion, fermerSession, ouvrirSession } from "$lib/session.js";
  import { gardeRoute, liensPour } from "$lib/droits.js";
  import { api } from "$lib/api.js";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  let enLigne = true;
  let moi = { identifiant: "", role: "", appareil: "", debut: "", enLigne: true };
  session.subscribe((v) => (moi = v));
  $: liens = [...liensPour(moi.role), ["/galerie", "Galerie"]];
  // Garde de routes : sans session → /connexion ; rôle insuffisant → /connexion.
  $: if (typeof window !== "undefined" && $page.url) {
    const chemin = $page.url.pathname;
    if (chemin !== "/connexion" && chemin !== "/") {
      const g = gardeRoute(moi.role, chemin);
      if (!g.ok) goto("/connexion");
    }
  }
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
    try { // restaure l'acteur après rechargement (profil persisté à la connexion)
      const p = JSON.parse(sessionStorage.getItem("snack.profil") || "null");
      if (p?.id) { api.definirActeur(p.id); ouvrirSession({ identifiant: "0000", role: p.role, appareil: "appareil-demo" }); }
    } catch { /* stockage indisponible : on reste anonyme */ }
  }
</script>
<svelte:head><meta name="theme-color" content="#c2410c" /></svelte:head>
<header class="layout-entete">
  <a class="logo" href="/" aria-label="Accueil Snack-bar Apis"><Marque taille={32} /></a>
  <nav aria-label="Application">{#each liens as [href, lib]}<a class="zone-tactile" {href}>{lib}</a>{/each}</nav>
  <span class="qui">
    {#if moi.identifiant}
      {moi.role} · <button type="button" class="quitter" on:click={async () => { fermerSession(); api.definirActeur(null); sessionStorage.removeItem("snack.profil"); await goto("/connexion"); }}>Quitter</button>
    {:else}
      <a class="zone-tactile connecter" href="/connexion">Se connecter</a>
    {/if}
  </span>
  <BandeauConnexion {enLigne} />
</header>
<main><slot /></main>
<style>
  .layout-entete { display: flex; justify-content: space-between; align-items: center; gap: 12px;
                   padding: 8px 12px; border-bottom: 3px solid var(--primaire); flex-wrap: wrap;
                   background: var(--fond-carte); }
  .logo { text-decoration: none; color: inherit; }
  nav { display: flex; gap: 4px; flex-wrap: wrap; }
  nav a { min-height: 48px; min-width: 48px; display: inline-flex; align-items: center;
          padding: 0 12px; border: 1px solid var(--bordure, #ccc); border-radius: 6px;
          text-decoration: none; color: inherit; font-size: 14px; }
  .qui { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; }
  .quitter, .connecter { border: 1px solid var(--primaire); border-radius: 6px; padding: 8px 12px;
          background: var(--primaire); color: #fff; text-decoration: none; }
  .quitter { cursor: pointer; }
</style>
