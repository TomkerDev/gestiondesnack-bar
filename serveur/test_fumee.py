"""Test de fumee du serveur local (spec v1.2, stdlib uniquement).

Lance serveur.py sur une base jetable (SNACK_DB), exerce le cycle complet :
session -> catalogue -> commande -> envoi cuisine -> bons -> paiement especes
-> caisse -> ardoises -> remboursement -> stock -> prix -> journee.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(tempfile.gettempdir(), "snack-test-fumee.db")
PORT = 18080
URL = "http://127.0.0.1:%d" % PORT


def appel(methode, chemin, corps=None):
    data = json.dumps(corps or {}).encode() if corps is not None else None
    req = urllib.request.Request(URL + chemin, data=data, method=methode,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def verif(cond, nom):
    print(("PASS " if cond else "FAIL ") + nom)
    if not cond:
        raise SystemExit("Echec : " + nom)


def main():
    if os.path.exists(BASE):
        os.remove(BASE)
    env = dict(os.environ, SNACK_DB=BASE)
    srv = subprocess.Popen(
        [sys.executable, os.path.join(RACINE, "serveur", "serveur.py"), str(PORT)],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                appel("GET", "/api/produits")
                break
            except OSError:
                time.sleep(0.1)
        # 1. session SEC-1
        s, r = appel("POST", "/api/session", {"code": "1234"})
        verif(s == 200 and r["ok"] and r["utilisateur"]["nom"] == "Awa", "session Awa")
        s, r = appel("POST", "/api/session", {"code": "0000"})
        verif(s == 401 and not r["ok"], "code inconnu refuse")
        # 2. catalogue I2
        s, r = appel("GET", "/api/produits")
        verif(s == 200 and len(r["produits"]) == 8, "catalogue 8 produits")
        # 3. commande + lignes
        s, r = appel("POST", "/api/commandes",
                     {"serveur": "u-awa", "mode": "comptoir",
                      "lignes": [{"produit": "p-soda", "quantite": 2}]})
        verif(s == 200 and r["commande"]["total"] == 1000, "commande 2 sodas = 1000")
        cid = r["commande"]["id"]
        s, r = appel("POST", "/api/commandes/%s/lignes" % cid,
                     {"lignes": [{"produit": "p-eau", "quantite": 1}]})
        verif(s == 200 and r["commande"]["total"] == 1700, "ajout eau -> 1700")
        # 4. envoi cuisine + bon
        s, r = appel("POST", "/api/commandes/%s/envoyer" % cid)
        verif(s == 200 and r["ok"] and r["nBon"] == 1, "envoi cuisine bon n1")
        s, r = appel("GET", "/api/cuisine/bons")
        verif(s == 200 and len(r["bons"]) == 1, "1 bon cuisine")
        bid = r["bons"][0]["id"]
        s, r = appel("POST", "/api/cuisine/bons/%s/avancer" % bid)
        verif(s == 200 and r["statut"] == "en_preparation", "bon en preparation")
        # 5. regle PAI-2 : total inexact refuse
        s, r = appel("POST", "/api/commandes/%s/paiement" % cid,
                     {"reglements": [{"mode": "especes", "montant": 1000,
                                      "montant_recu": 1000, "monnaie_rendue": 0}]})
        verif(s == 409 and not r["ok"], "paiement partiel refuse (PAI-2)")
        # 6. paiement especes exact PAI-3
        s, r = appel("POST", "/api/commandes/%s/paiement" % cid,
                     {"reglements": [{"mode": "especes", "montant": 1700,
                                      "montant_recu": 2000, "monnaie_rendue": 300}]})
        verif(s == 200 and r["commande"]["statut"] == "payée", "paiement exact, monnaie 300")
        # 7. caisse CAI-2 : fond 5000 + especes 1700
        s, r = appel("GET", "/api/caisse?serveur=u-awa")
        verif(s == 200 and r["caisse"]["attendu"] == 6700, "caisse attendue 6700")
        # 8. vente ardoise ARD-2 puis remboursement ARD-4
        s, r = appel("POST", "/api/commandes",
                     {"serveur": "u-awa", "lignes": [{"produit": "p-jus", "quantite": 2}]})
        cid2 = r["commande"]["id"]
        s, r = appel("POST", "/api/commandes/%s/paiement" % cid2,
                     {"reglements": [{"mode": "ardoise", "montant": 2000, "client_id": "c-koffi"}]})
        verif(s == 200, "vente ardoise Koffi 2000")
        s, r = appel("GET", "/api/ardoises")
        koffi = [c for c in r["ardoises"] if c["id"] == "c-koffi"][0]
        verif(koffi["solde"] == 2000, "solde Koffi 2000")
        s, r = appel("POST", "/api/ardoises/c-koffi/remboursement",
                     {"montant": 500, "mode": "especes", "serveur": "u-awa"})
        verif(s == 200 and r["solde"] == 1500, "remboursement 500 -> solde 1500")
        # 9. prix PRX-1 refuse au serveur, accepte au gerant
        s, r = appel("POST", "/api/produits/p-soda/prix", {"prix": 600, "serveur": "u-awa"})
        verif(s == 409 and not r["ok"], "prix refuse au serveur (R3)")
        s, r = appel("POST", "/api/produits/p-soda/prix", {"prix": 600, "serveur": "u-ibrahima"})
        verif(s == 200 and r["prix"] == 600, "prix soda -> 600 par gerant")
        # 10. cloture caisse : releve du reel puis cloture a l'exact
        s, r = appel("GET", "/api/caisse?serveur=u-awa")
        attendu = r["caisse"]["attendu"]
        s, r = appel("POST", "/api/caisse/cloture", {"serveur": "u-awa", "compte": attendu})
        verif(s == 200 and r["statut"] == "close" and r["ecart"] == 0,
              "cloture caisse ecart 0 (attendu %d)" % attendu)
        s, r = appel("POST", "/api/journee/cloturer")
        verif(s == 200 and r["statut"] == "close", "journee cloturee")
        print("FUMEE OK : 10 etapes vertes")
    finally:
        srv.terminate()
        srv.wait(timeout=10)


if __name__ == "__main__":
    main()
