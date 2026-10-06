/* I5 · File cuisine : transitions de statut (pures).
   CUI-3 : seul enchaînement envoyé → en préparation → prêt (pas de saut, cf. M4).
   CUI-4 : annulation reçue → carte rouge « ANNULÉ » + signal sonore.
   L'horodatage vient du PC (back) ; ici on ne produit que l'état local. */

export const COLONNES = ["envoyé", "en préparation", "prêt"];

export function avancer(bon) {
  if (bon.statut === "annulé") return { ...bon, erreur: "Bon annulé — statut figé" };
  const i = COLONNES.indexOf(bon.statut);
  if (i === -1) return { ...bon, erreur: "Statut inconnu" };
  if (i === COLONNES.length - 1) return { ...bon, erreur: "Déjà prêt" };
  return { ...bon, statut: COLONNES[i + 1] };
}

export function recevoirAnnulation(bon) {
  return { ...bon, statut: "annulé", signal: "annulation" };
}

export function nouveauBon(bon) {
  return { ...bon, statut: bon.statut || "envoyé", signal: "nouveau" };
}

export function trier(bons) {
  const ordre = { "envoyé": 0, "en préparation": 1, "prêt": 2, "annulé": 3 };
  return [...bons].sort((a, b) => ordre[a.statut] - ordre[b.statut] || a.heure.localeCompare(b.heure));
}

export function messageHorsLigne(enLigne, dernierSync) {
  if (enLigne) return "File en temps réel";
  return "Hors ligne — file potentiellement périmée (dernière synchro " + dernierSync + ")";
}
