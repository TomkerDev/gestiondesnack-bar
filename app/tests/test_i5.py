"""Tests statiques I5 : 3 colonnes, cartes lisibles, annulé rouge, son, hors ligne.
Usage: python app/tests/test_i5.py"""
import pathlib
app = pathlib.Path(__file__).resolve().parents[1] / "src"
page = (app / "routes/cuisine/+page.svelte").read_text(encoding="utf-8")
lib = (app / "lib/cuisine.js").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# 3 colonnes nommées
for c in ["envoyé", "en préparation", "prêt"]:
    ok("I5_colonne_" + c, '"%s"' % c in lib)

# Carte : table, plats, heure, DUPLICATA
ok("I5_carte_table", "Table {b.table}" in page)
ok("I5_carte_plats", "lignes as l" in page and "quantite" in page)
ok("I5_carte_heure", "Envoyé {b.heure}" in page)
ok("I5_carte_duplicata", "DUPLICATA" in page)

# Un appui = avancer
ok("I5_appui_avance", "toucheCarte" in page and "avancer(" in page)

# Annulé : rouge + mot ANNULÉ + signal sonore
ok("I5_annule_rouge", "annule" in page and "--alerte" in page)
ok("I5_annule_mot", "ANNULÉ" in page)
ok("I5_signal_sonore", "signal" in lib and ("🔔" in page or "son" in page.lower()))

# Lisibilité 2 mètres : grandes polices
ok("I5_lisibilite_24px", "font-size: 24px" in page and "32px" in page)

# Connexion en haut + message clair hors ligne
ok("I5_connexion_visible", "BandeauConnexion" in page and "<header>" in page)
ok("I5_hors_ligne_clair", "périmée" in lib and "messageHorsLigne" in page)

# Papier hors ligne : pas de faux bon (pas de saisie locale dans l'écran)
ok("I5_papier_hors_ligne_absent", "papier" not in page.lower())

# Tactile : la carte (élément interactif principal) porte la classe
ok("I5_tactile", 'class="carte zone-tactile"' in page)

print("I5 OK —", n, "tests")
