import { test } from "node:test";
import assert from "node:assert/strict";
import { ajouter, retirer, annulerRetrait, nbArticles, total, envoyerCuisine } from "../src/lib/panier.js";

const P = (id, nom, prix) => ({ id, nom, prix });

test("CMD-1 trois produits ajoutés, quantités et total", () => {
  let panier = { lignes: [] };
  panier = ajouter(panier, P("b", "Bière", 1500));
  panier = ajouter(panier, P("s", "Soda", 1000));
  panier = ajouter(panier, P("p", "Poulet", 5000));
  assert.equal(nbArticles(panier), 3);
  assert.equal(total(panier), 7500);
});

test("CMD-6 un appui = exactement une unité, appuis répétés cumulent", () => {
  let panier = ajouter({ lignes: [] }, P("b", "Bière", 1500));
  panier = ajouter(panier, P("b", "Bière", 1500));
  panier = ajouter(panier, P("b", "Bière", 1500));
  assert.equal(panier.lignes.length, 1);
  assert.equal(panier.lignes[0].quantite, 3);
  assert.equal(total(panier), 4500);
});

test("PRX-3 prix figé à l'ajout même si le catalogue change", () => {
  const catalogue = [P("b", "Bière", 1500)];
  let panier = ajouter({ lignes: [] }, catalogue[0]);
  catalogue[0].prix = 9999; // hausse après ajout
  assert.equal(total(panier), 1500);
});

test("retrait puis Annuler restaure la ligne", () => {
  let panier = ajouter({ lignes: [] }, P("b", "Bière", 1500));
  panier = ajouter(panier, P("s", "Soda", 1000));
  panier = ajouter(panier, P("p", "Poulet", 5000));
  const avant = panier;
  const r = retirer(panier, "s");
  assert.equal(r.panier.lignes.length, 2);
  const apresAnnul = annulerRetrait(r.annulable);
  assert.deepEqual(apresAnnul, avant);
});

test("retrait du dernier exemplaire supprime la ligne ; retrait inconnu sans effet", () => {
  let panier = ajouter({ lignes: [] }, P("b", "Bière", 1500));
  const r = retirer(panier, "b");
  assert.equal(r.panier.lignes.length, 0);
  const r2 = retirer(panier, "zzz");
  assert.equal(r2.annulable, null);
  assert.deepEqual(r2.panier, panier);
});

test("CUI-1 envoi en cuisine fige les lignes en « envoyé » et vide le panier", () => {
  let panier = ajouter({ lignes: [] }, P("b", "Bière", 1500));
  panier = ajouter(panier, P("p", "Poulet", 5000));
  const ticket = envoyerCuisine(panier);
  assert.equal(ticket.lignes.length, 2);
  assert.ok(ticket.lignes.every((l) => l.statutCuisine === "envoyé"));
  assert.equal(ticket.total, 6500);
  assert.equal(envoyerCuisine({ lignes: [] }), null);
});
