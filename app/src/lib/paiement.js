/* I4 · Règles de paiement (pures, testables via node --test).
   Miroir UI des réservations M2/M3 : le back Rust reste l'autorité.
   - PAI-1 : mode de règlement connu uniquement.
   - PAI-2 : total couvert exactement (espèces + mobile multiples + ardoise TOTALE seule).
   - PAI-3 : monnaie calculée, reçu insuffisant → refus.
   - PAI-6 : pourboire hors total.
   - ARD-2 : plafond ardoise ; dépassement → refus + déblocage R1 (pas hors ligne).
   - ARD-6 : hors ligne, ardoise sur copie locale, pas de déblocage. */

export const MODES = ["especes", "mobile"];
export const OPERATEURS = ["orange", "mobicash", "wave"];

export function resteAPayer(total, reglements, ardoise = 0) {
  const paye = reglements.reduce((s, r) => s + r.montant, 0) + ardoise;
  return total - paye;
}

export function ajouterReglement(reglements, reglement) {
  if (!MODES.includes(reglement.mode)) return { erreur: "Mode de règlement inconnu" };
  if (!Number.isInteger(reglement.montant) || reglement.montant <= 0)
    return { erreur: "Montant entier strictement positif requis" };
  if (reglement.mode === "mobile" && (!reglement.operateur || !reglement.reference))
    return { erreur: "Opérateur et référence obligatoires" };
  return { reglements: [...reglements, { ...reglement }], erreur: null };
}

export function monnaieRendue(recu, totalDu) {
  if (recu < totalDu) return { erreur: "Reçu insuffisant", rendu: null };
  return { erreur: null, rendu: recu - totalDu };
}

export function peutValider(total, reglements) {
  return resteAPayer(total, reglements) === 0;
}

export function totalAvecPourboire(total, pourboire) {
  return { total: total, pourboire: pourboire, due: total }; // pourboire hors total (PAI-6)
}

export function payerArdoise(total, solde, plafond, { enLigne = true, autorise = false } = {}) {
  const attenduApres = solde + total;
  if (attenduApres > plafond) {
    if (autorise) return { ok: true, attenduApres, reste: 0 };
    return { ok: false, reste: total, demandeR1: !enLigne ? false : true,
      raison: enLigne ? "Plafond dépassé — demander un déblocage" : "Plafond dépassé — déblocage impossible hors ligne (dernière copie des soldes)" };
  }
  return { ok: true, attenduApres, reste: 0 };
}

export function ardoiseSeule(reglements) {
  return reglements.every((r) => r.mode !== "especes" && r.mode !== "mobile") || reglements.length === 0;
}
