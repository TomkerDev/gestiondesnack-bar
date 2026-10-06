"""Tests M4. Usage: python core/tests_m4/test_m4.py"""
import sys, itertools
sys.path.insert(0, "core/tests_m4")
from m4_mirror import *
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

def ko(nom, exc, fn):
    global n
    try:
        fn()
    except exc:
        n += 1; print("OK", nom); return
    raise SystemExit("FAIL " + nom)

# STK-2 commutativite : tout ordre => meme stock (condition offline)
base = [Mvt("b", 24, "achat"), Mvt("b", -2, "vente"), Mvt("b", -1, "vente"), Mvt("b", 12, "achat")]
ok("STK-2_commutativite_24_ordres", all(dispo(list(p), "b") == 33 for p in itertools.permutations(base)))
ok("STK-2_stock_somme_pas_ecriture", dispo(base, "b") == 33)
# STK-3 : derniere bouteille vendue 2 fois => autorise + alerte + liste negatifs
m = [Mvt("b", 1, "achat")]
ok("STK-3_derniere_bouteille_ok_sans_alerte", vente(m, "b", 1) is False)
ok("STK-3_seconde_vente_autorisee_avec_alerte", vente(m, "b", 1) is True)
ok("STK-3_stock_negatif_liste", negatifs(m) == ["b"] and dispo(m, "b") == -1)
# STK-4 [M7-Q1-A] : a_valider hors dispo ; validee => achat ; rejet non-validee => rien ; rejet validee => inverse
m = [Mvt("b", 10, "achat")]
en_attente = [("b", 6)]
ok("STK-4_a_valider_hors_dispo", dispo(m, "b") == 10)
m += valider_entree("ibou", "awa", True, en_attente)
ok("STK-4_validation_fait_entrer_en_dispo", dispo(m, "b") == 16)
ok("STK-4_rejet_non_validee_rien", rejeter(False, en_attente) == [])
inv = rejeter(True, en_attente)
ok("STK-4_rejet_validee_inverse", inv[0].qte == -6 and inv[0].type == "rejet_entree")
ko("STK-4_saisie_non_autorisee_refusee", SaisieNonAutorisee, lambda: valider_entree("x", "awa", False, en_attente))
ko("STK-4_auto_validation_refusee", ValidationParSaisisseur, lambda: valider_entree("awa", "awa", True, en_attente))
# STK-5 : manque + excedent + zero + motif obligatoire
mv = inventaire("b", 16, 14, "casse non declaree")
ok("STK-5_manque_correction_negative", mv.qte == -2 and mv.type == "correction")
mv = inventaire("b", 16, 18, "livraison non saisie")
ok("STK-5_excedent_correction_positive", mv.qte == 2)
ok("STK-5_zero_pas_de_mouvement", inventaire("b", 16, 16, "") is None)
ko("STK-5_ecart_sans_motif_refuse", InventaireSansMotif, lambda: inventaire("b", 16, 14, "  "))
# STK-6 : pertes quantites + valorisation proprio seul (R3)
ok("STK-6_valorisation_proprio", valorisation([("b", 2, 900), ("b", 1, 900)], True) == 2700)
ok("STK-6_valorisation_cachee_gerant", valorisation([("b", 2, 900)], False) is None)
# CUI-3/CUI-4/CUI-5
ok("CUI-3_envoye_vers_preparation", transition("envoye", "preparation") == "preparation")
ok("CUI-4_envoye_annulable_serveur", transition("envoye", "annule") == "annule")
ok("CUI-4_annule_apres_prepa_perte", perte_apres_prepa("preparation") is True)
ok("CUI-4_annule_avant_prepa_pas_perte", perte_apres_prepa("envoye") is False)
ko("CUI-3_saut_statut_refuse", TransitionCuisineInvalide, lambda: transition("envoye", "servi"))
ko("CUI-5_annulation_offline_impossible", AnnulationHorsLigne, lambda: transition("envoye", "annule", True))
print("M4 OK —", n, "tests")
