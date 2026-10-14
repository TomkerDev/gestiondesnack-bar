<!-- I1 · Sélecteur de motif : liste paramétrable, libellé au-dessus du champ.
     « Autre » exige un commentaire (§7) : le champ apparaît et porte required. -->
<script>
  export let motifs = [];
  export let motif = "";
  export let commentaire = "";
  export let libelle = "Motif";
  export let erreur = "";
  export let requis = false;
</script>

<div class="champ">
  <label class="champ-libelle" for="motif">{libelle}{#if requis}<span aria-hidden="true"> *</span>{/if}</label>
  <select id="motif" class="champ-saisie zone-tactile" bind:value={motif} aria-required={requis || undefined}
          aria-invalid={erreur ? "true" : undefined}>
    <option value="" disabled>Choisir un motif…</option>
    {#each motifs as m}<option value={m}>{m}</option>{/each}
  </select>
  {#if erreur}<p class="champ-erreur" role="alert">{erreur}</p>{/if}
</div>

{#if motif === "Autre"}
  <div class="champ champ-commentaire">
    <label class="champ-libelle" for="motif-commentaire">Préciser<span aria-hidden="true"> *</span></label>
    <input id="motif-commentaire" class="champ-saisie zone-tactile" bind:value={commentaire} required />
  </div>
{/if}

<style>
  .champ-commentaire { margin-top: var(--sp-2); }
</style>

