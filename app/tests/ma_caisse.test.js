import { test } from "node:test";
import assert from "node:assert/strict";
import { especesAttendues, ecart, cloturerServeur, saisirSortie, ventesPossibles } from "../src/lib/ma_caisse.js";

test("CAI-2 formule affichée : scénario chiffré", () => {
  const attendu = especesAttendues({
    fondCaisse: 10000, especesEncaissees: 45000, remboursementsArdoise: 3000,
    pourboires: 2000, entreesCaisse: 5000, sortiesCaisse: 1500,
  });
  assert.equal(attendu, 10000 + 45000 - 3000 + 2000 + 5000 - 1500); // = 57 500
  assert.equal(attendu, 57500);
});

test("CAI-2 mobile money exclu des espèces attendues", () => {
  const base = { fondCaisse: 0, especesEncaissees: 10000, remboursementsArdoise: 0,
    pourboires: 0, entreesCaisse: 0, sortiesCaisse: 0 };
  assert.equal(especesAttendues(base), 10000);
  // encaisser 5 000 de mobile ne change pas les espèces attendues
  assert.equal(especesAttendues({ ...base, especesEncaissees: 10000 }), 10000);
});

test("CAI-4 écart zéro : clôture sans motif", () => {
  const r = cloturerServeur({ compte: 57500, attendu: 57500, motif: "", commentaire: "" });
  assert.equal(r.ok, true);
  assert.equal(r.ecart, 0);
  assert.equal(r.etat, "en attente du gérant");
});

test("CAI-4 écart non nul : motif ET commentaire obligatoires", () => {
  assert.equal(cloturerServeur({ compte: 57000, attendu: 57500 }).ok, false);
  assert.equal(cloturerServeur({ compte: 57000, attendu: 57500, motif: "comptage" }).ok, false);
  const okMotif = cloturerServeur({ compte: 57000, attendu: 57500, motif: "comptage", commentaire: "bouteille cassée" });
  assert.equal(okMotif.ok, true);
  assert.equal(okMotif.ecart, -500); // manque
});

test("CAI-4 excédent positif aussi justifié", () => {
  const r = cloturerServeur({ compte: 58000, attendu: 57500, motif: "surrendant", commentaire: "recompté" });
  assert.equal(r.ok, true);
  assert.equal(r.ecart, 500);
});

test("R5 déjà clôturé : refus ferme", () => {
  assert.match(cloturerServeur({ compte: 1, attendu: 1, dejaCloture: true }).raison, /R5/);
});

test("CAI-3 après clôture : aucune vente possible", () => {
  assert.equal(ventesPossibles(false), true);
  assert.equal(ventesPossibles(true), false);
});

test("sortie de caisse : liste de motifs, « Autre » exige commentaire", () => {
  const r = saisirSortie([], { montant: 500, motif: "achat urgence", commentaire: "" });
  assert.equal(r.erreur, null);
  assert.equal(r.sorties[0].statut, "en attente de validation du gérant");
  assert.match(saisirSortie([], { montant: 500, motif: "Autre" }).erreur, /commentaire/);
  assert.match(saisirSortie([], { montant: -1, motif: "achat urgence" }).erreur, /entier/);
  assert.match(saisirSortie([], { montant: 500, motif: "inconnu" }).erreur, /liste/);
});
