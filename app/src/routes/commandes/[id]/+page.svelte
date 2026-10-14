<!-- I3 · Détail d'une commande : lignes + statut cuisine, actions selon rôle/état/offline.
   Payée → seulement « Demander une correction ». Offline → actions visibles avec raison. -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import LigneCommande from "$lib/components/LigneCommande.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import FenetreR1 from "$lib/components/FenetreR1.svelte";
  import { actions, annulerPlat, imprimerAddition } from "$lib/detail_commande.js";
  export let commande;
  export let enLigne = true;
  export let dejaImprime = false;
  export let motifR1 = ["erreur de service", "geste commercial", "Autre"];
  export let onAction = null; // callback d'intégration (id d'action de detail_commande.actions)
  let demandeR1 = null;
  let message = "";
  $: listeActions = actions(commande, { enLigne, dejaImprime });
  function tenterAnnulation(ligne) {
    const r = annulerPlat(commande, ligne.id, { enLigne });
    if (r.ok) {
      commande = { ...commande, lignes: commande.lignes.filter((l) => l.id !== ligne.id) };
      message = "« " + ligne.nom + " » annulé";
      demandeR1 = null;
    } else if (r.demandeR1) { demandeR1 = ligne; message = ""; }
    else { demandeR1 = null; message = r.raison; }
  }
  function validerR1() { demandeR1 = null; message = "Autorisation obtenue — relancer l'annulation"; }
</script>
<svelte:head><title>Détail commande</title></svelte:head>
<BandeauConnexion {enLigne} />
<h1>Commande {commande.id}</h1>
{#if message}<p class="message" role="status">{message}</p>{/if}
<ul class="lignes">
  {#each commande.lignes as l}
    <li class="zone-tactile">
      <LigneCommande nom={l.nom} quantite={l.quantite} prix={l.prix} net={l.net} statutCuisine={l.statutCuisine} />
      <button class="zone-tactile" on:click={() => tenterAnnulation(l)}>Annuler ce plat</button>
    </li>
  {/each}
</ul>
{#if demandeR1}
  <FenetreR1 motifs={motifR1} titre={"Autorisation pour « " + demandeR1.nom + " » (en préparation)"} on:valider={validerR1} />
{/if}
<nav class="actions zone-tactile" aria-label="Actions">
  {#each listeActions as a}
    <button class="zone-tactile" disabled={!a.actif} title={a.raisonInactif}
      on:click={() => onAction?.(a.cle)}
      aria-label={a.libelle + (a.actif ? "" : " — " + a.raisonInactif)}>{a.libelle}</button>
    {#if !a.actif}<span role="note">↳ {a.raisonInactif}</span>{/if}
  {/each}
</nav>
<p class="impression">Impression : {imprimerAddition(dejaImprime).mention}</p>

<style>
  /* I3 · Détail : lignes en cartes, actions en barre, désactivés explicités. */
  .message {
    padding: var(--sp-2) var(--sp-3);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-bouton);
    background: var(--surface-haute);
    font-size: var(--t-sm);
  }

  .lignes {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    padding: 0;
    margin: 0;
    list-style: none;
  }

  .lignes li {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    flex-wrap: wrap;
  }

  .lignes li :global(.ligne) { flex: 1; min-width: 220px; }

  .lignes li button {
    min-height: var(--tactile);
    padding: 0 var(--sp-3);
    border: var(--bordure-large) solid var(--danger);
    border-radius: var(--rayon-bouton);
    color: var(--danger);
    font-size: var(--t-sm);
    font-weight: 600;
    cursor: pointer;
  }
  .lignes li button:hover { background: color-mix(in srgb, var(--danger) 16%, transparent); }

  /* barre d'actions : rangées d'au moins 48 px, raison sous le bouton */
  .actions {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    padding: var(--sp-3);
    background: var(--surface);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-carte);
    box-shadow: var(--ombre);
  }

  .actions button {
    min-height: var(--tactile);
    padding: 0 var(--sp-3);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-bouton);
    background: var(--surface-haute);
    color: var(--texte);
    font-size: var(--t-base);
    font-weight: 600;
    text-align: left;
    cursor: pointer;
    transition: border-color var(--dur) var(--ease), background var(--dur) var(--ease);
  }
  .actions button:hover:not(:disabled) { border-color: var(--accent); }
  .actions button:disabled { opacity: 0.5; cursor: not-allowed; }

  .actions span {
    font-size: var(--t-sm);
    color: var(--texte-secondaire);
    padding-left: var(--sp-3);
  }

  .impression {
    font-size: var(--t-sm);
    color: var(--texte-secondaire);
  }
</style>
