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
{#if message}<p role="status">{message}</p>{/if}
<ul>
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
<nav class="zone-tactile" aria-label="Actions">
  {#each listeActions as a}
    <button class="zone-tactile" disabled={!a.actif} title={a.raisonInactif}
      on:click={() => onAction?.(a.cle)}
      aria-label={a.libelle + (a.actif ? "" : " — " + a.raisonInactif)}>{a.libelle}</button>
    {#if !a.actif}<span role="note">↳ {a.raisonInactif}</span>{/if}
  {/each}
</nav>
<p>Impression : {imprimerAddition(dejaImprime).mention}</p>
