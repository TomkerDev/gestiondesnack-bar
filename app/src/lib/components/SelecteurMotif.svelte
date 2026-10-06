<!-- I1 · Sélecteur motif : liste paramétrable, « Autre » exige commentaire (§7). -->
<script>export let motifs = []; export let motif = ""; export let commentaire = "";</script>
<label>Motif<select class="zone-tactile" bind:value={motif}>{#each motifs as m}<option value={m}>{m}</option>{/each}</select></label>
{#if motif === "Autre"}<label>Préciser<input class="zone-tactile" bind:value={commentaire} required /></label>{/if}
