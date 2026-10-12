<!-- I2 · Prise de commande : grille unique + filtres catégorie, un appui = +1.
   Téléphone : barre fixe bas (articles, total, Envoyer). Tablette : grille + commande à droite.
   Stock zéro : jamais bloquant côté serveur (alerte gérant côté back). Hors ligne : bandeau. -->
<script>
  import { onMount } from "svelte";
  import Bouton from "$lib/components/Bouton.svelte";
  import TuileProduit from "$lib/components/TuileProduit.svelte";
  import LigneCommande from "$lib/components/LigneCommande.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import { ajouter, retirer, annulerRetrait, nbArticles, total } from "$lib/panier.js";
  import { api } from "$lib/api.js";
  import { goto } from "$app/navigation";
  export let produits = [];
  export let enLigne = true;
  export let onEnvoyer = null; // injecté par le layout (testé en isolation sinon)
  export let onPayer = null;
  const FILTRES = ["Tout", "Bières", "Softs", "Alcools", "Plats"];
  let filtre = "Tout";
  let panier = { lignes: [] };
  let restauration = null;
  let message = "";
  let envoi = false;
  $: visibles = filtre === "Tout" ? produits : produits.filter((p) => p.categorie === filtre);
  onMount(() => { charger(); });
  async function charger() {
    const r = await api.catalogue(); // PC caisse = référence de données (spec §6)
    enLigne = api.etat.enLigne;
    if (r.ok) produits = r.produits;
    else message = r.raison;
  }
  function touche(produit) { panier = ajouter(panier, produit); restauration = null; message = ""; }
  function touchePastille(produit) {
    const r = retirer(panier, produit.id);
    panier = r.panier; restauration = r.annulable;
    message = "Retiré — " + (r.annulable ? "Annuler" : "");
  }
  function annuler() {
    if (restauration) { panier = annulerRetrait(restauration); restauration = null; message = ""; }
  }
  async function envoyer() {
    if (panier.lignes.length === 0 || envoi) return;
    envoi = true;
    const r = onEnvoyer ? await onEnvoyer(panier) : await api.creerCommande(panier.lignes);
    if (r.ok && !r.differe && !onEnvoyer && r.commande?.id) {
      const k = await api.envoyerCuisine(r.commande.id); // CUI-1 : un envoi = un bon
      if (!k.ok) { envoi = false; message = k.raison; return; }
    }
    envoi = false;
    if (r.ok) {
      panier = { lignes: [] };
      message = r.differe ? "Envoyé — sera synchronisé au retour du réseau" : "Commande envoyée en cuisine";
      if (!r.differe && typeof goto === "function" && r.commande?.id) goto("/commandes/" + r.commande.id);
    } else message = r.raison;
  }
  async function payer() {
    if (panier.lignes.length === 0 || envoi) return;
    if (onPayer) { onPayer(panier); return; }
    envoi = true;
    // CMD-1 (comptoir) : créée, envoyée en cuisine puis payée dans un seul flux
    const r = await api.creerCommande(panier.lignes);
    if (r.ok && !r.differe && r.commande?.id) await api.envoyerCuisine(r.commande.id);
    envoi = false;
    enLigne = api.etat.enLigne;
    if (!r.ok) { message = r.raison; return; }
    if (r.differe || !r.commande?.id) { message = "Envoyé — paiement différé jusqu'au retour du réseau"; return; }
    panier = { lignes: [] };
    try { sessionStorage.setItem("snack.aPayer", r.commande.id); } catch { /* stockage local absent */ }
    goto("/paiement");
  }
</script>
<svelte:head><title>Prise de commande</title></svelte:head>
<BandeauConnexion {enLigne} />
<nav aria-label="Catégories">
  {#each FILTRES as f}<button class="zone-tactile" aria-pressed={filtre === f} on:click={() => filtre = f}>{f}</button>{/each}
</nav>
<div class="conteneur">
  <section aria-label="Catalogue">
    {#each visibles as p}
      <TuileProduit nom={p.nom} prix={p.prix} quantite={(panier.lignes.find((l) => l.id === p.id) || {}).quantite || 0}
        on:touche={() => touche(p)} on:pastille={() => touchePastille(p)} />
    {/each}
  </section>
  <aside aria-label="Commande en cours">
    <ul>{#each panier.lignes as l}<LigneCommande nom={l.nom} quantite={l.quantite} prix={l.prix} net={l.quantite * l.prix} />{/each}</ul>
    {#if message}<p role="status">{message} <button class="zone-tactile" on:click={annuler}>Annuler</button></p>{/if}
    <p>Total {total(panier)} · {nbArticles(panier)} articles</p>
    <Bouton libelle="Envoyer en cuisine" desactive={panier.lignes.length === 0 || envoi} on:click={envoyer} />
    <Bouton libelle="Payer" variante="contour" desactive={panier.lignes.length === 0} on:click={payer} />
  </aside>
</div>
