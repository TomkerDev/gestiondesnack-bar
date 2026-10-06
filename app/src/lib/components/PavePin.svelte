<!-- I1 · Pavé PIN : touches 64 px, sans 0/9 exclus (grille complète), valeur remontée au parent. -->
<script>export let valeur = ""; export let longueurMax = 8;</script>
<div class="pave-pin" role="group" aria-label="Saisie du code">
  {#each ["1","2","3","4","5","6","7","8","9","0"] as t}
    <button type="button" on:click={() => valeur = (valeur + t).slice(0, longueurMax)} aria-label={"Touche " + t}>{t}</button>
  {/each}
  <button type="button" on:click={() => valeur = valeur.slice(0, -1)} aria-label="Effacer">⌫</button>
</div>
