/* I2 · État panier — fonctions pures (testables via node --test).
   Règles UI only : 1 appui = +1 ; prix figé à l'ajout ; retrait avec « Annuler ».
   Aucun blocage stock ici (STK-3 : le gère le back, pas l'UI). */

export function ajouter(panier, produit) {
  const exist = panier.lignes.find((l) => l.id === produit.id);
  if (exist) {
    return {
      ...panier,
      lignes: panier.lignes.map((l) => (l.id === produit.id ? { ...l, quantite: l.quantite + 1 } : l)),
    };
  }
  // Prix figé à l'ajout (PRX-3) : copie, jamais re-lu du catalogue
  return {
    ...panier,
    lignes: [...panier.lignes, { id: produit.id, nom: produit.nom, prix: produit.prix, quantite: 1 }],
  };
}

export function retirer(panier, id) {
  const ligne = panier.lignes.find((l) => l.id === id);
  if (!ligne) return { panier, annulable: null };
  const reste = ligne.quantite > 1
    ? panier.lignes.map((l) => (l.id === id ? { ...l, quantite: l.quantite - 1 } : l))
    : panier.lignes.filter((l) => l.id !== id);
  return { panier: { ...panier, lignes: reste }, annulable: { ligne, precedent: panier } };
}

export function annulerRetrait(restauration) {
  return restauration ? restauration.precedent : null;
}

export function nbArticles(panier) {
  return panier.lignes.reduce((n, l) => n + l.quantite, 0);
}

export function total(panier) {
  return panier.lignes.reduce((s, l) => s + l.quantite * l.prix, 0);
}

export function envoyerCuisine(panier) {
  if (panier.lignes.length === 0) return null;
  return {
    lignes: panier.lignes.map((l) => ({ ...l, statutCuisine: "envoyé" })),
    total: total(panier),
    panierVide: { lignes: [] },
  };
}
