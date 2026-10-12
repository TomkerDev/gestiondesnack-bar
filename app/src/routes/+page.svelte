<!-- Accueil démo : aiguillage tactile vers les écrans. -->
<script>
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
<h1>Snack-bar — Démo</h1>
<p>Codes : Awa <b>1234</b> (serveur) · Ibrahim <b>9111</b> (gérant) · Hassane <b>9999</b> (proprio).</p>
<nav class="grille" aria-label="Écrans">
  {#each ECRANS as [href, titre, desc]}
    <a class="carte zone-tactile" {href}><b>{titre}</b><span>{desc}</span></a>
  {/each}
</nav>
<style>
  .grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; padding: 12px; }
  .carte { border: 1px solid var(--bordure, #ccc); border-radius: 10px; padding: 16px;
           display: flex; flex-direction: column; gap: 4px; text-decoration: none; color: inherit;
           min-height: 88px; }
  .carte span { font-size: 13px; opacity: .75; }
</style>
