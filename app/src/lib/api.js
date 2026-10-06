/* I-INT · Client d'intégration vers le PC caisse (serveur local HTTP).
   Le PC caisse est la référence de données (spec §6) ; ce client l'atteint depuis
   les appareils serveurs / cuisine / gérant.

   OFF-1 : hors ligne, l'appareil continue — prise/modification de commandes,
           encaissement (espèces, mobile money), vente sur ardoise → EN FILE
           d'attente, rejouée à la resynchronisation (OFF-3).
   OFF-2 : hors ligne, INTERDITES avec raison écrite — remises, offerts, R1,
           déblocages, annulations après envoi en cuisine, corrections, impression.
   Toute réponse renvoie { ok, ... } — jamais d'exception propagée à l'UI.
   fetch et horloge sont injectés : le module est pur et testable en node. */

export const INTERDIT_HORS_LIGNE = {
  remise: "Remise indisponible hors ligne (OFF-2)",
  offert: "Offert indisponible hors ligne (OFF-2)",
  r1: "Autorisation R1 indisponible hors ligne (OFF-2)",
  deblocage: "Déblocage de plafond indisponible hors ligne (OFF-2)",
  annulation_post_prepa: "Annulation après envoi en cuisine indisponible hors ligne (OFF-2)",
  correction: "Correction indisponible hors ligne (OFF-2)",
  impression: "Impression de l'addition indisponible hors ligne (OFF-2)"
};

// Actions autorisées hors ligne → mises en file (OFF-1)
export const FILE_HORS_LIGNE = ["prise_commande", "modification_commande", "encaissement_especes",
                                "encaissement_mobile", "vente_ardoise"];

export function creerClient({ base = "", fetchImpl, horloge, enLigne = true } = {}) {
  const fetcher = fetchImpl ?? ((...a) => globalThis.fetch(...a));
  const now = horloge ?? (() => new Date().toISOString());
  const etat = { enLigne, file: [], abonnes: [] };

  function emitre(e) { for (const ab of etat.abonnes) ab(e); }

  async function reseau(chemin, { methode = "GET", corps } = {}) {
    try {
      const r = await fetcher(base + chemin, {
        method: methode,
        headers: { "Content-Type": "application/json" },
        body: corps === undefined ? undefined : JSON.stringify(corps)
      });
      const donnees = await r.json().catch(() => ({}));
      if (!r.ok) return { ok: false, raison: donnees.raison ?? ("Erreur serveur " + r.status) };
      return { ok: true, ...donnees };
    } catch {
      etat.enLigne = false; // perte détectée en pleine requête
      return { ok: false, raison: "Connexion perdue au PC caisse", horsLigne: true };
    }
  }

  function classer(action, chemin, methode, corps) {
    if (INTERDIT_HORS_LIGNE[action]) return { ok: false, raison: INTERDIT_HORS_LIGNE[action], horsLigne: true };
    if (!FILE_HORS_LIGNE.includes(action))
      return { ok: false, raison: "Action « " + action + " » non autorisée hors ligne (OFF-2)", horsLigne: true };
    etat.file.push({ action, chemin, methode, corps, quand: now() });
    emitre({ type: "en_file", action, taille: etat.file.length });
    return { ok: true, differe: true, horsLigne: true, tailleFile: etat.file.length };
  }

  async function demander(action, chemin, { methode = "GET", corps } = {}) {
    if (etat.enLigne) {
      const rep = await reseau(chemin, { methode, corps });
      if (rep.horsLigne) return classer(action, chemin, methode, corps); // bascule → file
      return rep;
    }
    return classer(action, chemin, methode, corps);
  }


  async function resynchroniser() {
    if (etat.file.length === 0) { etat.enLigne = true; return { ok: true, rejouees: 0, alertes: [] }; }
    etat.enLigne = true;
    const rejouees = []; const alertes = [];
    while (etat.file.length > 0) {
      const cmd = etat.file[0];
      const rep = await reseau(cmd.chemin, { methode: cmd.methode, corps: cmd.corps });
      if (!rep.ok) break; // le PC refuse encore → la file reste intacte (réessai suivant)
      etat.file.shift();
      rejouees.push(cmd.action);
      if (rep.alertes) alertes.push(...rep.alertes); // OFF-3 : alertes à la resynchro
    }
    emitre({ type: "resynchro", rejouees: rejouees.length, alertes });
    return { ok: true, rejouees: rejouees.length, alertes };
  }

  return {
    get etat() { return { enLigne: etat.enLigne, file: [...etat.file] }; },
    basculerLigne(v) { etat.enLigne = v; },
    abonner(fn) { etat.abonnes.push(fn); return () => { etat.abonnes = etat.abonnes.filter((f) => f !== fn); }; },
    resynchroniser,
    demander,
    // ---- Endpoints du serveur local du PC caisse ----
    identifier: (code) => demander("identification", "/api/session", { methode: "POST", corps: { code } }),
    catalogue: () => demander("lecture", "/api/produits"),
    creerCommande: (lignes) => demander("prise_commande", "/api/commandes", { methode: "POST", corps: { lignes } }),
    ajouterLignes: (id, lignes) => demander("modification_commande", "/api/commandes/" + id + "/lignes", { methode: "POST", corps: { lignes } }),
    envoyerCuisine: (id) => demander("modification_commande", "/api/commandes/" + id + "/envoyer", { methode: "POST" }),
    mesCommandes: (serveur) => demander("lecture", "/api/commandes?serveur=" + encodeURIComponent(serveur)),
    paiement: (id, reglements) => demander(
      reglements.some((r) => r.mode === "mobile") ? "encaissement_mobile" : "encaissement_especes",
      "/api/commandes/" + id + "/paiement", { methode: "POST", corps: { reglements } }),
    bonsCuisine: () => demander("lecture", "/api/cuisine/bons"),
    avancerBon: (id) => demander("modification_commande", "/api/cuisine/bons/" + id + "/avancer", { methode: "POST" }),
    etatCaisse: (serveur) => demander("lecture", "/api/caisse?serveur=" + encodeURIComponent(serveur)),
    sortieCaisse: (corps) => demander("encaissement_especes", "/api/caisse/sortie", { methode: "POST", corps }),
    cloturerCaisse: (corps) => demander("encaissement_especes", "/api/caisse/cloture", { methode: "POST", corps }),
    cloturerJournee: (corps) => demander("encaissement_especes", "/api/journee/cloturer", { methode: "POST", corps }),
    entreesStock: () => demander("lecture", "/api/stock/entrees"),
    validerEntree: (id) => demander("lecture", "/api/stock/entrees/" + id + "/valider", { methode: "POST" }),
    rejeterEntree: (id) => demander("lecture", "/api/stock/entrees/" + id + "/rejeter", { methode: "POST" }),
    inventaire: (corps) => demander("lecture", "/api/stock/inventaire", { methode: "POST", corps }),
    ardoises: () => demander("lecture", "/api/ardoises"),
    plafond: (id, plafond) => demander("lecture", "/api/ardoises/" + id + "/plafond", { methode: "POST", corps: { plafond } }),
    remboursement: (id, montant, mode) => demander("lecture", "/api/ardoises/" + id + "/remboursement", { methode: "POST", corps: { montant, mode } }),
    changerPrix: (id, prix) => demander("lecture", "/api/produits/" + id + "/prix", { methode: "POST", corps: { prix } })
  };
}

    // Client unique partagé par l'application (base = PC caisse)
    export const api = creerClient({ base: "" });

