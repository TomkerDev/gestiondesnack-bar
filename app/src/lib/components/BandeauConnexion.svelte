<!-- I1 · Bandeau de connexion : « En ligne » en pastille verte discrète ;
     connexion perdue → bandeau orange calme avec message clair (OFF-1).
     Toujours visible, jamais bloquant : les ventes continuent hors ligne. -->
<script>
  export let enLigne = true;
  export let message = "";   // raison optionnelle fournie par le parent
</script>

<div class="bandeau zone-tactile" role="status" aria-live="polite" data-en-ligne={enLigne}>
  {#if enLigne}
    <span class="bandeau-en-ligne">
      <span class="bandeau-point" aria-hidden="true"></span>
      En ligne
    </span>
  {:else}
    <span class="bandeau-perdu">
      <span class="bandeau-cloche" aria-hidden="true">!</span>
      <span>
        <b>Connexion perdue</b> — les ventes continuent, la synchronisation suivra au retour du réseau.
        {#if message}<span class="bandeau-detail">{message}</span>{/if}
      </span>
    </span>
  {/if}
</div>

<style>
  .bandeau {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    min-height: var(--tactile);
    padding: var(--sp-2) var(--sp-3);
    border-radius: var(--rayon-bouton);
    border: var(--bordure-large) solid transparent;
    font-size: var(--t-sm);
    transition: background var(--dur-long) var(--ease), border-color var(--dur-long) var(--ease);
  }

  /* en ligne : pastille verte discrète, pas de bandeau plein */
  .bandeau-en-ligne {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
    color: var(--texte-secondaire);
    font-weight: 600;
  }
  .bandeau-point {
    width: 8px;
    height: 8px;
    border-radius: var(--rayon-pastille);
    background: var(--succes);
    flex: none;
  }

  /* connexion perdue : orange calme, message lisible — jamais rouge panique */
  .bandeau-perdu {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
    color: var(--texte);
  }
  .bandeau-cloche {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    flex: none;
    border-radius: var(--rayon-pastille);
    background: var(--alerte);
    color: var(--sur-accent);
    font-weight: 800;
    font-size: var(--t-xs);
  }
  .bandeau-detail { display: block; color: var(--texte-secondaire); }

  [data-en-ligne="false"] {
    background: color-mix(in srgb, var(--alerte) 14%, transparent);
    border-color: color-mix(in srgb, var(--alerte) 45%, transparent);
  }
</style>
