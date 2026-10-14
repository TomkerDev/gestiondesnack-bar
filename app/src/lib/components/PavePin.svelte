<!-- I1 · Clavier PIN : 3 colonnes, touches arrondies ≥ 56 px de haut,
     indicateur de 4 points, grille complète (aucun 0/9 exclu).
     Valeur remontée au parent via bind:valeur. Aucune logique de sécurité ici. -->
<script>
  export let valeur = "";
  export let longueurMax = 8;
  export let attendu = 4;      // nombre de points de l'indicateur
  $: points = Array.from({ length: Math.max(attendu, valeur.length) }, (_, i) => i < valeur.length);
</script>

<div class="pave-pin" role="group" aria-label="Saisie du code">
  <!-- indicateur : un point rempli par chiffre saisi -->
  <div class="pave-indicateur" aria-hidden="true">
    {#each points as rempli}
      <span class="pave-point" class:pave-point--plein={rempli}></span>
    {/each}
  </div>

  <div class="pave-touches">
    {#each ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"] as t}
      <button type="button" class="pave-cle zone-tactile"
              on:click={() => (valeur = (valeur + t).slice(0, longueurMax))}
              aria-label={"Touche " + t}>{t}</button>
    {/each}
    <button type="button" class="pave-cle pave-cle--effacer zone-tactile"
            on:click={() => (valeur = valeur.slice(0, -1))} aria-label="Effacer">⌫</button>
  </div>

  <p class="pave-compteur" role="status">
    {valeur.length} / {longueurMax} chiffre{valeur.length > 1 ? "s" : ""}
  </p>
</div>

<style>
  .pave-pin {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--sp-3);
    width: 100%;
    max-width: 320px;
  }

  .pave-indicateur {
    display: flex;
    gap: var(--sp-2);
    justify-content: center;
  }
  .pave-point {
    width: 12px;
    height: 12px;
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-pastille);
    background: transparent;
    transition: background var(--dur) var(--ease), border-color var(--dur) var(--ease);
  }
  .pave-point--plein {
    background: var(--accent);
    border-color: var(--accent);
  }

  /* 3 colonnes, touches ≥ 56 px (jeton 64 px) arrondies */
  .pave-touches {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--sp-2);
    width: 100%;
  }
  .pave-cle {
    min-height: var(--h-cle-pin);
    min-width: var(--tactile);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--surface);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-bouton);
    color: var(--texte);
    font-size: var(--t-lg);
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    transition: background var(--dur) var(--ease), border-color var(--dur) var(--ease),
                transform var(--dur) var(--ease);
  }
  .pave-cle:hover { border-color: var(--accent); }
  .pave-cle:active { transform: scale(var(--echelle-active)); background: var(--surface-haute); }

  .pave-cle--effacer { color: var(--texte-secondaire); }

  .pave-compteur {
    margin: 0;
    font-size: var(--t-sm);
    color: var(--texte-secondaire);
    font-variant-numeric: tabular-nums;
  }
</style>
