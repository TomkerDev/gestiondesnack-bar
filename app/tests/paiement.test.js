import { test } from "node:test";
import assert from "node:assert/strict";
import {
  ajouterReglement, monnaieRendue, peutValider, resteAPayer,
  totalAvecPourboire, payerArdoise, ardoiseSeule,
} from "../src/lib/paiement.js";

test("PAI-1 mode de règlement inconnu refusé", () => {
  assert.match(ajouterReglement([], { mode: "cheque", montant: 100 }).erreur, /inconnu/);
});

test("PAI-2 montant négatif ou décimal refusé", () => {
  assert.ok(ajouterReglement([], { mode: "especes", montant: -5 }).erreur);
  assert.ok(ajouterReglement([], { mode: "especes", montant: 10.5 }).erreur);
});

test("PAI-2 mix espèces + mobile couvre le total", () => {
  let r = ajouterReglement([], { mode: "especes", montant: 3000 });
  r = ajouterReglement(r.reglements, { mode: "mobile", montant: 4500, operateur: "orange", reference: "TX1" });
  assert.equal(r.erreur, null);
  assert.ok(peutValider(7500, r.reglements));
  assert.equal(resteAPayer(7500, r.reglements), 0);
});

test("PAI-2 mobile sans opérateur/référence refusé", () => {
  assert.match(ajouterReglement([], { mode: "mobile", montant: 100, reference: "TX" }).erreur, /Opérateur/);
  assert.match(ajouterReglement([], { mode: "mobile", montant: 100, operateur: "orange" }).erreur, /référence/i);
});

test("PAI-2 valide seulement à reste nul", () => {
  assert.equal(peutValider(7500, [{ mode: "especes", montant: 7000 }]), false);
  assert.equal(resteAPayer(7500, [{ mode: "especes", montant: 7000 }]), 500);
});

test("PAI-3 monnaie calculée, reçu insuffisant refusé", () => {
  assert.deepEqual(monnaieRendue(5000, 4500), { erreur: null, rendu: 500 });
  assert.match(monnaieRendue(4000, 4500).erreur, /insuffisant/);
});

test("PAI-6 pourboire hors total", () => {
  const t = totalAvecPourboire(10000, 500);
  assert.equal(t.due, 10000);
  assert.equal(t.pourboire, 500);
});

test("PAI-2 ardoise = seule couverture, mix ardoise+règlements refusé", () => {
  assert.ok(ardoiseSeule([]));
  assert.ok(ardoiseSeule([{ mode: "ardoise" }]));
  assert.equal(ardoiseSeule([{ mode: "ardoise" }, { mode: "especes", montant: 100 }]), false);
});

test("ARD-2 plafond dépassé → refus + demande R1", () => {
  const r = payerArdoise(2000, 4500, 5000);
  assert.equal(r.ok, false);
  assert.equal(r.demandeR1, true);
  assert.match(r.raison, /déblocage/);
  assert.equal(payerArdoise(2000, 4500, 5000, { autorise: true }).ok, true);
});

test("ARD-2 plafond atteint exactement accepté", () => {
  assert.equal(payerArdoise(500, 4500, 5000).ok, true);
});

test("I4-scénario 3 700 : 2 000 espèces + 1 700 mobile + pourboire 300", () => {
  let r = ajouterReglement([], { mode: "especes", montant: 2000 });
  r = ajouterReglement(r.reglements, { mode: "mobile", montant: 1700, operateur: "orange", reference: "TX99" });
  assert.equal(r.erreur, null);
  assert.ok(peutValider(3700, r.reglements));
  const t = totalAvecPourboire(3700, 300);
  assert.equal(t.due, 3700); // le pourboire ne change pas le dû
});

test("I4-scénario ardoise refusée au-delà du plafond, puis débloquée par gérant", () => {
  const refus = payerArdoise(3000, 4500, 5000);
  assert.equal(refus.ok, false);
  assert.match(refus.raison, /déblocage/);
  const okDeblocage = payerArdoise(3000, 4500, 5000, { autorise: true });
  assert.equal(okDeblocage.ok, true);
});

test("ARD-6 hors ligne : plafond refusé, aucun déblocage", () => {
  const r = payerArdoise(2000, 4500, 5000, { enLigne: false });
  assert.equal(r.ok, false);
  assert.equal(r.demandeR1, false);
  assert.match(r.raison, /hors ligne/);
});

