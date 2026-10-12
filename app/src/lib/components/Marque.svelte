<!-- Marque « Braise » : flambeau + nom, réutilisé (accueil, connexion, en-tête). -->
<script>export let taille = 40;</script>
<span class="marque zone-tactile" aria-label="Snack-bar Braise">
  <svg width={taille} height={taille} viewBox="0 0 48 48" aria-hidden="true">
    <circle cx="24" cy="24" r="22" fill="var(--primaire)" />
    <path d="M24 8c2 6-4 8-2 14 1.4 4.2 6 5 6 10a8 8 0 1 1-16 0c0-3 2-5 3.5-7C17 21 18 17 20 14c1 2 2 3 2.5 5C24 17 24 12 24 8z"
          fill="#fff7ed" />
    <circle cx="24" cy="34" r="3.2" fill="var(--primaire-fonce)" />
  </svg>
  <span class="nom">Snack-bar <b>Braise</b></span>
</span>
<style>
  .marque { display: inline-flex; align-items: center; gap: 10px; }
  .nom { font-size: 20px; }
</style>
