import test from "node:test";
import assert from "node:assert/strict";
import { autorise, gardeRoute, liensPour } from "../src/lib/droits.js";

test("matrice §3 : le serveur vend mais ne touche ni prix ni caisse gérant", () => {
  assert.equal(autorise("serveur", "VendreEncaisser").ok, true);
  assert.equal(autorise("serveur", "FixerPrixPlafond").ok, false);
  assert.equal(autorise("serveur", "Gerant").ok, false);
  assert.equal(autorise("serveur", "VoirCoutsMarges").ok, false);
});

test("matrice §3 : le gérant fait tout sauf les coûts/marges (R3)", () => {
  assert.equal(autorise("gerant", "RemiseOffert").ok, true);
  assert.equal(autorise("gerant", "Gerant").ok, true);
  assert.equal(autorise("gerant", "CuisineAvancer").ok, true);
  assert.equal(autorise("gerant", "VoirCoutsMarges").ok, false);
});

test("matrice §3 : le propriétaire a tous les droits", () => {
  for (const a of ["VendreEncaisser", "Gerant", "CuisineAvancer", "VoirCoutsMarges"])
    assert.equal(autorise("proprietaire", a).ok, true);
});

test("garde : sans rôle → /connexion ; serveur bloqué sur /pc", () => {
  assert.equal(gardeRoute("", "/commande").redirection, "/connexion");
  assert.equal(gardeRoute("serveur", "/commande").ok, true);
  assert.equal(gardeRoute("serveur", "/cuisine").ok, true);
  const bloque = gardeRoute("serveur", "/pc");
  assert.equal(bloque.ok, false);
  assert.equal(bloque.redirection, "/connexion");
  assert.equal(gardeRoute("gerant", "/pc").ok, true);
  assert.equal(gardeRoute("gerant", "/pc/stock").ok, true);
});

test("navigation filtrée : 5 liens serveur, 7 gérant/proprio", () => {
  assert.equal(liensPour("").length, 0);
  assert.deepEqual(liensPour("serveur").map(([h]) => h),
    ["/commande", "/commandes", "/cuisine", "/paiement", "/ma-caisse"]);
  assert.equal(liensPour("gerant").length, 7);
  assert.equal(liensPour("proprietaire").length, 7);
});
