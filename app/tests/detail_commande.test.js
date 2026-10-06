import { test } from "node:test";
import assert from "node:assert/strict";
import {
  annulerPlat, actions, imprimerAddition, convertirEnTable,
  transfererCommande, groupParTable, estPayee,
} from "../src/lib/detail_commande.js";

const cmd = (statut = "ouverte", destination = "table", statutCuisine = "envoyé") => ({
  statut, destination, table: "4", serveur: "ibou",
  lignes: [{ id: "l1", nom: "Bière", statutCuisine }, { id: "l2", nom: "Poulet", statutCuisine: "prêt" }],
  historique: [],
});

test("CUI-4 annulation avant préparation (« envoyé ») : serveur OK", () => {
  assert.equal(annulerPlat(cmd(), "l1").ok, true);
});

test("CUI-4 annulation après passage « en préparation » : demande R1", () => {
  const r = annulerPlat(cmd("ouverte", "table", "en préparation"), "l1");
  assert.equal(r.ok, false);
  assert.equal(r.demandeR1, true);
  assert.equal(annulerPlat(cmd(), "l1", { autorise: true }).ok, true);
});

test("CMD-5 ligne introuvable refusée", () => {
  assert.equal(annulerPlat(cmd(), "zzz").ok, false);
});

test("R4 commande payée : aucune modification, seulement correction", () => {
  const c = cmd("payée");
  assert.equal(estPayee(c), true);
  assert.equal(annulerPlat(c, "l1").ok, false);
  const a = actions(c);
  assert.ok(a.filter((x) => x.cle !== "correction" && x.cle !== "imprimer").every((x) => !x.actif));
  assert.ok(a.some((x) => x.cle === "correction" && x.actif));
});

test("OFF-2 hors ligne : actions indisponibles visibles avec raison", () => {
  const a = actions(cmd(), { enLigne: false });
  const annul = a.find((x) => x.cle === "annuler_plat");
  assert.equal(annul.actif, false);
  assert.match(annul.raisonInactif, /Hors ligne/);
  assert.ok(a.length >= 6); // rien n'est caché
  assert.equal(a.find((x) => x.cle === "imprimer").actif, true); // impression reste possible
});

test("OFF-2 annulation plat hors ligne refusée (CUI-5)", () => {
  assert.equal(annulerPlat(cmd(), "l1", { enLigne: false }).ok, false);
});

test("CMD-3 comptoir → table ; déjà table refusé", () => {
  const c = convertirEnTable(cmd("ouverte", "comptoir"), "7");
  assert.equal(c.destination, "table");
  assert.equal(c.table, "7");
  assert.equal(convertirEnTable(cmd("ouverte", "table"), "7").erreur, "Déjà une table");
});

test("CMD-4 transfert à collègue avec historique", () => {
  const c = transfererCommande(cmd(), "awa");
  assert.equal(c.serveur, "awa");
  assert.deepEqual(c.historique, ["transférée à awa"]);
});

test("CMD-7 impression : DUPLICATA si déjà imprimée", () => {
  assert.equal(imprimerAddition(false).mention, "ORIGINAL");
  assert.equal(imprimerAddition(true).mention, "DUPLICATA");
  assert.ok(actions(cmd(), { dejaImprime: true }).some((a) => a.libelle.includes("DUPLICATA")));
});

test("CMD-2 groupement par table + comptoir", () => {
  const g = groupParTable([cmd("ouverte", "table"), cmd("ouverte", "comptoir"), cmd("ouverte", "table")]);
  assert.equal(g["Table 4"].length, 2);
  assert.equal(g["Comptoir"].length, 1);
});
