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
<Bouton libelle="Nouvelle commande" on:click={() => onNouvelle()} />
{#if commandes.length === 0}
  <p>Aucune commande ouverte</p>
{/if}
{#each Object.entries(groupes) as [nomGroupe, liste]}
  <section aria-label={nomGroupe}>
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
