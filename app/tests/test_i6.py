"""Tests statiques I6 : CAI-2 affiché, sortie en attente gérant, écart justifié, état final.
Usage: python app/tests/test_i6.py"""
import pathlib
app = pathlib.Path(__file__).resolve().parents[1] / "src"
page = (app / "routes/ma-caisse/+page.svelte").read_text(encoding="utf-8")
lib = (app / "lib/ma_caisse.js").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# Résumé : les 6 lignes de CAI-2 affichées, dans l'ordre de la formule
for libelle in ["Fond de caisse", "Espèces encaissées", "Remboursements ardoise",
                "Pourboires", "Entrées de caisse", "Sorties de caisse"]:
    ok("I6_ligne_" + libelle.replace(" ", "_"), libelle in page)
ok("I6_formule_identique", "especesAttendues" in page and "+ r.pourboires" in lib and "- r.sortiesCaisse" in lib)

# Sortie de caisse : montant + motif liste + attente gérant
ok("I6_sortie_montant", "Montant" in page and "montantSortie" in page)
ok("I6_sortie_motif_liste", "MOTIFS_SORTIE" in page and "SelecteurMotif" in page)
ok("I6_sortie_attente_gerant", "en attente de validation du gérant" in lib)

# Clôture : saisie compté, écart affiché, non nul → motif + commentaire
ok("I6_compte_saisi", "Montant compté" in page)
ok("I6_ecart_affiche", "Écart :" in page)
ok("I6_ecart_non_nul_motif", "motif et commentaire obligatoires" in page)

# État final : en attente du gérant, plus de vente
ok("I6_attente_gerant", "en attente du gérant" in page)
ok("I6_plus_de_vente", "Plus aucune vente" in page)

# Scénario exige CAI-2 dans le module (testé en node)
ok("I6_scenario_present", "57500" in pathlib.Path(__file__).with_name("ma_caisse.test.js").read_text(encoding="utf-8"))

# Entiers uniquement (step=1 sur chaque champ numérique)
ok("I6_entiers", page.count('type="number"') >= 2 and page.count('step="1"') == page.count('type="number"'))

print("I6 OK —", n, "tests")
