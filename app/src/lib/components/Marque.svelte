<!-- Marque « Apis » : abeille stylisée + nom, réutilisée (accueil, connexion, en-tête).
     Aucune couleur en dur : uniquement des jetons de thème. -->
<script>
  export let taille = 40;
</script>

<span class="marque zone-tactile" aria-label="Snack-bar Apis">
  <svg width={taille} height={taille} viewBox="0 0 48 48" aria-hidden="true" class="marque-svg">
    <circle class="marque-disque" cx="24" cy="24" r="22" />
    <ellipse class="marque-corps" cx="24" cy="26" rx="10" ry="12" />
    <path class="marque-rayure" d="M14 22h20M14 30h20" />
    <path class="marque-aile" d="M16 16c-4-5-10-4-10 0s5 6 9 3M32 16c4-5 10-4 10 0s-5 6-9 3" />
    <circle class="marque-oeil" cx="20" cy="14" r="1.8" />
    <circle class="marque-oeil" cx="28" cy="14" r="1.8" />
  </svg>
  <span class="marque-nom">Snack-bar <b>Apis</b></span>
</span>

<style>
  .marque {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
  }
  .marque-svg { flex: none; }

  /* palette : disque accent, corps crème, rayures accent foncé, ailes translucides */
  .marque-disque { fill: var(--accent); }
  .marque-corps { fill: var(--sur-accent); }
  .marque-rayure { stroke: var(--accent-fonce); stroke-width: 4; fill: none; }
  .marque-aile {
    fill: color-mix(in srgb, var(--sur-accent) 70%, transparent);
    stroke: var(--accent-fonce);
    stroke-width: 1.5;
  }
  .marque-oeil { fill: var(--accent-fonce); }

  .marque-nom { font-size: var(--t-md); white-space: nowrap; }
  .marque-nom b { color: var(--accent); }
</style>

