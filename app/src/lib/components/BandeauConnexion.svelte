<!-- I1 · Bandeau connexion : En ligne / Hors ligne (OFF-1). Toujours visible, jamais bloquant. -->
<script>export let enLigne = true;</script>
<div class="bandeau zone-tactile" role="status">{enLigne ? "En ligne" : "Hors ligne — les ventes continuent, la synchro suivra"}</div>
