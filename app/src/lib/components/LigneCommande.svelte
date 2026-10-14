<!-- I1 · Ligne de commande : produit, quantité, prix figé, net.
     Les actions sont portées par le parent (pas de bouton ici). -->
<script>
  export let nom = "";
  export let quantite = 0;
  export let prix = "";
  export let net = "";
  export let statutCuisine = "";
</script>

<li class="ligne zone-tactile">
  <span class="ligne-nom">{nom}</span>
  <span class="ligne-qte montant" aria-label={quantite + " fois"}>× {quantite}</span>
  <span class="ligne-prix montant texte-secondaire">{prix}</span>
  <strong class="ligne-net montant">{net}</strong>
  {#if statutCuisine}<span class="ligne-statut">{statutCuisine}</span>{/if}
</li>

<style>
  .ligne {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    min-height: var(--tactile);
    padding: var(--sp-2) var(--sp-3);
    background: var(--surface);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-carte);
  }

  .ligne-nom {
    flex: 1;
    min-width: 0;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .ligne-qte {
    min-width: 3ch;
    text-align: center;
    color: var(--texte-secondaire);
  }

  .ligne-prix { min-width: 6ch; text-align: right; }

  .ligne-net {
    min-width: 7ch;
    text-align: right;
    font-size: var(--t-md);
  }

  .ligne-statut {
    font-size: var(--t-xs);
    color: var(--texte-secondaire);
    padding-left: var(--sp-2);
    border-left: var(--bordure-large) solid var(--bordure);
  }
</style>

