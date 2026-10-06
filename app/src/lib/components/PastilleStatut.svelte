<!-- I1 · Pastille statut : couleur + texte (jamais couleur seule). Statuts cuisine CUI-3. -->
<script>export let statut;</script>
<span class="pastille zone-tactile" data-statut={statut}>{statut}</span>
<style>.pastille[data-statut="pret"]{background:var(--succes)}.pastille[data-statut="alerte"]{background:var(--alerte)}</style>
