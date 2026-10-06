<!-- I1 · Galerie : chaque composant dans chaque état (chargement, vide, hors ligne, erreur, sombre, clair). -->
<script>
  import Bouton from "$lib/components/Bouton.svelte";
  import TuileProduit from "$lib/components/TuileProduit.svelte";
  import PastilleStatut from "$lib/components/PastilleStatut.svelte";
  import BandeauConnexion from "$lib/components/BandeauConnexion.svelte";
  import PavePin from "$lib/components/PavePin.svelte";
  import FenetreR1 from "$lib/components/FenetreR1.svelte";
  import SelecteurMotif from "$lib/components/SelecteurMotif.svelte";
  import LigneCommande from "$lib/components/LigneCommande.svelte";
  let theme = "clair";
</script>
<svelte:head><title>Galerie des composants</title></svelte:head>
<div data-theme={theme}>
  <h1>Galerie</h1>
  <button on:click={() => theme = theme === "clair" ? "sombre" : "clair"}>Basculer {theme}</button>
  <section><h2>Bouton</h2><Bouton libelle="Valider le paiement" /><Bouton libelle="Annuler" variante="contour" /><Bouton libelle="Patientez" desactive={true} /></section>
  <section><h2>Tuile</h2><TuileProduit nom="Bière 65cl" prix="1 500" quantite={0} /><TuileProduit nom="Bière 65cl" prix="1 500" quantite={2} /></section>
  <section><h2>Statuts</h2><PastilleStatut statut="envoyé" /><PastilleStatut statut="en préparation" /><PastilleStatut statut="pret" /></section>
  <section><h2>Bandeau</h2><BandeauConnexion enLigne={true} /><BandeauConnexion enLigne={false} /></section>
  <section><h2>PIN</h2><PavePin /></section>
  <section><h2>R1</h2><FenetreR1 motifs={["erreur de service", "geste commercial", "Autre"]} /></section>
  <section><h2>Motif</h2><SelecteurMotif motifs={["casse non déclarée", "Autre"]} motif="Autre" /></section>
  <section><h2>Ligne</h2><LigneCommande nom="Bière 65cl" quantite={2} prix="1 500" net="3 000" statutCuisine="envoyé" /></section>
  <section><h2>Vide / erreur</h2><p>Aucune commande ouverte</p><p role="alert">La cuisine ne répond pas — les ventes continuent</p></section>
</div>
