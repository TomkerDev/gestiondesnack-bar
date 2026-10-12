<!-- Accueil : marque + aiguillage filtré par rôle (§3).
   Non connecté : hero + bouton « Prendre son poste » uniquement.
   Connecté : seuls les écrans du scope du rôle, via lib/droits.js. -->
<script>
  import Marque from "$lib/components/Marque.svelte";
  import { session } from "$lib/session.js";
  import { gardeRoute } from "$lib/droits.js";
  const ECRANS = [
    ["/commande", "Prise de commande", "Nouvelle commande (Awa, code 1234)"],
    ["/commandes", "Mes commandes", "Suivi + envoi cuisine"],
    ["/paiement", "Paiement", "Espèces, mobile, ardoise"],
    ["/cuisine", "Cuisine", "Bons + avancement"],
    ["/ma-caisse", "Ma caisse", "État + clôture"],
    ["/pc", "PC gérant", "Pilotage journée (gérant/proprio)"],
    ["/pc/stock", "Stock & prix", "Entrées, inventaire, prix (gérant/proprio)"],
    ["/galerie", "Galerie", "Composants tactiles"]
  ];
  let moi = { role: "" };
  session.subscribe((v) => (moi = v));
  $: visibles = ECRANS.filter(([href]) => href === "/galerie" || gardeRoute(moi.role, href).ok);
</script>
<header class="hero">
  <Marque taille={64} />
  <p class="slogan">Tiéboulé, braisé, servi — même sans réseau.</p>
  {#if !moi.role}
    <a class="bouton-plein demarrer" href="/connexion">Prendre son poste</a>
  {:else}
    <p class="connecte">Poste : <b>{moi.role}</b> — vos écrans ci-dessous.</p>
  {/if}
</header>
{#if moi.role}
  <h2>Mes écrans</h2>
  <nav class="grille" aria-label="Écrans autorisés">
    {#each visibles as [href, titre, desc]}
      <a class="carte zone-tactile" {href}><b>{titre}</b><span>{desc}</span></a>
    {/each}
  </nav>
{/if}
<style>
  .hero { display: flex; flex-direction: column; align-items: center; gap: 8px;
          padding: 24px 12px; background: var(--primaire-doux); border-radius: 0 0 16px 16px; }
  .slogan { margin: 0; color: var(--texte-doux); font-size: 18px; }
  .demarrer { background: var(--primaire); color: #fff; text-decoration: none;
              padding: 12px 28px; font-size: 18px; display: inline-block; }
  .connecte { margin: 0; font-size: 17px; }
  .grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; padding: 12px; }
  .carte { border: 1px solid var(--bordure, #ccc); border-radius: 10px; padding: 16px;
           display: flex; flex-direction: column; gap: 4px; text-decoration: none; color: inherit;
           min-height: 88px; }
  .carte span { font-size: 13px; opacity: .75; }
</style>
