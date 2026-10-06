"""Tests statiques I4 : écran paiement (structure, un seul action principal, ardoise).
Usage: python app/tests/test_i4.py"""
import pathlib
app = pathlib.Path(__file__).resolve().parents[1] / "src"
page = (app / "routes/paiement/+page.svelte").read_text(encoding="utf-8")
lib = (app / "lib/paiement.js").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# En haut : total net, reste à payer, monnaie à rendre
ok("I4_total_net", "Total net" in page)
ok("I4_reste_payer", "Reste à payer" in page)
ok("I4_monnaie_rendre", "Monnaie à rendre" in page)

# Une seule action principale, active seulement si reste nul
ok("I4_une_seule_action_principale", page.count("Valider le paiement") == 1)
ok("I4_valider_conditionne", "desactive={!actif}" in page)

# Règlements : espèces (reçu) et mobile (opérateur + référence obligatoires)
ok("I4_especes_reçu", "especes" in page and "Reçu" in page)
ok("I4_mobile_operateur_ref", "operateur" in page and "reference" in page)
ok("I4_mobile_obligatoire_lib", "Opérateur" in page and "Référence" in page)

# Plusieurs règlements possibles
ok("I4_reglements_multiples", "ajouterReglement" in page and "reglements as r" in page)

# Pourboire hors total
ok("I4_pourboire_hors_total", "hors total" in page and "totalAvecPourboire" in lib)

# Ardoise : bouton distinct, solde + plafond, refus + R1
ok("I4_ardoise_bouton_distinct", "Payer sur l'ardoise" in page)
ok("I4_ardoise_solde_plafond", "Solde" in page and "Plafond" in page)
ok("I4_ardoise_refus_R1", "FenetreR1" in page and "déblocage" in page)

# Hors ligne : copie locale, pas de déblocage
ok("I4_offline_pas_deblocage", "déblocage impossible" in page and "dernière copie" in lib)
ok("I4_bandeau", "BandeauConnexion" in page)

# Retour compte
ok("I4_bandeau_offline", "enLigne" in page)

# Touches 48px
ok("I4_tactile", page.count("zone-tactile") >= 6)

print("I4 OK —", n, "tests")
