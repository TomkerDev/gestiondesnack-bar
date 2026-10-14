<!-- I1 · Bouton : action tactile. Variantes plein (principale), contour, danger.
     États : actif, désactivé, chargement. Aucune couleur en dur : jetons uniquement.
     Zéro métier — le parent reçoit l'événement « click ». -->
<script>
  export let libelle = "";
  export let variante = "plein";      // "plein" | "contour" | "danger"
  export let desactive = false;
  export let chargement = false;
  export let large = false;           // pleine largeur (actions principales d'écran)
  $: occupe = desactive || chargement;
</script>

<button
  type="button"
  class="bouton zone-tactile"
  class:bouton--plein={variante === "plein"}
  class:bouton--contour={variante === "contour"}
  class:bouton--danger={variante === "danger"}
  class:bouton--large={large}
  class:bouton--chargement={chargement}
  disabled={occupe}
  aria-label={libelle}
  aria-busy={chargement ? "true" : undefined}
  on:click
>
  {#if chargement}<span class="bouton-chargeur" aria-hidden="true"></span>{/if}
  <span class="bouton-libelle">{libelle}</span>
</button>

<style>
  .bouton {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--sp-2);
    min-height: var(--h-bouton);
    padding: 0 var(--sp-5);
    border: var(--bordure-large) solid transparent;
    border-radius: var(--rayon-bouton);
    font-size: var(--t-base);
    font-weight: 600;
    line-height: 1;
    cursor: pointer;
    transition: background var(--dur) var(--ease), border-color var(--dur) var(--ease),
                color var(--dur) var(--ease), transform var(--dur) var(--ease);
    user-select: none;
  }

  .bouton:active:not(:disabled) { transform: scale(var(--echelle-active)); }

  /* plein : action principale, fond accent, texte sur-accent */
  .bouton--plein { background: var(--accent); color: var(--sur-accent); }
  .bouton--plein:hover:not(:disabled) { background: var(--accent-fonce); }

  /* contour : action secondaire */
  .bouton--contour {
    background: transparent;
    border-color: var(--bordure);
    color: var(--texte);
  }
  .bouton--contour:hover:not(:disabled) {
    background: var(--surface-haute);
    border-color: var(--accent);
  }

  /* danger : destruction, jamais l'action principale d'un écran */
  .bouton--danger {
    background: transparent;
    border-color: var(--danger);
    color: var(--danger);
  }
  .bouton--danger:hover:not(:disabled) {
    background: color-mix(in srgb, var(--danger) 16%, transparent);
  }

  .bouton--large { width: 100%; }

  .bouton:disabled { opacity: 0.45; cursor: not-allowed; }

  /* chargement : on garde le libellé (jamais de bouton vide) + indicateur */
  .bouton--chargement { cursor: progress; }
  .bouton-chargeur {
    width: 16px;
    height: 16px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: bouton-tourne 700ms linear infinite;
    flex: none;
  }

  @keyframes bouton-tourne { to { transform: rotate(360deg); } }

  @media (prefers-reduced-motion: reduce) {
    .bouton-chargeur { animation-duration: 1.4s; }
  }
</style>
