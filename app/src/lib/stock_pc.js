/* I8 · PC caisse : stock, entrées, inventaire, pertes, ardoises, prix (pures).
   Miroir UI de core/src/stock.rs + ardoise.rs + PRX-1.
   STK-2 : stock = somme des mouvements (jamais de modif directe).
   STK-3 : vente à stock négatif autorisée, produits négatifs en tête.
   STK-4 [M7-Q1-A] : entrée « à valider » hors disponible ; même personne
          ne saisit pas puis ne valide pas la même entrée ; rejet = mouvement
          inverse seulement si elle était déjà validée.
   STK-5 : inventaire quotidien, écart en quantités, motif obligatoire.
   STK-6 : pertes affichées séparément, valorisation coût → propriétaire (R3).
   ARD-1/5 : plafond (gérant ou proprio), alertes dépassement, remboursement.
   PRX-1 : prix ≤ coût refusé, message SANS révéler le coût.
   Le back reste l'autorité ; ici on produit les lignes d'affichage. */

// ---------- Stock (STK-2, STK-3) ----------

export function stockDisponible(mouvements, produit) {
  return mouvements.filter((m) => m.produit === produit).reduce((s, m) => s + m.quantite, 0);
}

export function triStock(lignes) {
  // négatifs en tête, puis ordre alphabétique stable
  return [...lignes].sort((a, b) => {
    const na = a.quantite < 0 ? 0 : 1;
    const nb = b.quantite < 0 ? 0 : 1;
    return na - nb || a.produit.localeCompare(b.produit);
  });
}

export function produitsNegatifs(mouvements) {
  const tot = new Map();
  for (const m of mouvements) tot.set(m.produit, (tot.get(m.produit) ?? 0) + m.quantite);
  return [...tot].filter(([, s]) => s < 0).map(([p]) => p);
}

// ---------- Entrées (STK-4, D19) ----------

export function saisirEntree(lignes) {
  // une entrée ne contient QUE des quantités — aucun champ prix
  if (lignes.length === 0) return { ok: false, raison: "Au moins une ligne requise" };
  if (lignes.some((l) => !Number.isInteger(l.quantite) || l.quantite <= 0))
    return { ok: false, raison: "Quantités entières strictement positives uniquement" };
  return { ok: true, lignes: lignes.map((l) => ({ produit: l.produit, quantite: l.quantite })) };
}

export function validerEntree(saisiePar, valideePar, peutSaisir, lignes) {
  if (!peutSaisir) return { ok: false, raison: "Indicateur « peut saisir les entrées » non activé" };
  if (saisiePar === valideePar) return { ok: false, raison: "Séparation obligatoire : la saisie et la validation doivent être faites par deux personnes différentes" };
  return { ok: true, mouvements: lignes.map((l) => ({ produit: l.produit, quantite: l.quantite, type: "achat" })) };
}

export function rejeterEntree(entree, valideePar) {
  // déjà validée (entrée en dispo) → mouvement inverse ; sinon rien à inverser
  if (!entree.validee) return { ok: true, mouvements: [], note: "Entrée jamais entrée en disponible : aucun mouvement inverse" };
  return { ok: true, mouvements: entree.lignes.map((l) => ({ produit: l.produit, quantite: -l.quantite, type: "rejet_entree" })) };
}

export function etatEntree(entree) {
  return entree.validee ? "validée" : "à valider";
}

export function disponiblesEtAttente(mouvements, attente) {
  return { disponible: mouvements, attente: attente }; // affichés séparément (STK-4)
}

// ---------- Inventaire (STK-5, O9) ----------

export function ecartInventaire(theorique, comptee) {
  if (!Number.isInteger(comptee)) return { ok: false, raison: "Comptage entier requis" };
  return { ok: true, ecart: comptee - theorique };
}

export function correctionInventaire(produit, theorique, comptee, motif) {
  const e = ecartInventaire(theorique, comptee);
  if (!e.ok) return e;
  if (e.ecart === 0) return { ok: true, mouvement: null }; // aucun écart, aucun mouvement
  if (!motif || motif.trim() === "") return { ok: false, raison: "Motif obligatoire pour tout écart d'inventaire" };
  return { ok: true, mouvement: { produit, quantite: e.ecart, type: "correction" } };
}

// ---------- Pertes (STK-6, O16) ----------

export const ORIGINES_PERTES = ["casse", "annulation après préparation", "offert", "écart d'inventaire négatif"];

export function regrouperPertes(pertes) {
  const groupes = {};
  for (const o of ORIGINES_PERTES) groupes[o] = [];
  for (const p of pertes) (groupes[p.origine] ??= []).push(p);
  return groupes; // affichées séparément
}

export function valorisationPertes(pertes, estProprietaire) {
  if (!estProprietaire) return null; // R3
  return pertes.reduce((s, p) => s + p.quantite * p.coutUnitaire, 0);
}

// ---------- Ardoises (ARD-1, ARD-5) ----------

export function depassementsPlafond(clients) {
  return clients.filter((c) => c.plafond !== null && c.solde > c.plafond);
}

export function fixerPlafond(client, plafond) {
  if (!Number.isInteger(plafond) || plafond < 0) return { ok: false, raison: "Plafond entier non négatif requis" };
  return { ok: true, client: { ...client, plafond } }; // gérant ou propriétaire (ARD-1) ; tracé SEC-3 côté back
}

export function rembourser(soldeDu, montant, mode) {
  if (montant <= 0 || soldeDu <= 0) return { ok: false, raison: "Remboursement invalide" };
  const nouveau = Math.max(soldeDu - montant, 0);
  return { ok: true, solde: nouveau, deltaEspeces: mode === "espèces" ? montant : 0 };
}

// ---------- Prix (PRX-1) ----------

export function modifierPrix(ancienPrix, nouveauPrix, cout, auteur) {
  if (!Number.isInteger(nouveauPrix) || nouveauPrix <= 0)
    return { ok: false, raison: "Prix entier strictement positif requis" };
  if (nouveauPrix <= cout)
    return { ok: false, raison: "Prix sous le seuil de rentabilité" }; // coût JAMAIS révélé
  return { ok: true, changement: { auteur, ancien: ancienPrix, nouveau: nouveauPrix, quand: "maintenant" } };
}
