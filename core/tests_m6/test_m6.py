"""Tests M6. Usage: python core/tests_m6/test_m6.py"""
import sys
sys.path.insert(0, "core/tests_m6")
from m6_mirror import *
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

# SEC-1 : PIN >= 4 chiffres ; blocage 5 echecs ; session 2 min
ok("SEC-1_pin_4_chiffres_ok", pin_valide("1234"))
ko("SEC-1_pin_3_chiffres_refuse", PinTropCourt, lambda: pin_valide("123"))
ko("SEC-1_pin_lettres_refuse", PinTropCourt, lambda: pin_valide("12ab"))
ok("SEC-1_blocage_5min_puis_15min", duree_blocage(4) == 0 and duree_blocage(5) == 300 and duree_blocage(6) == 900)
ok("SEC-1_session_2min", session_valide(1000, 1120))
ko("SEC-1_session_expiree", SessionExpiree, lambda: session_valide(1000, 1121))
# Matrice §3 : serveur refuse remise/correction/couts ; gerant refuse couts ; proprio tout
ko("MATRICE_serveur_remise_refusee", DroitInsuffisant, lambda: autorise("serveur", "remise"))
ko("MATRICE_serveur_correction_refusee", DroitInsuffisant, lambda: autorise("serveur", "correction"))
ko("MATRICE_serveur_couts_refuse", DroitInsuffisant, lambda: autorise("serveur", "couts"))
ok("MATRICE_serveur_vente_ok", autorise("serveur", "vendre"))
ko("MATRICE_gerant_couts_refuse_R3", DroitInsuffisant, lambda: autorise("gerant", "couts"))
ok("MATRICE_gerant_remise_ok", autorise("gerant", "remise"))
ok("MATRICE_proprio_couts_ok", autorise("proprietaire", "couts"))
# R1 : jeton 1 usage, 60s, lie, offline refuse ; reutilisation refusee ; 2e acte re-PIN
j = Jeton("remise", "c1", 500, "ibou", "awa", 1000)
consommer(j, "remise", "c1", 500, 1030)
ok("R1_jeton_consomme_1_usage", j.consomme)
ko("R1_reutilisation_refusee", JetonDejaConsomme, lambda: consommer(j, "remise", "c1", 500, 1040))
j = Jeton("remise", "c1", 500, "ibou", "awa", 1000)
ko("R1_expire_60s", JetonExpire, lambda: consommer(j, "remise", "c1", 500, 1061))
j = Jeton("remise", "c1", 500, "ibou", "awa", 1000)
ko("R1_montant_lie_refuse", JetonInvalide, lambda: consommer(j, "remise", "c1", 600, 1030))
j = Jeton("remise", "c1", 500, "ibou", "awa", 1000)
ko("R1_offline_refuse", R1HorsLigne, lambda: consommer(j, "remise", "c1", 500, 1030, True))
print("M6 OK —", n, "tests")
