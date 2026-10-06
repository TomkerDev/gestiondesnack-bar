"""Tests M5 chiffres. Usage: python core/tests_m5/test_m5.py"""
import sys
sys.path.insert(0, "core/tests_m5")
from m5_mirror import *
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

# Scenario chiffre complet : fond 10000, vente 3000 especes (recu 5000, monnaie 2000),
# tip especes 500, remb ardoise especes 2000, sortie validee 1500, tip mobile reverse 1000 (sortie).
# attendues = 10000+3000-2000+500+2000-1500-1000 = 11000
a = attendues(10000, 3000, 2000, 500, 2000, 2500)
ok("CAI-2_scenario_chiffre_complet", a == 11000)
# Mobile exclu des attendues
ok("CAI-2_mobile_hors_especes", attendues(10000, 0, 0, 0, 0, 0) == 10000)
# CAI-4 : ecart 0 sans motif ; dans tolerance sans motif ; hors tolerance exige motif+comm
ok("CAI-4_ecart_zero_sans_motif", cloturer(11000, 11000, 0, "", "") == ("close", 0))
ok("CAI-4_dans_tolerance_sans_motif", cloturer(11100, 11000, 200, "", "") == ("close", 100))
ko("CAI-4_hors_tolerance_sans_motif_refuse", EcartNonJustifie, lambda: cloturer(11500, 11000, 200, "", ""))
ko("CAI-4_motif_sans_commentaire_refuse", EcartNonJustifie, lambda: cloturer(11500, 11000, 0, "erreur", ""))
ok("CAI-4_manque_justifie", cloturer(10500, 11000, 0, "erreur monnaie", "rendu 1000 au lieu de 500") == ("close", -500))
# CAI-5 : forcage R1 + motif ; sans R1 refuse
ok("CAI-5_forcage_R1_motif", cloturer(0, 11000, 0, "serveur parti", "vu gerant", True, True)[0] == "forcee")
ko("CAI-5_forcage_sans_R1_refuse", ForcageSansAutorisation, lambda: cloturer(0, 11000, 0, "m", "c", False, True))
# CAI-1/R5 : journee refuse si caisse ouverte ; close definitive
ko("CAI-1_journee_caisse_ouverte_refusee", CaissesNonCloses, lambda: fermer_journee("en_cloture", False))
ok("CAI-1_journee_toutes_closes", fermer_journee("en_cloture", True) == "close")
ko("R5_journee_close_jamais_rouverte", JourneeDejaClose, lambda: fermer_journee("close", True))
ok("R5_correction_veille_imputee_jour_J", imputer_correction("J2") == "J2")
# CAI-6/PAI-4 : rapprochement releve
ok_, lit = rapprocher([("W1", 2500), ("W2", 1000)], [("W1", 2500)])
ok("CAI-6_rapproche_ok_et_litige", ok_ == ["W1"] and lit == ["W2"])
print("M5 OK —", n, "tests")
