/* I6 · Ma caisse — réservations UI de CAI-2 à CAI-5 et PAI-6 (pures).
   Formule CAI-2 (spec v1.2, Q4-A) :
     espèces attendues = fond de caisse
       + espèces encaissées (hors mobile money)
       - remboursements ardoise en espèces
       + pourboires reçus en espèces
       + entrées de caisse
       - sorties de caisse
   L'entier est i64 ; le back reste l'autorité. */

export function especesAttendues(r) {
  return r.fondCaisse
    + r.especesEncaissees
    - r.remboursementsArdoise
    + r.pourboires
    + r.entreesCaisse
    - r.sortiesCaisse;
}

export function ecart(compte, attendu) {
  return compte - attendu; // < 0 manque, > 0 excédent, 0 parfait
}

export function motifObligatoire(ecartValeur) {
  return ecartValeur !== 0; // CAI-4 : écart non nul → motif + commentaire obligatoires
}

export function cloturerServeur({ compte, attendu, motif, commentaire, dejaCloture }) {
  if (dejaCloture) return { ok: false, raison: "Déjà clôturée — journée figée (R5)" };
  const e = ecart(compte, attendu);
  if (motifObligatoire(e) && (!motif || !commentaire))
    return { ok: false, raison: "Écart " + e + " : motif et commentaire obligatoires", ecart: e };
  return { ok: true, ecart: e, etat: "en attente du gérant" };
}

export const MOTIFS_SORTIE = ["achat urgence", "rangement", "Autre"];

export function saisirSortie(sorties, { montant, motif, commentaire }) {
  if (!Number.isInteger(montant) || montant <= 0)
    return { erreur: "Montant entier strictement positif requis" };
  if (!MOTIFS_SORTIE.includes(motif)) return { erreur: "Motif hors liste" };
  if (motif === "Autre" && !commentaire) return { erreur: "« Autre » exige un commentaire" };
  return { sorties: [...sorties, { montant, motif, commentaire, statut: "en attente de validation du gérant" }], erreur: null };
}

export function ventesPossibles(apresCloture) {
  return !apresCloture; // CAI-3 : après clôture, plus aucune vente pour ce serveur ce jour
}
