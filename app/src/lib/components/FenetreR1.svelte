<!-- I1/I3 · Fenêtre d'autorisation gérant (R1) : PIN + motif.
     Feuille montante sur téléphone, fenêtre centrée sur écran large.
     Jeton 60 s / 1 usage vérifié en M6. Zéro métier. -->
<script>
  import { createEventDispatcher } from "svelte";
  import Bouton from "./Bouton.svelte";
  export let motifs = [];
  export let motif = "";
  export let pin = "";
  export let titre = "Autorisation du gérant";
  export let erreur = "";
  const dispatch = createEventDispatcher();
  $: pret = pin.length >= 4 && motif !== "";
</script>

<div class="r1-fond" role="presentation" on:click={() => dispatch("annuler")}></div>

<div class="r1 zone-tactile" role="dialog" aria-modal="true" aria-label={titre}>
  <span class="r1-poignee" aria-hidden="true"></span>
  <h2 class="r1-titre">{titre}</h2>

  <div class="champ">
    <label class="champ-libelle" for="r1-motif">Motif</label>
    <select id="r1-motif" class="champ-saisie zone-tactile" bind:value={motif}>
      {#each motifs as m}<option value={m}>{m}</option>{/each}
    </select>
  </div>

  <div class="champ">
    <label class="champ-libelle" for="r1-pin">Code gérant</label>
    <input id="r1-pin" class="champ-saisie zone-tactile" type="password" inputmode="numeric"
           autocomplete="off" bind:value={pin} minlength="4" aria-invalid={erreur ? "true" : undefined} />
  </div>

  {#if erreur}<p class="r1-erreur" role="alert">{erreur}</p>{/if}

  <p class="r1-note">Valable pour cet acte uniquement, 60 secondes</p>

  <Bouton libelle="Valider" large desactive={!pret} on:click={() => dispatch("valider", { motif, jeton: true })} />
  <Bouton libelle="Annuler" variante="contour" large on:click={() => dispatch("annuler")} />
</div>

<style>
  /* voile : la fenêtre est modale, l'arrière-plan est désactivé */
  .r1-fond {
    position: fixed;
    inset: 0;
    background: rgb(0 0 0 / 45%);
    z-index: 40;
  }

  /* téléphone : feuille montante collée au bas de l'écran */
  .r1 {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 41;
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
    max-height: 90vh;
    overflow-y: auto;
    padding: var(--sp-4) var(--sp-4) var(--sp-6);
    background: var(--surface);
    border-top: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-carte) var(--rayon-carte) 0 0;
    box-shadow: var(--ombre);
  }

  .r1-poignee {
    width: 44px;
    height: 4px;
    border-radius: var(--rayon-pastille);
    background: var(--bordure);
    align-self: center;
  }

  .r1-titre { font-size: var(--t-md); margin: 0; }

  .r1-erreur {
    margin: 0;
    color: var(--danger);
    font-size: var(--t-sm);
  }

  .r1-note {
    margin: 0;
    font-size: var(--t-sm);
    color: var(--texte-secondaire);
  }

  /* écran large : fenêtre centrée */
  @media (min-width: 720px) {
    .r1 {
      left: 50%;
      right: auto;
      bottom: auto;
      top: 50%;
      transform: translate(-50%, -50%);
      width: min(440px, calc(100vw - 2 * var(--sp-6)));
      border: var(--bordure-large) solid var(--bordure);
      border-radius: var(--rayon-carte);
      padding: var(--sp-6);
    }
    .r1-poignee { display: none; }
  }
</style>

