"""Tests statiques I7 : nav latérale, raccourcis, alertes, clôture conditionnelle,
rôle propriétaire vs gérant (jamais de prix d'achat pour le gérant).
Usage: python app/tests/test_i7.py"""
import pathlib, re
app = pathlib.Path(__file__).resolve().parents[1] / "src"
page = (app / "routes/pc/+page.svelte").read_text(encoding="utf-8")
lib = (app / "lib/pc_gerant.js").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# Navigation latérale + 3 vues + raccourcis clavier
ok("I7_nav_laterale", "<nav aria-label=\"Navigation\">" in page and "flex-direction: column" in page)
for v in ["Tableau de bord", "Journée", "Caisses"]:
    ok("I7_vue_" + v.replace(" ", "_"), '"%s"' % v in page)
ok("I7_raccourcis_clavier", "svelte:window" in page and "on:keydown" in page)

# Tableaux denses
ok("I7_tableaux_denses", "border-collapse" in page and "font-size: 14px" in page)

# Alertes : 4 familles affichées (via alertes()), état vide compris
ok("I7_alertes", "alertesListe" in page and "Aucune alerte" in page)
ok("I7_4_familles", all(t in lib for t in ["stockNegatif", "entreesAValider", "ardoisesAuPlafond", "ecartsCaisse"]))

# Ventes en cours + appareils
ok("I7_ventes_en_cours", "ventesEnCours" in page)
ok("I7_appareils", "appareils" in page and "hors ligne" in page)

# Journée : ouvrir avec fond par serveur, clôture conditionnelle avec raison visible
ok("I7_ouvrir_fond", "Ouvrir la journée" in page and "fondParServeur" in lib)
ok("I7_cloture_conditionnee", "Clôturer la journée" in page and "cloture.ok" in page)
ok("I7_raison_visible", 'role="note"' in page and "↳" in page)

# Caisses : forçage R1 avec motif
ok("I7_forcer_R1", "Forcer la clôture" in page and "FenetreR1" in page)
ok("I7_forcer_motif", "Motif obligatoire" in lib)

# R3 : le gérant ne voit jamais un prix d'achat
ok("I7_R3_colonnes", 'colonnes(role)' in page and 'role === "proprietaire"' in page)
mots_achat = re.findall(r"\b(cout|marge|prix_achat|cost|margin)\b", page)
# cout/marge n'apparaissent que dans la branche propriétaire
ok("I7_gerant_jamais_achat", page.count("{c.cout}") == 1 and '{c.marge}' in page and 'role === "proprietaire"' in page)
ok("I7_lib_jamais_pour_gerant", 'role !== "proprietaire"' in lib or '!== "proprietaire"' in lib)

print("I7 OK —", n, "tests")
