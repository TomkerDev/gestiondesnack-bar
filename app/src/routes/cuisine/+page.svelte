<!-- I5 · Écran cuisine : 3 colonnes (Envoyé, En préparation, Prêt), cartes grandes et lisibles.
   Un appui = avancer le statut. Annulé = rouge + « ANNULÉ » + son. Connexion en haut.
   Hors ligne : message clair, la file n'est pas présentée comme à jour. -->
<script>
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import { avancer, recevoirAnnulation, trier, messageHorsLigne, COLONNES } from "$lib/cuisine.js";
  export let bons = [];
  export let enLigne = true;
  export let dernierSync = "—";
  export let onAvancer = () => {};
  let dernierSignal = "";
  $: col = Object.fromEntries(COLONNES.map((c) => [c, trier(bons.filter((b) => b.statut === c))]));
  function toucheCarte(bon) {
    const suivant = avancer(bon);
    if (suivant.erreur) return;
    dernierSignal = "";
    onAvancer(suivant);
  }
  export function signalAnnulation(bon) {
    const b = recevoirAnnulation(bon);
    dernierSignal = b.signal; // l'appelant joue aussi le son
    onAvancer(b);
    return b;
  }
</script>
<svelte:head><title>Cuisine</title></svelte:head>
<header>
  <BandeauConnexion {enLigne} />
  <p role="status">{messageHorsLigne(enLigne, dernierSync)}</p>
  {#if dernierSignal}<p role="alert">🔔 {dernierSignal === "annulation" ? "ANNULATION REÇUE" : "NOUVEAU BON"}</p>{/if}
</header>
<main aria-label="File cuisine">
  {#each COLONNES as c}
    <section aria-label={c}>
      <h2>{c}</h2>
      {#each col[c] as b (b.id)}
        <button class="carte zone-tactile" class:annule={b.statut === "annulé"}
          aria-label={"Bon table " + b.table + ", " + b.statut}
          disabled={b.statut === "annulé" || b.statut === "prêt"}
          on:click={() => toucheCarte(b)}>
          {#if b.statut === "annulé"}
            <strong>ANNULÉ</strong>
          {:else}
            <span class="table">Table {b.table}</span>
            {#each b.lignes as l}<span>{l.quantite}× {l.nom}</span>{/each}
            <span>Envoyé {b.heure}</span>
            {#if b.duplicata}<span>DUPLICATA</span>{/if}
          {/if}
        </button>
      {/each}
    </section>
  {/each}
</main>
<style>
  .carte { font-size: 24px; min-height: 120px; text-align: left; border: 2px solid var(--bord); }
  .table { font-size: 32px; font-weight: bold; }
  .annule { background: var(--alerte); color: #fff; }
</style>
