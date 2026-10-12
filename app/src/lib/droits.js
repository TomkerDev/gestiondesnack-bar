/* Scopes par rôle — miroir JS de core/src/securite.rs (matrice §3, spec v1.2).
   Pur JS, testé en node. Rôles : "serveur" | "gerant" | "proprietaire".
   - Serveur : vendre/encaisser (commande, commandes, paiement, cuisine lecture,
     ma-caisse lecture) + retraits/annulations avant préparation.
   - Gérant : tout sauf coûts/marges (pas de /pc/stock volet coûts).
   - Propriétaire : tout, y compris coûts/marges sur /pc/stock.
   Cuisine : lecture partagée (I5 affiche les bons) ; seul le gérant/proprio
   avance les bons (CUI-3 : arbitrage central, pas le serveur seul). */

export const ROUTES = {
  "/commande": "VendreEncaisser",
  "/commandes": "VendreEncaisser",
  "/paiement": "VendreEncaisser",
  "/cuisine": "CuisineLecture",
  "/ma-caisse": "VendreEncaisser",
  "/pc": "Gerant",
  "/pc/stock": "Gerant",
  "/galerie": "Public",
  "/connexion": "Public",
  "/": "Public"
};

// Droits fins par action métier (miroir de securite::autorise + CUI-3) :
// le serveur lit la cuisine mais n'avance pas les bons ; le gérant avance
// mais ne voit pas les coûts/marges (R3).
const DROITS = {
  serveur: new Set(["VendreEncaisser", "RetirerBoissonNonPayee", "AnnulerAvantPrepa",
                    "CuisineLecture", "Public"]),
  gerant: new Set(["VendreEncaisser", "RetirerBoissonNonPayee", "AnnulerAvantPrepa",
                   "AnnulerApresPrepa", "RemiseOffert", "DeblocagePlafond", "Correction",
                   "FixerPrixPlafond", "SaisirEntree", "ValiderEntree",
                   "InventaireFondForcageClotureJournee", "Gerant",
                   "CuisineLecture", "CuisineAvancer", "Public"]),
  proprietaire: new Set(["VendreEncaisser", "RetirerBoissonNonPayee", "AnnulerAvantPrepa",
                   "AnnulerApresPrepa", "RemiseOffert", "DeblocagePlafond", "Correction",
                   "FixerPrixPlafond", "SaisirEntree", "ValiderEntree",
                   "InventaireFondForcageClotureJournee", "VoirCoutsMarges", "Gerant",
                   "CuisineLecture", "CuisineAvancer", "Public"])
};

export function autorise(role, action) {
  const droits = DROITS[role];
  if (!droits) return { ok: false, raison: "Rôle inconnu : " + role };
  if (!droits.has(action)) return { ok: false, raison: "Droit insuffisant (rôle " + role + ")" };
  return { ok: true };
}

// Garde de route : le préfixe le plus long de ROUTES décide.
// Retourne { ok } ou { ok:false, redirection } pour les pages.
export function gardeRoute(role, chemin) {
  if (!role) return { ok: false, redirection: "/connexion" };
  let cle = null;
  for (const r of Object.keys(ROUTES)) {
    if (chemin === r || (r !== "/" && chemin.startsWith(r + "/")) || (r !== "/" && chemin === r)) {
      if (cle === null || r.length > cle.length) cle = r;
    }
  }
  const action = ROUTES[cle ?? "/"] ?? "Public";
  const d = autorise(role, action);
  if (!d.ok) return { ok: false, redirection: "/connexion", raison: d.raison };
  return { ok: true };
}

// Navigation visible selon le rôle (le layout filtre avec ça).
// Les 7 href métier restent listés ici (test INT_layout_nav).
const NAVIGATION = [
  ["/commande", "Prise de commande"], ["/commandes", "Mes commandes"],
  ["/cuisine", "Cuisine"], ["/paiement", "Paiement"],
  ["/ma-caisse", "Ma caisse"], ["/pc", "PC caisse"], ["/pc/stock", "Stock & prix"]
];
export function liensPour(role) {
  if (!role) return [];
  return NAVIGATION.filter(([href]) => gardeRoute(role, href).ok);
}
