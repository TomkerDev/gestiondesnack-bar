<!-- I6 · Ma caisse (serveur) : résumé CAI-2 affiché ligne à ligne, sortie de caisse
   en attente gérant, clôture avec écart justifié obligatoire, puis « en attente du gérant ».
   Toute saisie de montant est entière (i64 back). -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import SelecteurMotif from "$lib/components/SelecteurMotif.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import { especesAttendues, ecart, cloturerServeur, saisirSortie, MOTIFS_SORTIE } from "$lib/ma_caisse.js";
  export let r = { fondCaisse: 0, especesEncaissees: 0, remboursementsArdoise: 0,
                   pourboires: 0, entreesCaisse: 0, sortiesCaisse: 0 };
  export let enLigne = true;
  export let dejaCloture = false;
  export let onCloturer = () => {};
  let sorties = [];
  let montantSortie = 0;
  let motifSortie = MOTIFS_SORTIE[0];
  let commentaireSortie = "";
  let compte = 0;
  let motifEcart = "";
  let commentaireEcart = "";
  let message = "";
  $: attendu = especesAttendues({ ...r, sortiesCaisse: r.sortiesCaisse + sorties.reduce((s, x) => s + x.montant, 0) });
  $: ecartV = ecart(Number(compte) || 0, attendu);
  $: lignes = [
    ["Fond de caisse", r.fondCaisse],
    ["Espèces encaissées", r.especesEncaissees],
    ["Remboursements ardoise", -r.remboursementsArdoise],
    ["Pourboires", r.pourboires],
    ["Entrées de caisse", r.entreesCaisse],
    ["Sorties de caisse", -r.sortiesCaisse],
  ];
  function ajouterSortie() {
    const s = saisirSortie(sorties, { montant: Number(montantSortie), motif: motifSortie, commentaire: commentaireSortie });
    if (s.erreur) message = s.erreur;
    else { sorties = s.sorties; message = ""; montantSortie = 0; commentaireSortie = ""; }
  }
  function cloturer() {
    const res = cloturerServeur({ compte: Number(compte) || 0, attendu, motif: motifEcart, commentaire: commentaireEcart, dejaCloture });
    if (res.ok) { message = ""; onCloturer(res); }
    else message = res.raison;
  }
</script>
<svelte:head><title>Ma caisse</title></svelte:head>
<BandeauConnexion {enLigne} />
<h1>Ma caisse</h1>
{#if dejaCloture}
  <p role="status">Clôturée — en attente du gérant. Plus aucune vente possible pour vous aujourd'hui.</p>
{/if}
{#if message}<p role="alert">{message}</p>{/if}
<section aria-label="Résumé">
  <h2>Espèces attendues (CAI-2)</h2>
  <dl>
    {#each lignes as [lib, v]}<dt>{lib}</dt><dd>{v}</dd>{/each}
  </dl>
  <p><strong>Total : {attendu}</strong></p>
</section>
<section aria-label="Sortie de caisse">
  <h2>Sortie de caisse</h2>
  <label>Montant<input class="zone-tactile" type="number" min="1" step="1" bind:value={montantSortie} /></label>
  <SelecteurMotif motifs={MOTIFS_SORTIE} bind:motif={motifSortie} bind:commentaire={commentaireSortie} />
  <Bouton libelle="Demander la sortie" variante="contour" desactive={dejaCloture} on:click={ajouterSortie} />
  <ul>{#each sorties as s}<li>{s.montant} — {s.motif} · {s.statut}</li>{/each}</ul>
</section>
<section aria-label="Clôture">
  <h2>Clôture</h2>
  <label>Montant compté<input class="zone-tactile" type="number" min="0" step="1" bind:value={compte} /></label>
  <p>Écart : <strong>{ecartV}</strong></p>
  {#if ecartV !== 0}
    <SelecteurMotif motifs={["erreur de service", "comptage", "Autre"]} bind:motif={motifEcart} bind:commentaire={commentaireEcart} />
    <p role="note">Écart non nul : motif et commentaire obligatoires</p>
  {/if}
  <Bouton libelle="Clôturer ma caisse" desactive={dejaCloture} on:click={cloturer} />
</section>
