import { test } from "node:test";
import assert from "node:assert/strict";
import {
  stockDisponible, triStock, produitsNegatifs, saisirEntree, validerEntree, rejeterEntree,
  ecartInventaire, correctionInventaire, regrouperPertes, valorisationPertes,
  depassementsPlafond, fixerPlafond, rembourser, modifierPrix, ORIGINES_PERTES
} from "../src/lib/stock_pc.js";

const M = [{ produit: "biere", quantite: -3, type: "vente" }, { produit: "biere", quantite: 25, type: "achat" }];

test("STK-2/3 : stock = somme des mouvements, négatifs en tête", () => {
  assert.equal(stockDisponible(M, "biere"), 22);
  const tri = triStock([{ produit: "a", quantite: 5 }, { produit: "b", quantite: -1 }, { produit: "c", quantite: 0 }]);
  assert.equal(tri[0].produit, "b");
  assert.deepEqual(produitsNegatifs([{ produit: "jus", quantite: -2 }]), ["jus"]);
  assert.deepEqual(produitsNegatifs(M), []);
});

test("STK-4 : rejet d'une entrée", () => {
  const ligne = [{ produit: "coca", quantite: 12 }];
  // même personne saisit puis valide → refus
  const m = validerEntree("awa", "awa", true, ligne);
  assert.equal(m.ok, false);
  assert.match(m.raison, /deux personnes/);
  // sans indicateur → refus
  assert.equal(validerEntree("awa", "gérant", false, ligne).ok, false);
  // validation OK → mouvements d'achat
  const ok = validerEntree("awa", "gérant", true, ligne);
  assert.equal(ok.ok, true);
  assert.deepEqual(ok.mouvements, [{ produit: "coca", quantite: 12, type: "achat" }]);
  // rejet d'une entrée JAMAIS validée → aucun mouvement inverse
  const rej = rejeterEntree({ validee: false, lignes: ligne });
  assert.deepEqual(rej.mouvements, []);
  assert.match(rej.note, /jamais entrée en disponible/);
  // rejet d'une entrée validée → mouvement inverse exact
  const rev = rejeterEntree({ validee: true, lignes: ligne });
  assert.deepEqual(rev.mouvements, [{ produit: "coca", quantite: -12, type: "rejet_entree" }]);
});

test("STK-4 : une entrée ne contient que des quantités entières positives", () => {
  assert.equal(saisirEntree([{ produit: "biere", quantite: 6 }]).ok, true);
  assert.equal(saisirEntree([{ produit: "biere", quantite: 2.5 }]).ok, false);
  assert.equal(saisirEntree([]).ok, false);
  const l = saisirEntree([{ produit: "biere", quantite: 6 }]);
  assert.ok(!("prix" in l.lignes[0]) && !("cout" in l.lignes[0]));
});

test("STK-5 : inventaire manque ET excédent, motif obligatoire par écart", () => {
  const manque = correctionInventaire("biere", 20, 18, "casse");
  assert.equal(manque.ok, true);
  assert.deepEqual(manque.mouvement, { produit: "biere", quantite: -2, type: "correction" });
  const excedent = correctionInventaire("biere", 20, 23, "comptage double");
  assert.deepEqual(excedent.mouvement, { produit: "biere", quantite: 3, type: "correction" });
  // écart sans motif → refus
  assert.match(correctionInventaire("biere", 20, 18, "").raison, /Motif obligatoire/);
  assert.match(correctionInventaire("biere", 20, 18, "  ").raison, /Motif obligatoire/);
  // pas d'écart → aucun mouvement, aucun motif exigé
  const nul = correctionInventaire("biere", 20, 20, "");
  assert.equal(nul.ok, true);
  assert.equal(nul.mouvement, null);
  assert.equal(ecartInventaire(20, 18).ecart, -2);
});

test("STK-6 : pertes séparées, valorisation au coût réservée au proprio (R3)", () => {
  const pertes = [
    { produit: "verre", quantite: 2, coutUnitaire: 500, origine: "casse" },
    { produit: "biere", quantite: 3, coutUnitaire: 700, origine: "offert" }
  ];
  const g = regrouperPertes(pertes);
  assert.equal(ORIGINES_PERTES.length, 4);
  assert.equal(g["casse"].length, 1);
  assert.equal(g["offert"].length, 1);
  assert.equal(g["annulation après préparation"].length, 0);
  assert.equal(valorisationPertes(pertes, false), null); // gérant : rien
  assert.equal(valorisationPertes(pertes, true), 1000 + 2100);
});

test("ARD-5 : dépassements de plafond + plafond fixé par le gérant", () => {
  const clients = [
    { nom: "ali", solde: 5000, plafond: 4000 },
    { nom: "fatou", solde: 1000, plafond: 4000 },
    { nom: "omar", solde: 9999, plafond: null }
  ];
  assert.deepEqual(depassementsPlafond(clients).map((c) => c.nom), ["ali"]);
  assert.equal(fixerPlafond(clients[0], 6000).ok, true);
  assert.equal(fixerPlafond(clients[0], -1).ok, false);
  assert.equal(fixerPlafond(clients[0], 6000.5).ok, false);
});

test("remboursement ardoise : arrondi à zéro, espèces comptées", () => {
  const r = rembourser(3000, 5000, "espèces");
  assert.equal(r.ok, true);
  assert.equal(r.solde, 0);
  assert.equal(r.deltaEspeces, 5000);
  assert.equal(rembourser(3000, 0, "espèces").ok, false);
  assert.equal(rembourser(0, 100, "espèces").ok, false);
});

test("PRX-1 : prix sous le seuil refusé SANS révéler le coût (test gérant)", () => {
  const cout = 850;
  const refus = modifierPrix(1500, 800, cout, "gérant");
  assert.equal(refus.ok, false);
  assert.match(refus.raison, /sous le seuil de rentabilité/);
  // le message ne contient jamais la valeur du coût
  assert.ok(!refus.raison.includes(String(cout)));
  // prix == coût → refus pareil
  assert.equal(modifierPrix(1500, 850, cout, "gérant").ok, false);
  // au-dessus → accepté, changement tracé (qui, ancien, nouveau, quand)
  const ok = modifierPrix(1500, 900, cout, "gérant");
  assert.equal(ok.ok, true);
  assert.deepEqual(Object.keys(ok.changement).sort(), ["ancien", "auteur", "nouveau", "quand"]);
  assert.equal(modifierPrix(1500, -5, cout, "gérant").ok, false);
});
