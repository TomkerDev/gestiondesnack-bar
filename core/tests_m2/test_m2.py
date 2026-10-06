"""Tests M2 nommes par exigence. Usage: python core/tests_m2/test_m2.py"""
import sys
sys.path.insert(0, "core/tests_m2")
from m2_mirror import *

MODES = ["especes", "mobile", "ardoise"]
n = 0

def cmd(mode="table", table="T3", serv="s1", cid="c1"):
    return Commande(cid, serv, table, mode)

def ligne(lid="l1", q=2, prix=1500):
    return Ligne(lid, "bierre", q, prix)

def ok(nom, fn):
    global n
    fn(); n += 1; print("OK", nom)

def ko(nom, exc, fn):
    global n
    try:
        fn()
    except exc:
        n += 1; print("OK", nom); return
    raise SystemExit("FAIL " + nom + " (pas d'erreur " + exc.__name__ + ")")

# CMD-1 : comptoir ok, table ok
c = cmd("comptoir", None); assert c.mode == "comptoir"; print("OK CMD-1_comptoir")
c = cmd("table", "T3"); assert c.table == "T3"; print("OK CMD-1_table"); n += 2
# CMD-2 : transfert meme table trace
a, b = cmd(table="T3"), cmd(table="T3", cid="c2")
ajouter_ligne(a, ligne()); tr = []
transferer_lignes(a, b, ["l1"], tr)
ok("CMD-2_transfert_meme_table", lambda: None) if tr == ["l1"] and "l1" in b.lignes else (_ for _ in ()).throw(SystemExit("FAIL CMD-2"))
ko("CMD-2_transfert_table_differente_refuse", TransfertTableDifferente,
   lambda: transferer_lignes(cmd(table="T3"), cmd(table="T4", cid="x"), ["z"], []))
# CMD-3 : comptoir->table par createur ; inverse impossible ; autre serveur refuse
c = cmd("comptoir", None); convertir(c, "s1", "T5"); assert c.mode == "table"; print("OK CMD-3_comptoir_vers_table"); n += 1
ko("CMD-3_table_vers_comptoir_interdit", ConversionInterdite, lambda: convertir(cmd("table"), "s1", "T9"))
ko("CMD-3_conversion_par_autre_refusee", ConversionParAutre, lambda: convertir(cmd("comptoir", None), "s2", "T9"))
# CMD-4 : transfert serveur
c = cmd(); transferer_serveur(c, "s2"); assert c.serveur == "s2"; print("OK CMD-4_transfert_serveur"); n += 1
# CMD-5 : retrait avec motif ; sans motif refuse ; inexistante refuse
c = cmd(); ajouter_ligne(c, ligne()); retirer_ligne(c, "l1", "erreur saisie"); assert not c.lignes; print("OK CMD-5_retrait_motif"); n += 1
c = cmd(); ajouter_ligne(c, ligne())
ko("CMD-5_retrait_sans_motif_refuse", BoissonSansMotif, lambda: retirer_ligne(c, "l1", "  "))
ko("CMD-5_ligne_inexistante_refusee", LigneIntrouvable, lambda: retirer_ligne(cmd(), "zz", "motif"))
# PAI-1 : mode inconnu refuse
c = cmd(); ajouter_ligne(c, ligne(q=1, prix=1000))
ko("PAI-1_mode_inconnu_refuse", ModeInconnu, lambda: regler(c, [Reglement("carte", 1000)], MODES))
# PAI-2 : somme == net ; trop faible / trop eleve refuses ; mix especes+mobile ok ; ardoise exclusive+totale
def _c3000():
    c = cmd(); ajouter_ligne(c, ligne(q=2, prix=1500)); return c  # net 3000
ko("PAI-2_reglement_trop_faible_refuse", TotalInexact,
   lambda: regler(_c3000(), [Reglement("especes", 2000, 2000, 0)], MODES))
ko("PAI-2_reglement_trop_eleve_refuse", TotalInexact,
   lambda: regler(_c3000(), [Reglement("especes", 4000, 4000, 0)], MODES))
c = _c3000()
regler(c, [Reglement("especes", 1000, 1000, 0), Reglement("mobile", 2000)], MODES)
assert c.statut == "payee"; print("OK PAI-2_mix_especes_mobile"); n += 1
c = _c3000()
regler(c, [Reglement("ardoise", 3000)], MODES)
assert c.statut == "payee"; print("OK PAI-2_ardoise_totale_seule"); n += 1
ko("PAI-2_mix_avec_ardoise_refuse", ArdoiseNonExclusive,
   lambda: regler(_c3000(), [Reglement("ardoise", 2000), Reglement("especes", 1000, 1000, 0)], MODES))
ko("PAI-2_ardoise_partielle_refusee", ArdoiseNonExclusive,
   lambda: regler(_c3000(), [Reglement("ardoise", 2000)], MODES))
# PAI-3 : recu/monnaie coherents ; recu < montant refuse ; monnaie incoherente refusee
c = _c3000()
regler(c, [Reglement("especes", 3000, 5000, 2000)], MODES)
assert c.reglements[0].monnaie_rendue == 2000; print("OK PAI-3_monnaie_rendue"); n += 1
ko("PAI-3_recu_insuffisant_refuse", MontantInvalide,
   lambda: regler(_c3000(), [Reglement("especes", 3000, 2000, 0)], MODES))
ko("PAI-3_monnaie_incoherente_refusee", MontantInvalide,
   lambda: regler(_c3000(), [Reglement("especes", 3000, 5000, 1000)], MODES))
# PAI-5 : sans R1 refuse ; avec R1 ok ; offert => net 0 ligne conservee + stock a decremente (M4)
c = _c3000()
ko("PAI-5_remise_sans_R1_refusee", RemiseSansAutorisation,
   lambda: appliquer_remise(c, "l1", 500, False, False))
appliquer_remise(c, "l1", 500, False, True); assert total_net(c) == 2500; print("OK PAI-5_remise_avec_R1"); n += 1
c = _c3000(); appliquer_remise(c, "l1", 0, True, True)
assert total_net(c) == 0 and "l1" in c.lignes; print("OK PAI-5_offert_ligne_conservee_net_zero"); n += 1
# PAI-6 : pourboire hors total et hors CA
c = _c3000()
regler(c, [Reglement("especes", 3000, 3500, 500, pourboire=700)], MODES)
assert c.statut == "payee" and total_net(c) == 3000; print("OK PAI-6_tip_hors_total"); n += 1
# R4 : payee immuable — ajout, retrait, remise, reglement refuses ; correction = distinct (table corrections M1)
c = _c3000(); regler(c, [Reglement("especes", 3000, 3000, 0)], MODES)
ko("R4_ajout_sur_payee_refuse", CommandePayee, lambda: ajouter_ligne(c, ligne("l9")))
ko("R4_retrait_sur_payee_refuse", CommandePayee, lambda: retirer_ligne(c, "l1", "motif"))
ko("R4_remise_sur_payee_refusee", CommandePayee, lambda: appliquer_remise(c, "l1", 100, False, True))
ko("R4_reglement_sur_payee_refuse", CommandePayee, lambda: regler(c, [Reglement("especes", 3000, 3000, 0)], MODES))
ko("R4_transfert_serveur_sur_payee_refuse", CommandePayee, lambda: transferer_serveur(c, "s9"))
print("M2 OK —", n, "tests")

