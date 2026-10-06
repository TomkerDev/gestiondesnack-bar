"""M1 critere 2 : commande, paiement mixte, ardoise, correction. Usage: python db/test_scenario_m1.py"""
import sqlite3, pathlib, uuid

def nid():
    return str(uuid.uuid4())

base = pathlib.Path(__file__).parent / "migrations"
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys=ON")
for f in sorted(base.glob("*.sql")):
    db.executescript(open(f, encoding="utf-8").read())

J, GERANT, SERV = nid(), nid(), nid()
CLI, BIERRE, PLAT = nid(), nid(), nid()
CMD, CMD2, L1, L2, L3 = nid(), nid(), nid(), nid(), nid()
J2, CORR = nid(), nid()
db.executemany("INSERT INTO users(id,nom,role,pin_hash,pin_salt) VALUES(?,?,?,?,?)", [
    (GERANT, "Awa", "gerant", "h", "s"), (SERV, "Ibou", "serveur", "h", "s")])
db.execute("INSERT INTO products(id,nom,type,prix_vente,prix_achat) VALUES(?,?,'boisson',?,?)",
           (BIERRE, "Biere 65cl", 1500, 900))
db.execute("INSERT INTO products(id,nom,type,suivi_stock,prix_vente,cout_estime) VALUES(?,?,'plat',0,?,?)",
           (PLAT, "Poulet braise", 2500, 1400))
db.execute("INSERT INTO clients(id,nom,telephone,plafond) VALUES(?,?,?,?)", (CLI, "Moussa", "770000000", 10000))
db.execute("INSERT INTO journees(id,statut,ouverte_par) VALUES(?,'ouverte',?)", (J, GERANT))
db.execute("INSERT INTO caisses(id,journee_id,serveur_id,fond) VALUES(?,?,?,?)", (nid(), J, SERV, 10000))
e = nid()

db.execute("INSERT INTO entrees_stock(id,journee_id,statut,saisie_par,validee_par) VALUES(? ,?,'validee',?,?)",
           (e, J, SERV, GERANT))
db.execute("INSERT INTO entree_lignes(id,entree_id,produit_id,quantite) VALUES(?,?,?,?)", (nid(), e, BIERRE, 24))
db.execute("INSERT INTO mouvements_stock(id,produit_id,journee_id,quantite,type,entree_id,cree_par) VALUES(?,?,?,?,?,?,?)",
           (nid(), BIERRE, J, 24, "achat", e, GERANT))
db.execute("INSERT INTO commandes(id,journee_id,serveur_id,table_nom,mode,statut,total_brut,total_net) VALUES(?,?,?,?,?,?,?,?)",
           (CMD, J, SERV, "T3", "table", "ouverte", 5500, 5500))
db.execute("INSERT INTO lignes(id,commande_id,produit_id,quantite,prix_unitaire_fige,cout_unitaire_fige,statut_cuisine) VALUES(?,?,?,?,?,?,?)",
           (L1, CMD, BIERRE, 2, 1500, 900, "non_envoye"))
db.execute("INSERT INTO lignes(id,commande_id,produit_id,quantite,prix_unitaire_fige,cout_unitaire_fige,statut_cuisine) VALUES(?,?,?,?,?,?,?)",
           (L2, CMD, PLAT, 1, 2500, 1400, "envoye"))
db.execute("INSERT INTO mouvements_stock(id,produit_id,journee_id,quantite,type,commande_id,cree_par) VALUES(?,?,?,?,?,?,?)",
           (nid(), BIERRE, J, -2, "vente", CMD, SERV))
db.execute("INSERT INTO reglements(id,commande_id,journee_id,serveur_id,mode,montant,montant_recu,monnaie_rendue,pourboire) VALUES(?,?,?,?,?,?,?,?,?)",
           (nid(), CMD, J, SERV, "especes", 3000, 3000, 0, 500))
db.execute("INSERT INTO reglements(id,commande_id,journee_id,serveur_id,mode,montant,operateur,reference_operateur,statut_rapprochement) VALUES(?,?,?,?,?,?,?,?,?)",
           (nid(), CMD, J, SERV, "mobile", 2500, "Wave", "W123", "a_rapprocher"))
db.execute("UPDATE commandes SET statut='payee' WHERE id=?", (CMD,))
db.execute("INSERT INTO audit_log(qui,quoi,commande_id,motif,detail) VALUES(?,?,?,?,?)",
           (SERV, "paiement_mixte", CMD, None, '{"especes":3000,"mobile":2500,"tip":500}'))
db.execute("INSERT INTO commandes(id,journee_id,serveur_id,table_nom,mode,statut,total_brut,total_net) VALUES(?,?,?,?,?,?,?,?)",
           (CMD2, J, SERV, "T1", "table", "ouverte", 3000, 3000))
db.execute("INSERT INTO lignes(id,commande_id,produit_id,quantite,prix_unitaire_fige,cout_unitaire_fige) VALUES(?,?,?,?,?,?)",
           (L3, CMD2, BIERRE, 2, 1500, 900))
db.execute("INSERT INTO reglements(id,commande_id,journee_id,serveur_id,mode,montant,client_id) VALUES(?,?,?,?,?,?,?)",
           (nid(), CMD2, J, SERV, "ardoise", 3000, CLI))
db.execute("INSERT INTO ardoise_mouvements(id,client_id,commande_id,journee_id,sens,montant,serveur_id) VALUES(?,?,?,?,?,?,?)",
           (nid(), CLI, CMD2, J, "vente", 3000, SERV))
db.execute("UPDATE commandes SET statut='payee' WHERE id=?", (CMD2,))
db.execute("INSERT INTO journees(id,statut,ouverte_par) VALUES(?,'ouverte',?)", (J2, GERANT))
db.execute("INSERT INTO corrections(id,commande_origine_id,journee_id,type,sort_produit,montant,motif,cree_par) VALUES(?,?,?,?,?,?,?,?)",
           (CORR, CMD, J2, "financiere", "retour_stock", 1500, "1 biere en trop", GERANT))
db.execute("INSERT INTO mouvements_stock(id,produit_id,journee_id,quantite,type,cree_par,motif) VALUES(?,?,?,?,?,?,?)",
           (nid(), BIERRE, J2, 1, "retour", GERANT, "correction R4"))
att = db.execute("""SELECT 10000
  + COALESCE((SELECT SUM(montant) FROM reglements WHERE journee_id=? AND serveur_id=? AND mode='especes'),0)
  - COALESCE((SELECT SUM(monnaie_rendue) FROM reglements WHERE journee_id=? AND serveur_id=?),0)
  + COALESCE((SELECT SUM(pourboire) FROM reglements WHERE journee_id=? AND serveur_id=? AND mode='especes'),0)
  - COALESCE((SELECT SUM(montant) FROM sorties_caisse WHERE journee_id=? AND serveur_id=? AND statut='validee'),0)""",
  (J, SERV, J, SERV, J, SERV, J, SERV)).fetchone()[0]
assert att == 10000 + 3000 - 0 + 500, att
for sql in ["UPDATE audit_log SET motif='x'", "DELETE FROM audit_log",
            "UPDATE mouvements_stock SET quantite=0", "DELETE FROM mouvements_stock"]:
    try:
        db.execute(sql); raise SystemExit("FAIL trigger manquant: " + sql)
    except sqlite3.Error:
        pass
dispo = db.execute("SELECT SUM(quantite) FROM mouvements_stock WHERE produit_id=? AND journee_id=?", (BIERRE, J)).fetchone()[0]
assert dispo == 22, dispo
print("M1 SCENARIO OK — CAI-2 attendues:", att, "| stock dispo biere (J):", dispo)
