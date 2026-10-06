import { test } from "node:test";
import assert from "node:assert/strict";
import { alertes, peutCloturerJournee, forcerCloture, colonnes, filtreValeurs, ouvrirJournee } from "../src/lib/pc_gerant.js";

test("tableau de bord : les 4 familles d'alertes", () => {
  const a = alertes({ stockNegatif: true, entreesAValider: 3, ardoisesAuPlafond: 1, ecartsCaisse: true });
  assert.equal(a.length, 4);
  assert.match(a[1], /3 entrée/);
  assert.deepEqual(alertes({ stockNegatif: false, entreesAValider: 0, ardoisesAuPlafond: 0, ecartsCaisse: false }), []);
});

test("CAI-1 clôture de journée refusée tant qu'une caisse est ouverte", () => {
  const j = { etat: "ouverte", caisses: [{ serveur: "ibou", etat: "close" }, { serveur: "awa", etat: "ouverte" }] };
  const r = peutCloturerJournee(j);
  assert.equal(r.ok, false);
  assert.match(r.raison, /encore ouverte/);
  assert.deepEqual(r.caissesOuvertes, ["awa"]);
});

test("CAI-1 toutes closes → clôture autorisée ; R5 si déjà clôturée", () => {
  const j = { etat: "ouverte", caisses: [{ serveur: "ibou", etat: "close" }, { serveur: "awa", etat: "close" }] };
  assert.equal(peutCloturerJournee(j).ok, true);
  assert.match(peutCloturerJournee({ etat: "clôturée", caisses: [] }).raison, /R5/);
});

test("CAI-5 clôture forcée : R1 + motif obligatoires", () => {
  const c = { serveur: "ibou", etat: "ouverte" };
  assert.match(forcerCloture(c, { motif: "vol" }).raison, /R1/);
  assert.match(forcerCloture(c, { jeton: "j1" }).raison, /Motif/);
  assert.match(forcerCloture(c, { jeton: "j1", motif: "Autre" }).raison, /commentaire/);
  const ok = forcerCloture(c, { jeton: "j1", motif: "oubli de clôture", commentaire: "serveur parti" });
  assert.equal(ok.ok, true);
  assert.equal(ok.caisse.etat, "close");
  assert.equal(ok.caisse.forcee, true);
  assert.match(forcerCloture({ serveur: "x", etat: "close" }, { jeton: "j", motif: "m" }).raison, /Déjà close/);
});

test("R3 : gérant sans prix d'achat, propriétaire avec", () => {
  assert.ok(colonnes("proprietaire").includes("marge"));
  assert.ok(colonnes("proprietaire").includes("cout"));
  const g = colonnes("gerant");
  assert.ok(!g.includes("marge") && !g.includes("cout"));
  assert.equal(filtreValeurs("gerant"), true);
  assert.equal(filtreValeurs("proprietaire"), false);
});

test("CAI-1 ouverture : fond entier non négatif par serveur", () => {
  assert.equal(ouvrirJournee(null, { fondParServeur: [{ serveur: "ibou", fond: 10000 }] }).ok, true);
  assert.match(ouvrirJournee(null, { fondParServeur: [{ serveur: "ibou", fond: -1 }] }).raison, /entier/);
  assert.match(ouvrirJournee(null, { fondParServeur: [] }).raison, /Fond/);
  const deja = ouvrirJournee({ etat: "ouverte" }, { fondParServeur: [{ serveur: "ibou", fond: 1 }] });
  assert.match(deja.raison, /CAI-1/);
});
