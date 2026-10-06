<!-- I7 · PC caisse (gérant/propriétaire) : nav latérale, tableaux denses, raccourcis clavier.
   3 vues : tableau de bord (alertes, ventes en cours, appareils), journée (ouvrir/suivre/clôturer),
   caisses (clôtures + forçage R1). R3 : colonnes coûts/marges seulement si propriétaire. -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import FenetreR1 from "$lib/components/FenetreR1.svelte";
  import { alertes, peutCloturerJournee, forcerCloture, colonnes, ouvrirJournee } from "$lib/pc_gerant.js";
  export let role = "gerant"; // "gerant" | "proprietaire"
  export let donnees = { stockNegatif: false, entreesAValider: 0, ardoisesAuPlafond: 0, ecartsCaisse: false,
                         ventesEnCours: [], appareils: [], journee: null, caisses: [] };
  export let onJournee = () => {};
  export let onForcer = () => {};
  const VUES = [["bord", "Tableau de bord"], ["journee", "Journée"], ["caisses", "Caisses"]];
  let vue = "bord";
  let forcerCaisse = null;
  let motif = ""; let commentaire = "";
  let message = "";
  $: cols = colonnes(role);
  $: alertesListe = alertes(donnees);
  $: cloture = peutCloturerJournee(donnees.journee);
  function raccourci(e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
    const i = { "1": 0, "2": 1, "3": 2 }[e.key];
    if (i !== undefined) vue = VUES[i][0];
  }
  function ouvrir() {
    const r = ouvrirJournee(donnees.journee, { fondParServeur: donnees.caisses.map((c) => ({ serveur: c.serveur, fond: c.fond || 0 })) });
    if (r.ok) { message = ""; onJournee(r.journee); } else message = r.raison;
  }
  function cloturer() {
    if (cloture.ok) { message = ""; onJournee({ ...donnees.journee, etat: "clôturée" }); }
    else message = cloture.raison;
  }
  function validerR1() {
    const r = forcerCloture(forcerCaisse, { jeton: "jeton-60s", motif, commentaire });
    if (r.ok) { message = ""; onForcer(r.caisse); forcerCaisse = null; motif = ""; commentaire = ""; }
    else message = r.raison;
  }
</script>
<svelte:head><title>PC caisse</title></svelte:head>
<svelte:window on:keydown={raccourci} />
<div class="pc">
  <nav aria-label="Navigation">
    {#each VUES as [cle, lib], i}
      <button class="zone-tactile" aria-current={vue === cle} on:click={() => vue = cle}>{lib} ({i + 1})</button>
    {/each}
  </nav>
  <main>
    {#if message}<p role="alert">{message}</p>{/if}
    {#if vue === "bord"}
      <h1>Tableau de bord</h1>
      <section aria-label="Alertes">
        <h2>Alertes</h2>
        {#if alertesListe.length === 0}<p>Aucune alerte</p>{:else}
          <ul>{#each alertesListe as a}<li role="alert">{a}</li>{/each}</ul>
        {/if}
      </section>
      <section aria-label="Ventes en cours">
        <h2>Ventes en cours</h2>
        <table><thead><tr><th>Table</th><th>Total</th></tr></thead>
          <tbody>{#each donnees.ventesEnCours as v}<tr><td>{v.table}</td><td>{v.total}</td></tr>{/each}</tbody>
        </table>
      </section>
      <section aria-label="Appareils">
        <h2>Appareils connectés</h2>
        <table><thead><tr><th>Appareil</th><th>État</th></tr></thead>
          <tbody>{#each donnees.appareils as d}<tr><td>{d.nom}</td><td>{d.enLigne ? "en ligne" : "hors ligne"}</td></tr>{/each}</tbody>
        </table>
      </section>
    {:else if vue === "journee"}
      <h1>Journée</h1>
      <Bouton libelle="Ouvrir la journée" desactive={donnees.journee?.etat === "ouverte"} on:click={ouvrir} />
      <p>État : {donnees.journee ? donnees.journee.etat : "aucune journée"}</p>
      <Bouton libelle="Clôturer la journée" desactive={!cloture.ok} on:click={cloturer} />
      {#if !cloture.ok && donnees.journee}<p role="note">↳ {cloture.raison}</p>{/if}
      <table><thead><tr><th>Serveur</th><th>Fond</th><th>État</th></tr></thead>
        <tbody>{#each donnees.caisses as c}<tr><td>{c.serveur}</td><td>{c.fond}</td><td>{c.etat}</td></tr>{/each}</tbody>
      </table>
    {:else}
      <h1>Caisses</h1>
      <table>
        <thead><tr>{#each cols as col}<th>{col}</th>{/each}<th>Action</th></tr></thead>
        <tbody>
          {#each donnees.caisses as c}
            <tr>
              <td>{c.serveur}</td><td>{c.total}</td><td>{c.ecart}</td>
              {#if role === "proprietaire"}<td>{c.cout}</td><td>{c.marge}</td>{/if}
              <td>
                {#if c.etat !== "close"}<button class="zone-tactile" on:click={() => forcerCaisse = c}>Forcer la clôture</button>{:else}close{/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if forcerCaisse}
        <FenetreR1 motifs={["oubli de clôture", "partie anticipée", "Autre"]} bind:motif
          titre={"Forcer la clôture de " + forcerCaisse.serveur} on:valider={validerR1} />
      {/if}
    {/if}
  </main>
</div>
<style>
  .pc { display: flex; min-height: 100vh; }
  nav { width: 220px; border-right: 1px solid var(--bord); display: flex; flex-direction: column; }
  table { border-collapse: collapse; width: 100%; font-size: 14px; } /* tableau dense */
  th, td { border: 1px solid var(--bord); padding: 4px 8px; text-align: left; }
</style>
