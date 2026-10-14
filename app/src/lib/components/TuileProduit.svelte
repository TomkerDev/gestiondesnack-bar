<!-- I1/I2 · Tuile produit : nom en gras, prix en secondaire SOUS le nom,
     pastille de quantité ronde en haut à droite, état sélectionné (bordure
     accent + fond accent 16 %). Un appui = « touche » ; la pastille émet « pastille »
     (retrait). Aucune couleur en dur. Zéro métier (STK-3 géré par le back). -->
<script>
  import { createEventDispatcher } from "svelte";
  export let nom = "";
  export let prix = "";
  export let quantite = 0;
  export let selectionne = false;
  export let indispo = false;      // affiché, jamais bloquant côté UI
  const dispatch = createEventDispatcher();
  $: aria = nom + ", " + prix + (quantite > 0 ? ", " + quantite + " dans la commande" : "")
            + (indispo ? ", rupture de stock" : "");
</script>

<button
  type="button"
  class="tuile zone-tactile"
  class:tuile--selectionne={selectionne}
  class:tuile--indispo={indispo}
  aria-pressed={selectionne}
  aria-label={aria}
  on:click={() => dispatch("touche", nom)}
>
  <span class="tuile-corps">
    <span class="tuile-nom">{nom}</span>
    <span class="tuile-prix montant">{prix}</span>
  </span>

  {#if quantite > 0}
    <!-- Pastille : cible tactile autonome, stopPropagation vers la tuile -->
    <span
      class="tuile-pastille zone-tactile"
      role="button"
      tabindex="0"
      aria-label={"Retirer un " + nom + " (" + quantite + " dans la commande)"}
      on:click|stopPropagation={() => dispatch("pastille", nom)}
      on:keydown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); dispatch("pastille", nom); } }}
    >{quantite}</span>
  {/if}
</button>

<style>
  .tuile {
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: var(--sp-2);
    width: 100%;
    min-height: var(--h-tuile);
    padding: var(--sp-3) var(--sp-4);
    background: var(--surface);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-carte);
    box-shadow: var(--ombre);
    text-align: left;
    transition: border-color var(--dur) var(--ease), background var(--dur) var(--ease),
                transform var(--dur) var(--ease);
  }
  .tuile:hover:not(.tuile--indispo) { border-color: var(--accent); }
  .tuile:active:not(.tuile--indispo) { transform: scale(var(--echelle-active)); }

  .tuile-corps { display: flex; flex-direction: column; gap: var(--sp-1); flex: 1; min-width: 0; }

  .tuile-nom {
    font-size: var(--t-base);
    font-weight: 700;
    line-height: 1.3;
  }

  .tuile-prix {
    font-size: var(--t-sm);
    color: var(--texte-secondaire);
  }

  /* sélection : bordure accent + fond accent à 16 % */
  .tuile--selectionne {
    border-color: var(--accent);
    background: var(--accent-doux);
  }
  .tuile--selectionne .tuile-prix { color: var(--texte); }

  /* indisponible : reste visible et lisible, jamais masqué (STK-3) */
  .tuile--indispo { opacity: 0.55; }
  .tuile--indispo .tuile-nom { text-decoration: line-through; }

  /* pastille de quantité : ronde, en haut à droite */
  .tuile-pastille {
    position: absolute;
    top: calc(var(--sp-2) * -0.5);
    right: calc(var(--sp-2) * -0.5);
    min-width: 32px;
    min-height: 32px;
    padding: 0 var(--sp-2);
    background: var(--accent);
    color: var(--sur-accent);
    border-radius: var(--rayon-pastille);
    font-size: var(--t-sm);
    font-weight: 700;
    box-shadow: 0 0 0 2px var(--surface);
  }
</style>

