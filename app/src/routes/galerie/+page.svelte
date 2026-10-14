<!-- I1 · Galerie : chaque composant dans chaque état, en thème sombre ET clair.
     La bascule pose data-theme sur <html> — le thème devient global, plus un
     simple <div> orphelin. Page de développement uniquement (jamais en prod). -->
<script>
  import { onMount } from "svelte";
  import Bouton from "$lib/components/Bouton.svelte";
  import TuileProduit from "$lib/components/TuileProduit.svelte";
  import PastilleStatut from "$lib/components/PastilleStatut.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import PavePin from "$lib/components/PavePin.svelte";
  import FenetreR1 from "$lib/components/FenetreR1.svelte";
  import SelecteurMotif from "$lib/components/SelecteurMotif.svelte";
  import LigneCommande from "$lib/components/LigneCommande.svelte";
  import Navigation from "$lib/components/Navigation.svelte";
  import Champ from "$lib/components/Champ.svelte";
  import Marque from "$lib/components/Marque.svelte";

  let theme = "sombre";
  let pin = "";
  let motif = "";
  let commentaire = "";
  let champTexte = "";
  let champNombre = 0;
  let fenetreOuverte = false;

  const LIENS_DEMO = [
    ["/commande", "Prise de commande"],
    ["/commandes", "Mes commandes"],
    ["/cuisine", "Cuisine"],
    ["/paiement", "Paiement"],
    ["/ma-caisse", "Ma caisse"],
    ["/pc", "PC caisse"],
    ["/pc/stock", "Stock & prix"],
    ["/galerie", "Galerie"]
  ];

  onMount(() => {
    document.documentElement.setAttribute("data-theme", theme);
    return () => document.documentElement.removeAttribute("data-theme");
  });

  function basculer() {
    theme = theme === "sombre" ? "clair" : "sombre";
    document.documentElement.setAttribute("data-theme", theme);
  }
</script>

<svelte:head><title>Galerie des composants</title></svelte:head>

<header class="gal-entete">
  <div>
    <h1>Galerie des composants</h1>
    <p class="gal-sous">Chaque composant, chaque état — thème {theme}.</p>
  </div>
  <button type="button" class="gal-bascule zone-tactile" class:gal-bascule--clair={theme === "clair"}
          aria-pressed={theme === "clair"} on:click={basculer}>
    Basculer {theme}
  </button>
</header>
  <section class="gal-bloc" aria-labelledby="g-bouton">
  <h2 id="g-bouton">Bouton</h2>
  <div class="gal-range">
    <Bouton libelle="Valider le paiement" />
    <Bouton libelle="Annuler" variante="contour" />
    <Bouton libelle="Supprimer" variante="danger" />
    <Bouton libelle="Patientez" desactive={true} />
    <Bouton libelle="Envoi en cuisine" chargement={true} />
    <Bouton libelle="Pleine largeur" large={true} />
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-tuile">
  <h2 id="g-tuile">Tuile produit</h2>
  <div class="gal-grille">
    <TuileProduit nom="Bière 65cl" prix="1 500" quantite={0} />
    <TuileProduit nom="Bière 65cl" prix="1 500" quantite={2} />
    <TuileProduit nom="Attiéké poisson" prix="2 500" quantite={1} selectionne={true} />
    <TuileProduit nom="Poulet braisé" prix="3 000" quantite={0} indispo={true} />
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-pastille">
  <h2 id="g-pastille">Pastille de statut</h2>
  <div class="gal-range">
    <PastilleStatut statut="envoyé" />
    <PastilleStatut statut="en préparation" />
    <PastilleStatut statut="prêt" />
    <PastilleStatut statut="annulé" />
    <PastilleStatut statut="pret" />
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-bandeau">
  <h2 id="g-bandeau">Bandeau de connexion</h2>
  <div class="gal-colonne">
    <BandeauConnexion enLigne={true} />
    <BandeauConnexion enLigne={false} />
    <BandeauConnexion enLigne={false} message="Dernière synchro il y a 12 min." />
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-pin">
  <h2 id="g-pin">Clavier PIN</h2>
  <PavePin bind:valeur={pin} attendu={4} />
</section>

<section class="gal-bloc" aria-labelledby="g-ligne">
  <h2 id="g-ligne">Ligne de commande</h2>
  <ul class="gal-liste">
    <LigneCommande nom="Bière 65cl" quantite={2} prix="1 500" net="3 000" statutCuisine="envoyé" />
    <LigneCommande nom="Attiéké poisson" quantite={1} prix="2 500" net="2 500" statutCuisine="prêt" />
    <LigneCommande nom="Soda 33cl" quantite={3} prix="500" net="1 500" statutCuisine="" />
  </ul>
</section>

<section class="gal-bloc" aria-labelledby="g-nav">
  <h2 id="g-nav">Navigation</h2>
  <Navigation liens={LIENS_DEMO} chemin="/commandes" />
</section>

<section class="gal-bloc" aria-labelledby="g-champ">
  <h2 id="g-champ">Champs de formulaire</h2>
  <div class="gal-colonne">
    <Champ libelle="Référence" bind:valeur={champTexte} placeholder="Ex. MP-4821"
           aide="Portée par le reçu mobile money." />
    <Champ libelle="Montant" type="number" bind:valeur={champNombre} min={1} step={1} />
    <SelecteurMotif motifs={["erreur de service", "geste commercial", "Autre"]}
                    bind:motif bind:commentaire requis={true} />
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-etats">
  <h2 id="g-etats">États de page</h2>
  <div class="gal-colonne">
    <div class="gal-vide">Aucune commande ouverte</div>
    <div class="bande-etat bande-etat--alerte" role="alert">La cuisine ne répond pas — les ventes continuent</div>
    <div class="bande-etat bande-etat--succes" role="status">Commande envoyée en cuisine</div>
    <div class="bande-etat bande-etat--danger" role="alert">Annulation refusée — bon déjà servi</div>
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-marque">
  <h2 id="g-marque">Marque</h2>
  <div class="gal-range gal-range--marque">
    <Marque taille={24} />
    <Marque taille={40} />
    <Marque taille={64} />
  </div>
</section>

<section class="gal-bloc" aria-labelledby="g-r1">
  <h2 id="g-r1">Fenêtre d'autorisation gérant (R1)</h2>
  <Bouton libelle={fenetreOuverte ? "Masquer l'autorisation" : "Afficher l'autorisation"}
          variante="contour" on:click={() => (fenetreOuverte = !fenetreOuverte)} />
  {#if fenetreOuverte}
    <FenetreR1 motifs={["erreur de service", "geste commercial", "Autre"]}
               titre="Autorisation pour « Poulet braisé » (en préparation)" />
  {/if}
</section>

<style>
  .gal-entete {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--sp-4);
    flex-wrap: wrap;
    padding-bottom: var(--sp-3);
    border-bottom: var(--bordure-large) solid var(--bordure);
  }
  .gal-sous { margin: var(--sp-1) 0 0; color: var(--texte-secondaire); font-size: var(--t-sm); }

  .gal-bascule {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: var(--tactile);
    padding: 0 var(--sp-5);
    border: var(--bordure-large) solid var(--accent);
    border-radius: var(--rayon-bouton);
    background: var(--accent);
    color: var(--sur-accent);
    font-size: var(--t-base);
    font-weight: 600;
  }
  .gal-bascule--clair { background: var(--surface); color: var(--texte); border-color: var(--bordure); }

  .gal-bloc {
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
    padding: var(--sp-4);
    background: var(--surface);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-carte);
    box-shadow: var(--ombre);
  }
  .gal-bloc--large { padding: var(--sp-2); }

  .gal-range { display: flex; flex-wrap: wrap; gap: var(--sp-3); align-items: center; }
  .gal-range--marque { gap: var(--sp-6); }
  .gal-colonne { display: flex; flex-direction: column; gap: var(--sp-3); }
  .gal-grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: var(--sp-3); }
  .gal-liste { display: flex; flex-direction: column; gap: var(--sp-2); }
  .gal-vide {
    padding: var(--sp-6);
    text-align: center;
    color: var(--texte-secondaire);
    border: 1px dashed var(--bordure);
    border-radius: var(--rayon-carte);
  }
</style>
