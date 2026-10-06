<!-- I8 · PC caisse : stock, entrées, inventaire, pertes, ardoises, prix. -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import {
    triStock, produitsNegatifs, validerEntree, rejeterEntree, ecartInventaire,
    correctionInventaire, regrouperPertes, valorisationPertes, depassementsPlafond,
    fixerPlafond, rembourser, modifierPrix, ORIGINES_PERTES
  } from "$lib/stock_pc.js";
  export let role = "gerant"; // "gerant" | "proprietaire"
  export let donnees = { mouvements: [], attente: [], historique: [], boissons: [],
                         clients: [], pertes: [], catalogues: [], couts: {} };
  export let onValider = () => {};
  export let onRejeter = () => {};
  export let onInventaire = () => {};
  export let onPlafond = () => {};
  export let onRemboursement = () => {};
  export let onPrix = () => {};
  const VUES = ["Stock", "Entrées", "Inventaire", "Pertes", "Ardoises", "Prix"];
  let vue = "Stock";
  let message = "";
  let cible = null;      // boisson de la ligne d'inventaire saisie
  let comptee = null;
  let motifEcart = "";
  let clientPlafond = null; let plafondNouveau = null;
  let clientRemb = null; let montantRemb = null;
  let produitPrix = ""; let prixNouveau = null;
  const totaux = new Map();
  for (const m of donnees.mouvements) totaux.set(m.produit, (totaux.get(m.produit) ?? 0) + m.quantite);
  $: lignesStock = triStock([...totaux].map(([produit, quantite]) => ({ produit, quantite })));
  $: negatifs = produitsNegatifs(donnees.mouvements);
  $: depassements = depassementsPlafond(donnees.clients);
  function valider(entree) {
    const r = validerEntree(entree.saisiePar, "gérant", entree.peutSaisir ?? true, entree.lignes);
    if (r.ok) { message = ""; onValider(entree, r.mouvements); } else message = r.raison;
  }
  function rejeter(entree) {
    const r = rejeterEntree(entree);
    message = r.note ?? "";
    onRejeter(entree, r.mouvements);
  }
  function corriger() {
    const b = donnees.boissons.find((x) => x.nom === cible);
    if (!b) { message = "Choisissez une boisson"; return; }
    const e = ecartInventaire(b.theorique, comptee ?? NaN);
    if (!e.ok) { message = e.raison; return; }
    if (e.ecart === 0) { message = "Aucun écart, rien à corriger"; return; }
    const r = correctionInventaire(b.nom, b.theorique, comptee, motifEcart);
    if (!r.ok) { message = r.raison; return; }
    message = "";
    onInventaire(r.mouvement, motifEcart);
  }
  function appliquerPlafond() {
    const r = fixerPlafond(clientPlafond, plafondNouveau);
    if (r.ok) { message = ""; onPlafond(r.client); } else message = r.raison;
  }
  function encaisserRemb() {
    const r = rembourser(clientRemb?.solde ?? 0, montantRemb ?? 0, "espèces");
    if (r.ok) { message = ""; onRemboursement(clientRemb, montantRemb); } else message = r.raison;
  }
  function changerPrix() {
    const r = modifierPrix(0, prixNouveau ?? NaN, donnees.couts[produitPrix] ?? 0, "gérant");
    if (r.ok) { message = ""; onPrix(r.changement); } else message = r.raison;
  }
</script>
<svelte:head><title>PC · Stock et ardoises</title></svelte:head>
<nav aria-label="Sections stock">{#each VUES as v, i}<button class="zone-tactile" aria-current={vue === v} on:click={() => { vue = v; message = ""; }}>{v} ({i + 1})</button>{/each}</nav>
{#if message}<p role="alert">{message}</p>{/if}

{#if vue === "Stock"}
  <h1>Stock</h1>
  {#if negatifs.length > 0}<p role="alert">⚠ Stock négatif : {negatifs.join(", ")}</p>{/if}
  <table>
    <thead><tr><th>Produit</th><th>Quantité</th></tr></thead>
    <tbody>{#each lignesStock as l}<tr><td>{l.produit}</td><td>{l.quantite}</td></tr>{/each}</tbody>
  </table>
  <h2>Historique des mouvements</h2>
  <table>
    <thead><tr><th>Produit</th><th>Quantité</th><th>Type</th></tr></thead>
    <tbody>{#each donnees.historique as m}<tr><td>{m.produit}</td><td>{m.quantite}</td><td>{m.type}</td></tr>{/each}</tbody>
  </table>
{:else if vue === "Entrées"}
  <h1>Entrées de stock</h1>
  <p>Seules des quantités sont saisies. Disponible et en attente sont affichés séparément.</p>
  <table>
    <thead><tr><th>Produit</th><th>Disponible</th><th>En attente</th></tr></thead>
    <tbody>{#each donnees.catalogues as p}<tr><td>{p.nom}</td><td>{p.disponible ?? 0}</td><td>{p.attente ?? 0}</td></tr>{/each}</tbody>
  </table>
  <h2>File des entrées à valider</h2>
  {#each donnees.attente as entree}
    <div>
      <p>{entree.saisiePar} — {entree.lignes.map((l) => l.produit + " × " + l.quantite).join(", ")} — {entree.validee ? "validée" : "à valider"}</p>
      {#if !entree.validee}
        <Bouton libelle="Valider" variante="plein" on:click={() => valider(entree)} />
        <Bouton libelle="Rejeter" on:click={() => rejeter(entree)} />
      {/if}
    </div>
  {/each}
{:else if vue === "Inventaire"}
  <h1>Inventaire quotidien des boissons</h1>
  <p>Après clôture des caisses, avant clôture de la journée. Écarts en quantités.</p>
  <table>
    <thead><tr><th>Boisson</th><th>Théorique</th><th>Comptée</th><th>Écart</th></tr></thead>
    <tbody>
      {#each donnees.boissons as b}
        <tr><td>{b.nom}</td><td>{b.theorique}</td><td>{b.comptee ?? "—"}</td><td>{b.comptee != null ? b.comptee - b.theorique : "—"}</td></tr>
      {/each}
    </tbody>
  </table>
  <select bind:value={cible} aria-label="Boisson à corriger"><option value={null}>— choisir —</option>{#each donnees.boissons as b}<option value={b.nom}>{b.nom}</option>{/each}</select>
  <label>Comptée <input type="number" step="1" bind:value={comptee} /></label>
  <label>Motif de l'écart <input type="text" bind:value={motifEcart} /></label>
  <Bouton libelle="Enregistrer la correction" variante="plein" on:click={corriger} />
{:else if vue === "Pertes"}
  <h1>Pertes</h1>
  <p>Regroupées par origine, affichées séparément.</p>
  {#each ORIGINES_PERTES as origine}
    <section aria-label={origine}>
      <h2>{origine}</h2>
      <ul>{#each (regrouperPertes(donnees.pertes)[origine] ?? []) as p}<li>{p.produit} × {p.quantite}</li>{/each}</ul>
    </section>
  {/each}
  {#if role === "proprietaire"}
    <p>Valeur des pertes : {valorisationPertes(donnees.pertes, true)}</p>
  {/if}
{:else if vue === "Ardoises"}
  <h1>Ardoises</h1>
  {#if depassements.length > 0}
    <p role="alert">⚠ Plafond dépassé : {depassements.map((c) => c.nom).join(", ")}</p>
  {/if}
  <table>
    <thead><tr><th>Client</th><th>Solde</th><th>Plafond</th><th>État</th></tr></thead>
    <tbody>
      {#each donnees.clients as c}
        <tr><td>{c.nom}</td><td>{c.solde}</td><td>{c.plafond ?? "—"}</td><td>{c.plafond !== null && c.solde > c.plafond ? "dépassement" : "ok"}</td></tr>
      {/each}
    </tbody>
  </table>
  <h2>Fixer un plafond (gérant ou propriétaire)</h2>
  <select bind:value={clientPlafond} aria-label="Client plafond">{#each donnees.clients as c}<option value={c}>{c.nom}</option>{/each}</select>
  <input type="number" step="1" aria-label="Nouveau plafond" bind:value={plafondNouveau} />
  <Bouton libelle="Fixer le plafond" variante="plein" on:click={appliquerPlafond} />
  <h2>Enregistrer un remboursement</h2>
  <select bind:value={clientRemb} aria-label="Client remboursement">{#each donnees.clients as c}<option value={c}>{c.nom}</option>{/each}</select>
  <input type="number" step="1" aria-label="Montant remboursé" bind:value={montantRemb} />
  <Bouton libelle="Rembourser en espèces" variante="plein" on:click={encaisserRemb} />
{:else}
  <h1>Prix de vente</h1>
  <p>Un changement de prix ne s'applique qu'aux nouvelles lignes.</p>
  <select bind:value={produitPrix} aria-label="Produit prix">{#each donnees.catalogues as p}<option value={p.nom}>{p.nom} — {p.prix}</option>{/each}</select>
  <input type="number" step="1" aria-label="Nouveau prix" bind:value={prixNouveau} />
  <Bouton libelle="Appliquer le nouveau prix" variante="plein" on:click={changerPrix} />
{/if}
<style>
  nav { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1rem; }
  table { border-collapse: collapse; width: 100%; font-size: 14px; }
  th, td { border: 1px solid var(--bord); padding: 4px 8px; text-align: left; }
</style>

