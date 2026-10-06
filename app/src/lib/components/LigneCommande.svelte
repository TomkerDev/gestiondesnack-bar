<!-- I1 · Ligne commande : produit, quantité, prix figé, net. Actions par parent. -->
<script>export let nom; export let quantite; export let prix; export let net; export let statutCuisine = "";</script>
<li class="zone-tactile"><span>{nom}</span><span>× {quantite}</span><span>{prix}</span><strong>{net}</strong>{#if statutCuisine}<span>{statutCuisine}</span>{/if}</li>
