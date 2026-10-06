/* I3 · Règles d'affichage des commandes (pures, testables via node --test).
   Réservations M4 : annulation serveur seulement si « envoyé » ;
   après « en préparation » → besoin d'autorisation gérant (R1) ;
   hors ligne → annulation impossible (CUI-5), action visible mais expliquée (OFF-2).
   Commande payée → aucune modification, seulement « Demander une correction » (R4). */

export function estPayee(commande) {
  return commande.statut === "payée";
}

export function annulerPlat(commande, ligneId, { enLigne = true, autorise = false } = {}) {
  const ligne = commande.lignes.find((l) => l.id === ligneId);
  if (!ligne) return { ok: false, raison: "Ligne introuvable" };
  if (estPayee(commande)) return { ok: false, raison: "Commande payée — demander une correction" };
  if (!enLigne) return { ok: false, raison: "Annulation impossible hors ligne (retour réseau requis)" };
  if (ligne.statutCuisine === "envoyé" || autorise) return { ok: true, raison: "" };
  if (ligne.statutCuisine === "en préparation")
    return { ok: false, raison: "En préparation — autorisation gérant requise", demandeR1: true };
  return { ok: false, raison: "Statut non annulable : " + ligne.statutCuisine };
}

export function actions(commande, { enLigne = true, dejaImprime = false } = {}) {
  const base = [
    { cle: "annuler_plat", libelle: "Annuler un plat", actif: enLigne && !estPayee(commande),
      raisonInactif: estPayee(commande) ? "Payée — demander une correction" : "Hors ligne : retour réseau requis" },
    { cle: "retirer_boisson", libelle: "Retirer une boisson", actif: enLigne && !estPayee(commande),
      raisonInactif: estPayee(commande) ? "Payée — demander une correction" : "Hors ligne : retour réseau requis" },
    { cle: "transferer_lignes", libelle: "Transférer des lignes", actif: enLigne && !estPayee(commande),
      raisonInactif: estPayee(commande) ? "Payée — demander une correction" : "Hors ligne : retour réseau requis" },
    { cle: "transferer_commande", libelle: "Transférer la commande", actif: enLigne && !estPayee(commande),
      raisonInactif: estPayee(commande) ? "Payée — demander une correction" : "Hors ligne : retour réseau requis" },
    { cle: "convertir_table", libelle: "Convertir comptoir → table", actif: enLigne && !estPayee(commande) && commande.destination === "comptoir",
      raisonInactif: estPayee(commande) ? "Payée — demander une correction" : commande.destination === "table" ? "Déjà une table" : "Hors ligne : retour réseau requis" },
    { cle: "imprimer", libelle: (dejaImprime ? "Imprimer le DUPLICATA" : "Imprimer l'addition"), actif: true, raisonInactif: "" },
  ];
  if (estPayee(commande)) base.push({ cle: "correction", libelle: "Demander une correction", actif: true, raisonInactif: "" });
  return base; // OFF-2 : les inactifs restent listés avec leur raison — jamais cachés
}

export function imprimerAddition(dejaImprime) {
  return { mention: dejaImprime ? "DUPLICATA" : "ORIGINAL" };
}

export function convertirEnTable(commande, table) {
  if (commande.destination !== "comptoir") return { ...commande, erreur: "Déjà une table" };
  return { ...commande, destination: "table", table };
}

export function transfererCommande(commande, nouveauServeur) {
  return { ...commande, serveur: nouveauServeur, historique: [...(commande.historique || []), "transférée à " + nouveauServeur] };
}

export function groupParTable(commandes) {
  const groupes = {};
  for (const c of commandes) {
    const cle = c.destination === "table" ? "Table " + c.table : "Comptoir";
    (groupes[cle] = groupes[cle] || []).push(c);
  }
  return groupes;
}
