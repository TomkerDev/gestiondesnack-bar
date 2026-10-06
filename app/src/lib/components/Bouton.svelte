<!-- I1 · Bouton : plein ou contour. Props: libelle, variante, desactive, aria. Zéro métier. -->
<script>export let libelle; export let variante = "plein"; export let desactive = false;</script>
<button class={variante === "plein" ? "bouton-plein zone-tactile" : "bouton-contour zone-tactile"} disabled={desactive} aria-label={libelle} on:click>{libelle}</button>
