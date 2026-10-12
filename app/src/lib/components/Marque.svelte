<!-- Marque « Apis » : abeille stylisée + nom, réutilisée (accueil, connexion, en-tête). -->
<script>export let taille = 40;</script>
<span class="marque zone-tactile" aria-label="Snack-bar Apis">
  <svg width={taille} height={taille} viewBox="0 0 48 48" aria-hidden="true">
    <circle cx="24" cy="24" r="22" fill="var(--primaire)" />
    <ellipse cx="24" cy="26" rx="10" ry="12" fill="#fff7ed" />
    <path d="M14 22h20M14 30h20" stroke="var(--primaire-fonce)" stroke-width="4" />
    <path d="M16 16c-4-5-10-4-10 0s5 6 9 3M32 16c4-5 10-4 10 0s-5 6-9 3"
          fill="rgba(255,255,255,.85)" stroke="var(--primaire-fonce)" stroke-width="1.5" />
    <circle cx="20" cy="14" r="1.8" fill="#fff7ed" />
    <circle cx="28" cy="14" r="1.8" fill="#fff7ed" />
  </svg>
  <span class="nom">Snack-bar <b>Apis</b></span>
</span>
<style>
  .marque { display: inline-flex; align-items: center; gap: 10px; }
  .nom { font-size: 20px; }
</style>
