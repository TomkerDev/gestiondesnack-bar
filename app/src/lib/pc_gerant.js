/* I7 · PC caisse du gérant (pures).
   CAI-1 : ouverture = fond de caisse par serveur ; journée clôturable seulement
           quand toutes les caisses sont closes.
   CAI-5 : clôture forcée = R1 obligatoire + motif.
   CAI-6 : rapprochement, litige signalé.
   R3 : le gérant ne voit JAMAIS coût/marge (prix d'achat) — le propriétaire si.
   Le back reste l'autorité ; ici on produit les lignes d'affichage. */

export function alertes(a) {
  const out = [];
  if (a.stockNegatif) out.push("Stock négatif");
  if (a.entreesAValider > 0) out.push(a.entreesAValider + " entrée(s) de stock à valider");
  if (a.ardoisesAuPlafond > 0) out.push(a.ardoisesAuPlafond + " ardoise(s) au-dessus du plafond");
  if (a.ecartsCaisse) out.push("Écart(s) de caisse à traiter");
  return out;
}

export function peutCloturerJournee(journee) {
  if (!journee) return { ok: false, raison: "Aucune journée" };
  if (journee.etat === "clôturée") return { ok: false, raison: "Journée déjà clôturée (R5)" };
  const ouvertes = journee.caisses.filter((c) => c.etat !== "close");
  if (ouvertes.length > 0)
    return { ok: false, raison: "Clôture impossible : " + ouvertes.length + " caisse(s) encore ouverte(s)", caissesOuvertes: ouvertes.map((c) => c.serveur) };
  return { ok: true, raison: "" };
}

export function forcerCloture(caisse, { jeton, motif, commentaire }) {
  if (caisse.etat === "close") return { ok: false, raison: "Déjà close" };
  if (!jeton) return { ok: false, raison: "R1 obligatoire pour forcer une clôture" };
  if (!motif) return { ok: false, raison: "Motif obligatoire" };
  if (motif === "Autre" && !commentaire) return { ok: false, raison: "« Autre » exige un commentaire" };
  return { ok: true, caisse: { ...caisse, etat: "close", forcee: true, motif } };
}

export const COLONNES_VALEURS = ["cout", "marge"]; // colonnes proprietaire uniquement

export function colonnes(role) {
  return role === "proprietaire"
    ? ["serveur", "total", "ecart", ...COLONNES_VALEURS]
    : ["serveur", "total", "ecart"]; // gérant : mêmes écrans, sans ces colonnes (R3)
}

export function filtreValeurs(role) {
  return role !== "proprietaire";
}

export function ouvrirJournee(journee, { fondParServeur }) {
  if (journee && journee.etat === "ouverte") return { ok: false, raison: "Journée déjà ouverte (CAI-1)" };
  if (!fondParServeur || fondParServeur.length === 0 ||
      fondParServeur.some((f) => !Number.isInteger(f.fond) || f.fond < 0))
    return { ok: false, raison: "Fond de caisse entier non négatif par serveur requis" };
  return { ok: true, journee: { etat: "ouverte", caisses: fondParServeur.map((f) => ({ serveur: f.serveur, etat: "ouverte", fond: f.fond })) } };
}
