<!-- I1 · Champ de formulaire : libellé AU-DESSUS, saisie 48 px, message
     d'erreur SOUS le champ. Types texte / nombre / mot de passe.
     Aucune couleur en dur : jetons uniquement. Zéro métier. -->
<script>
  export let libelle = "";
  export let valeur = "";
  export let type = "text";            // "text" | "number" | "password"
  export let erreur = "";
  export let aide = "";
  export let placeholder = "";
  export let requis = false;
  export let min = undefined;
  export let step = undefined;
  export let name = "";
  export let inputmode = undefined;
  export let autocomplete = undefined;
  const id = name || libelle.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  $: describedBy = erreur ? id + "-erreur" : aide ? id + "-aide" : undefined;
</script>

<div class="champ">
  <label class="champ-libelle" for={id}>
    {libelle}{#if requis}<span aria-hidden="true"> *</span>{/if}
  </label>

  <input
    {id}
    class="champ-saisie zone-tactile"
    class:champ-saisie--erreur={!!erreur}
    {type}
    bind:value={valeur}
    {placeholder}
    {min}
    {step}
    {inputmode}
    {autocomplete}
    required={requis || undefined}
    aria-required={requis || undefined}
    aria-invalid={erreur ? "true" : undefined}
    aria-describedby={describedBy}
  />

  {#if aide && !erreur}<span class="champ-aide" id={id + "-aide"}>{aide}</span>{/if}
  {#if erreur}<span class="champ-erreur" id={id + "-erreur"} role="alert">{erreur}</span>{/if}
</div>

<style>
  .champ-aide {
    font-size: var(--t-sm);
    color: var(--texte-secondaire);
  }
  .champ-saisie--erreur {
    border-color: var(--danger);
  }
</style>
