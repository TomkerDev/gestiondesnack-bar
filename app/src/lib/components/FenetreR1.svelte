<!-- I1/I3 · Fenêtre R1 : PIN gérant + motif liste. Jeton 60 s / 1 usage vérifié en M6. -->
<script>
  import { createEventDispatcher } from "svelte";
  export let motifs = []; export let motif = ""; export let pin = "";
  export let titre = "Autorisation du gérant";
  const dispatch = createEventDispatcher();
</script>
<div class="zone-tactile" role="dialog" aria-label={titre}>
  <h2>{titre}</h2>
  <label>Motif<select class="zone-tactile" bind:value={motif}>{#each motifs as m}<option value={m}>{m}</option>{/each}</select></label>
  <label>Code gérant<input class="zone-tactile" type="password" inputmode="numeric" bind:value={pin} minlength="4" /></label>
  <p>Valable pour cet acte uniquement, 60 secondes</p>
  <button class="bouton-plein zone-tactile" disabled={pin.length < 4 || !motif} on:click={() => dispatch("valider", { motif, jeton: true })}>Valider</button>
</div>
