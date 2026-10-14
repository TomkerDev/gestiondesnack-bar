<!-- I3 · Liste des commandes ouvertes du serveur, groupées par table.
   Action principale : « Nouvelle commande » (table ou comptoir). -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import PastilleStatut from "$lib/components/PastilleStatut.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import { groupParTable } from "$lib/detail_commande.js";
  export let commandes = [];
  export let enLigne = true;
  export let onNouvelle = () => {};
  export let onOuvrir = () => {};
  $: groupes = groupParTable(commandes);
  function etatCuisine(c) {
    if (c.lignes.some((l) => l.statutCuisine === "en préparation")) return "en préparation";
    if (c.lignes.length && c.lignes.every((l) => l.statutCuisine === "prêt")) return "pret";
    return "envoyé";
  }
</script>
<svelte:head><title>Mes commandes</title></svelte:head>
<BandeauConnexion {enLigne} />
<h1>Mes commandes</h1>
<div class="barre-action">
  <Bouton libelle="Nouvelle commande" large on:click={() => onNouvelle()} />
</div>
{#if commandes.length === 0}
  <p class="etat-vide">Aucune commande ouverte</p>
{/if}
{#each Object.entries(groupes) as [nomGroupe, liste]}
  <section class="groupe" aria-label={nomGroupe}>
    <h2>{nomGroupe}</h2>
    <ul>
      {#each liste as c}
        <li class="zone-tactile">
          <button class="zone-tactile" on:click={() => onOuvrir(c.id)} aria-label={"Ouvrir commande " + c.id}>
            {nomGroupe} · {c.lignes.length} lignes · total {c.total}
          </button>
          <PastilleStatut statut={etatCuisine(c)} />
        </li>
      {/each}
    </ul>
  </section>
{/each}

<style>
  /* I3 · Liste : groupes par table, une carte par commande, pastille de statut. */
  .barre-action { display: flex; }

  .etat-vide {
    padding: var(--sp-8) var(--sp-4);
    text-align: center;
    color: var(--texte-secondaire);
    border: 1px dashed var(--bordure);
    border-radius: var(--rayon-carte);
  }

  .groupe {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
  }

  .groupe h2 {
    font-size: var(--t-md);
    color: var(--texte-secondaire);
    text-transform: capitalize;
  }

  .groupe ul {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    padding: 0;
    margin: 0;
    list-style: none;
  }

  .groupe li {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-2);
    background: var(--surface);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-carte);
    box-shadow: var(--ombre);
  }

  .groupe li button {
    flex: 1;
    min-height: var(--tactile);
    padding: var(--sp-2) var(--sp-3);
    text-align: left;
    border-radius: var(--rayon-bouton);
    font-size: var(--t-base);
    font-variant-numeric: tabular-nums;
    cursor: pointer;
  }
  .groupe li button:hover { background: var(--surface-haute); }
</style>
