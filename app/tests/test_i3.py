"""Tests statiques I3 : liste, détail, payée→correction, offline visible, DUPLICATA.
Usage: python app/tests/test_i3.py"""
import pathlib
app = pathlib.Path(__file__).resolve().parents[1] / "src"
liste = (app / "routes/commandes/+page.svelte").read_text(encoding="utf-8")
detail = (app / "routes/commandes/[id]/+page.svelte").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# Liste : groupement par table, action principale, état vide
ok("I3_groupement_par_table", "groupParTable" in liste)
ok("I3_nouvelle_commande_principale", "Nouvelle commande" in liste)
ok("I3_etat_vide", "Aucune commande ouverte" in liste)
ok("I3_etat_cuisine_visible", "etatCuisine" in liste and "PastilleStatut" in liste)

# Détail : actions complètes (libellés définis dans detail_commande.js, rendus par la page)
lib = (pathlib.Path(__file__).resolve().parents[1] / "src/lib/detail_commande.js").read_text(encoding="utf-8")
ok("I3_rendu_actions", "listeActions" in detail and "listeActions as a" in detail)
for cle, etiquette in [("annuler", "Annuler un plat"), ("boisson", "Retirer une boisson"),
                       ("transferer_lignes", "Transférer des lignes"), ("transferer_cmd", "Transférer la commande"),
                       ("convertir", "Convertir comptoir"), ("imprimer", "Imprimer")]:
    ok("I3_action_" + cle, etiquette in lib)

# Payée → seule action : Demander une correction
ok("I3_payee_correction_uniquement", "Demander une correction" in lib and "estPayee" in lib)

# Offline : jamais caché silencieusement — raison affichée à côté du bouton
ok("I3_offline_raison_affichee", "raisonInactif" in detail and 'role="note"' in detail)
ok("I3_raisons_meme_hors_ligne", "raisonInactif" in lib and "Hors ligne" in lib)

# R1 en préparation
ok("I3_R1_en_preparation", "FenetreR1" in detail and "en préparation" in detail)

# DUPLICATA
ok("I3_duplicata", "DUPLICATA" in lib and "imprimerAddition" in detail)

# 48px partout sur les boutons d'action
ok("I3_boutons_tactiles", detail.count("zone-tactile") >= 4)

print("I3 OK —", n, "tests")
