<!-- I1/I2 · Tuile produit : nom, prix, quantite (pastille si > 0). Émet « touche » (appui tuile) et « pastille » (retrait). Zéro métier. -->
<script>
  import { createEventDispatcher } from "svelte";
  export let nom; export let prix; export let quantite = 0;
  const dispatch = createEventDispatcher();
</script>
<button class="tuile-produit zone-tactile" aria-label={nom + ", " + prix} on:click={() => dispatch("touche", nom)}>
  <span>{nom}</span><span>{prix}</span>
  {#if quantite > 0}
    <span class="pastille zone-tactile" aria-label={quantite + " ajoutés"} on:click|stopPropagation={() => dispatch("pastille", nom)}>{quantite}</span>
  {/if}
</button>
