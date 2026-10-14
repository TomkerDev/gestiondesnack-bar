<!-- I-INT · Layout global : thème (sombre par défaut, jetons + base importés
   UNE FOIS ici), bandeau de connexion (OFF-1, piloté par session + événements
   navigateur online/offline), navigation tactile par rôle.
   Hors ligne → le client bascule et se resynchronise au retour du réseau (OFF-3).
   Scopes §3 (module lib/droits.js) : /commande /commandes /cuisine /paiement
   /ma-caisse (serveur+) ; /pc /pc/stock (gérant/proprio seuls, R3). -->
<script>
  import "$lib/theme.css";
  import "$lib/base.css";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import Marque from "$lib/components/Marque.svelte";
  import Navigation from "$lib/components/Navigation.svelte";
  import { session, majConnexion, fermerSession, ouvrirSession } from "$lib/session.js";
  import { gardeRoute, liensPour } from "$lib/droits.js";
  import { api } from "$lib/api.js";
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { dev } from "$app/environment";
  let enLigne = true;
  let moi = { identifiant: "", role: "", appareil: "", debut: "", enLigne: true };
  session.subscribe((v) => (moi = v));
  // Galerie : réservée au mode développement (jamais en production).
  $: liens = [...liensPour(moi.role), ...(dev ? [["/galerie", "Galerie"]] : [])];
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
    } catch { /* stockage local absent : on reste anonyme */ }
  }
</script>
<div class="app">
  <header class="entete">
    <a class="entete-logo" href="/" aria-label="Accueil Snack-bar Apis"><Marque taille={32} /></a>
    <Navigation {liens} chemin={$page.url.pathname} />
    <span class="entete-qui">
      {#if moi.identifiant}
        <span class="entete-role">{moi.role}</span>
        <button type="button" class="entete-quitter zone-tactile" on:click={async () => { fermerSession(); api.definirActeur(null); sessionStorage.removeItem("snack.profil"); await goto("/connexion"); }}>Quitter</button>
      {:else}
        <a class="entete-connecter zone-tactile" href="/connexion">Se connecter</a>
      {/if}
    </span>
  </header>

  <BandeauConnexion {enLigne} />

  <main class="contenu"><slot /></main>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .entete {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-2) var(--sp-3);
    background: var(--surface);
    border-bottom: var(--bordure-large) solid var(--bordure);
    flex-wrap: wrap;
  }

  .entete-logo {
    text-decoration: none;
    color: inherit;
    flex: none;
  }

  .entete-qui {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
    margin-left: auto;
    font-size: var(--t-sm);
  }

  .entete-role {
    color: var(--texte-secondaire);
    text-transform: capitalize;
  }

  .entete-quitter,
  .entete-connecter {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: var(--tactile);
    padding: 0 var(--sp-3);
    border-radius: var(--rayon-bouton);
    border: var(--bordure-large) solid var(--accent);
    background: var(--accent);
    color: var(--sur-accent);
    font-size: var(--t-sm);
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
  }

  .contenu {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--sp-4);
    padding: var(--sp-4);
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
  }
</style>
