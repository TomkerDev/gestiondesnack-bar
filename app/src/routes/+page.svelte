<!-- Accueil démo : marque + aiguillage tactile vers les écrans. -->
<script>
  import Marque from "$lib/components/Marque.svelte";
  const ECRANS = [
    ["/commande", "Prise de commande", "Nouvelle commande (Awa, code 1234)"],
    ["/commandes", "Mes commandes", "Suivi + envoi cuisine"],
    ["/paiement", "Paiement", "Espèces, mobile, ardoise"],
    ["/cuisine", "Cuisine", "Bons + avancement"],
    ["/ma-caisse", "Ma caisse", "État + clôture"],
    ["/pc", "PC gérant", "Pilotage journée"],
    ["/pc/stock", "Stock & prix", "Entrées, inventaire, prix"],
    ["/galerie", "Galerie", "Composants tactiles"]
  ];
</script>
<header class="hero">
  <Marque taille={64} />
  <p class="slogan">Tiéboulé, braisé, servi — même sans réseau.</p>
  <a class="bouton-plein demarrer" href="/connexion">Prendre son poste</a>
</header>
<h2>Écrans</h2>
<nav class="grille" aria-label="Écrans">
  {#each ECRANS as [href, titre, desc]}
    <a class="carte zone-tactile" {href}><b>{titre}</b><span>{desc}</span></a>
  {/each}
</nav>
<style>
  .hero { display: flex; flex-direction: column; align-items: center; gap: 8px;
          padding: 24px 12px; background: var(--primaire-doux); border-radius: 0 0 16px 16px; }
  .slogan { margin: 0; color: var(--texte-doux); font-size: 18px; }
  .demarrer { background: var(--primaire); color: #fff; text-decoration: none;
              padding: 12px 28px; font-size: 18px; display: inline-block; }
  .grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; padding: 12px; }
  .carte { border: 1px solid var(--bordure, #ccc); border-radius: 10px; padding: 16px;
           display: flex; flex-direction: column; gap: 4px; text-decoration: none; color: inherit;
           min-height: 88px; }
  .carte span { font-size: 13px; opacity: .75; }
</style>
