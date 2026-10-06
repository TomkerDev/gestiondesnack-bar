import { test } from "node:test";
import assert from "node:assert/strict";
import { avancer, recevoirAnnulation, nouveauBon, trier, messageHorsLigne, COLONNES } from "../src/lib/cuisine.js";

const bon = (statut = "envoyé") => ({ id: "b1", table: "4", statut, heure: "12:05" });

test("CUI-3 avance envoyé → en préparation → prêt", () => {
  assert.equal(avancer(bon("envoyé")).statut, "en préparation");
  assert.equal(avancer(bon("en préparation")).statut, "prêt");
});

test("CUI-3 pas de saut de statut : envoyé ne va jamais directement à prêt", () => {
  const b = avancer(bon("envoyé"));
  assert.equal(b.statut, "en préparation");
  assert.notEqual(b.statut, "prêt");
});

test("CUI-3 dernier état : déjà prêt refusé", () => {
  assert.match(avancer(bon("prêt")).erreur, /Déjà prêt/);
});

test("CUI-4 annulation pendant la préparation : carte ANNULÉ + signal sonore", () => {
  const a = recevoirAnnulation(bon("en préparation"));
  assert.equal(a.statut, "annulé");
  assert.equal(a.signal, "annulation");
});

test("CUI-4 annulé : plus d'avance possible", () => {
  assert.match(avancer(recevoirAnnulation(bon())).erreur, /annulé/i);
});

test("D3 nouveau bon : signal sonore + statut envoyé", () => {
  const n = nouveauBon({ id: "b2", table: "7", heure: "12:10" });
  assert.equal(n.statut, "envoyé");
  assert.equal(n.signal, "nouveau");
});

test("trier : colonnes dans l'ordre, annulé en fin", () => {
  const t = trier([bon("prêt"), bon("annulé"), bon("envoyé"), bon("en préparation")]);
  assert.deepEqual(t.map((b) => b.statut), ["envoyé", "en préparation", "prêt", "annulé"]);
  assert.deepEqual(COLONNES, ["envoyé", "en préparation", "prêt"]);
});

test("perte de connexion : message clair, jamais « à jour »", () => {
  assert.match(messageHorsLigne(false, "12:00"), /périmée/);
  assert.equal(messageHorsLigne(true, "12:00"), "File en temps réel");
});
