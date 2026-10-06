<!-- I4 · Paiement : total, reste, monnaie ; une seule action principale « Valider »
   active uniquement si reste = 0. Règlements multiples, mobile avec opérateur+référence.
   Pourboire hors total. Ardoise distincte avec plafond + R1. Bandeau hors ligne. -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import FenetreR1 from "$lib/components/FenetreR1.svelte";
  import { ajouterReglement, monnaieRendue, peutValider, resteAPayer,
           totalAvecPourboire, payerArdoise, OPERATEURS } from "$lib/paiement.js";
  export let total = 0;
  export let enLigne = true;
  export let soldeArdoise = 0;
  export let plafondArdoise = 0;
  export let motifR1 = ["déblocage plafond", "geste commercial", "Autre"];
  export let onValider = () => {};
  let reglements = [];
  let mode = "especes";
  let montant = 0;
  let recu = 0;
  let operateur = "orange";
  let reference = "";
  let pourboire = 0;
  let avecArdoise = false;
  let message = "";
  let demandeR1 = false;
  $: t = totalAvecPourboire(total, pourboire);
  $: reste = avecArdoise ? 0 : resteAPayer(total, reglements);
  $: rendu = monnaieRendue(recu, total - reglements.reduce((s, r) => s + r.montant, 0));
  $: actif = avecArdoise ? peutArdoise : peutValider(total, reglements);
  $: peutArdoise = (() => {
    const r = payerArdoise(total, soldeArdoise, plafondArdoise, { enLigne });
    demandeR1 = r.demandeR1 === true;
    return r.ok;
  })();
  function ajouter() {
    const r = ajouterReglement(reglements, { mode, montant: Number(montant), operateur, reference });
    if (r.erreur) message = r.erreur; else { reglements = r.reglements; message = ""; montant = 0; reference = ""; }
  }
  function valider() { if (actif) onValider({ reglements, pourboire, avecArdoise }); }
</script>
<svelte:head><title>Paiement</title></svelte:head>
<BandeauConnexion {enLigne} />
<h1>Paiement</h1>
<dl>
  <dt>Total net</dt><dd>{t.total}</dd>
  <dt>Reste à payer</dt><dd>{reste}</dd>
  <dt>Monnaie à rendre</dt><dd>{rendu.erreur ? "—" : rendu.rendu}</dd>
</dl>
{#if message}<p role="alert">{message}</p>{/if}
<section aria-label="Règlements">
  <label>Mode<select class="zone-tactile" bind:value={mode}>
    <option value="especes">Espèces</option><option value="mobile">Mobile money</option>
  </select></label>
  <label>Montant<input class="zone-tactile" type="number" min="1" step="1" bind:value={montant} /></label>
  {#if mode === "especes"}<label>Reçu<input class="zone-tactile" type="number" min="0" step="1" bind:value={recu} /></label>{/if}
  {#if mode === "mobile"}
    <label>Opérateur<select class="zone-tactile" bind:value={operateur}>{#each OPERATEURS as o}<option>{o}</option>{/each}</select></label>
    <label>Référence<input class="zone-tactile" bind:value={reference} required /></label>
  {/if}
  <Bouton libelle="Ajouter le règlement" variante="contour" on:click={ajouter} />
  <ul>{#each reglements as r}<li>{r.mode} — {r.montant}{r.reference ? " (" + r.operateur + " " + r.reference + ")" : ""}</li>{/each}</ul>
</section>
<label>Pourboire (hors total)<input class="zone-tactile" type="number" min="0" step="1" bind:value={pourboire} /></label>
<section aria-label="Ardoise">
  <button class="zone-tactile" aria-pressed={avecArdoise} on:click={() => avecArdoise = !avecArdoise}>Payer sur l'ardoise</button>
  {#if avecArdoise}
    <p>Solde {soldeArdoise} · Plafond {plafondArdoise}</p>
    {#if demandeR1}
      <p role="alert">Plafond dépassé — demander un déblocage</p>
      <FenetreR1 motifs={motifR1} titre="Déblocage ardoise" on:valider={() => demandeR1 = false} />
    {:else if !enLigne}
      <p role="note">Hors ligne : dernière copie des soldes, déblocage impossible</p>
    {/if}
  {/if}
</section>
<Bouton libelle="Valider le paiement" desactive={!actif} on:click={valider} />
