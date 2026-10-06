"""Tests M3. Usage: python core/tests_m3/test_m3.py"""
import sys
sys.path.insert(0, "core/tests_m3")
from m3_mirror import *
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

c = Client("m", 10000, 7000)
ok("ARD-2_vente_dans_plafond_acceptee", decider(c, 3000) == "accepte")
ok("ARD-2_montant_exactement_au_plafond_accepte", decider(Client("m", 10000, 8000), 2000) == "accepte")
ok("ARD-2_un_de_plus_refuse_deblocable", decider(Client("m", 10000, 8000), 2001) == "refuse_deblocable")
ok("ARD-2_sans_client_refuse", decider(None, 1000) == "refuse")
ok("ARD-1_plafond_zero_tout_refuse", decider(Client("m", 0, 0), 1) == "refuse_deblocable")
# ARD-3 : deblocage ponctuel R1, plafond inchange
ok("ARD-3_deblocage_R1_solde_bouge_plafond_fixe",
   appliquer_deblocage(9000, 3000, True) == 12000 and c.plafond == 10000)
ko("ARD-3_deblocage_sans_R1_refuse", DeblocageSansAutorisation, lambda: appliquer_deblocage(9000, 3000, False))
# ARD-4 : remboursement distinct attribue serveur ; especes vs mobile ; CA vs especes
s, d = appliquer_remboursement(5000, 2000, "especes")
ok("ARD-4_remboursement_especes_solde_et_attendues", (s, d) == (3000, 2000))
s, d = appliquer_remboursement(5000, 2000, "mobile")
ok("ARD-4_remboursement_mobile_hors_especes", (s, d) == (3000, 0))
s, d = appliquer_remboursement(1000, 5000, "especes")
ok("ARD-4_trop_percu_plafonne_a_zero", (s, d) == (0, 5000))
ko("ARD-4_remboursement_zero_refuse", RemboursementInvalide, lambda: appliquer_remboursement(5000, 0, "especes"))
ca, esp = impact_vente(3000)
ok("ARD-4_vente_CA_oui_especes_non", (ca, esp) == (3000, 0))
# ARD-6 : offline sur instantane, pas de deblocage, alerte resynchro
snap = Client("m", 10000, 7000)
ok("ARD-6_offline_dans_instantane_accepte", decider_offline(snap, 3000) == "accepte")
ok("ARD-6_offline_depassement_refuse_sec", decider_offline(snap, 4000) == "refuse")
ko("ARD-6_deblocage_offline_impossible", DeblocageHorsLigne, tenter_deblocage_offline)
alertes = controler_resynchro([("m", 7000, [3000, 4000], [])], {"m": 10000})
ok("ARD-6_double_vente_offline_alerte_synchro", alertes == [("m", 14000, 10000)])
ok("ARD-6_resynchro_sans_depassement_silencieuse",
   controler_resynchro([("m", 7000, [2000], [1000])], {"m": 10000}) == [])
print("M3 OK —", n, "tests")
