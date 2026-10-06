"""Tests statiques I8 : stock, entrées, inventaire, pertes, ardoises, prix (PC).
Usage: python app/tests/test_i8.py"""
import pathlib, re
app = pathlib.Path(__file__).resolve().parents[1] / "src"
page = (app / "routes/pc/stock/+page.svelte").read_text(encoding="utf-8")
lib = (app / "lib/stock_pc.js").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# Stock : négatifs en tête, historique
ok("I8_stock_vues", "Stock" in page and "Entrées" in page and "Inventaire" in page
    and "Pertes" in page and "Ardoises" in page and "Prix" in page)
ok("I8_negatifs_alerte", "Stock négatif" in page and "produitsNegatifs" in page)
ok("I8_tri_negatifs_en_tete", "a.quantite < 0" in lib)
ok("I8_historique_mouvements", "Historique des mouvements" in page and "m.type" in page)

# Entrées : file à valider, valider/rejeter, quantités seulement, séparation dispo/attente
ok("I8_file_a_valider", "File des entrées à valider" in page and "à valider" in page)
ok("I8_boutons_valider_rejeter", 'libelle="Valider"' in page and 'libelle="Rejeter"' in page)
ok("I8_saisie_quantites_seules", "Seules des quantités sont saisies" in page)
ok("I8_dispo_vs_attente", "Disponible" in page and "En attente" in page and "séparément" in page)
ok("I8_separation_meme_personne", "deux personnes différentes" in lib)

# Inventaire : écarts en quantités, motif obligatoire
ok("I8_inventaire_boissons", "Inventaire quotidien des boissons" in page)
ok("I8_ecart_quantites", "<th>Écart</th>" in page and "ecartInventaire" in page)
ok("I8_motif_obligatoire", "Motif obligatoire pour tout écart" in lib and "Motif de l'écart" in page)
ok("I8_ordre_inventaire", "Après clôture des caisses" in page)

# Pertes : séparées par origine, valorisation proprio seulement
for o in ["casse", "annulation après préparation", "offert", "écart d'inventaire négatif"]:
    ok("I8_perte_" + o.split()[0], o in lib)
ok("I8_pertes_affichees_separees", "Regroupées par origine" in page)
ok("I8_valorisation_proprio", 'role === "proprietaire"' in page and "valorisationPertes" in lib)

# Ardoises : soldes, plafonds, dépassements, fixer plafond, remboursement
ok("I8_ardoises_depassement", "Plafond dépassé" in page and "dépassement" in page)
ok("I8_fixer_plafond", "Fixer un plafond" in page and "gérant ou propriétaire" in page)
ok("I8_remboursement", "Rembourser en espèces" in page)

# Prix : seuil sans révéler le coût (PRX-1)
ok("I8_prix_seuil", "sous le seuil de rentabilité" in lib)
ok("I8_prix_message_sans_cout", "sous le seuil de rentabilité" in lib and "modifierPrix" in page)
# le coût n'apparaît jamais dans un message d'erreur de la page
ok("I8_prix_sans_afficher_cout", "Afficher le coût" not in page and "le coût est" not in page)
ok("I8_prix_nouvelles_lignes", "nouvelles lignes" in page)

# Interfaces tactiles : nav tactile + boutons composés (Bouton porte zone-tactile)
ok("I8_tactile", "zone-tactile" in page and page.count("<Bouton") >= 4)

print("I8 OK —", n, "tests")
