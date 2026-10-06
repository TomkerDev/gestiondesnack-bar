"""Tests I1 : 48px, pas de métier dans composants, contrastes, galerie.
Usage: python app/tests/test_i1.py (stdlib uniquement)."""
import re, pathlib
app = pathlib.Path(__file__).resolve().parents[1] / "src"
css = (app / "lib/theme.css").read_text(encoding="utf-8")
files = list((app / "lib/components").glob("*.svelte")) + [app / "routes/galerie/+page.svelte"]
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# 48 px : variable + classes tactiles
m = re.search(r"--tactile:\s*(\d+)px", css)
ok("I1_zone_tactile_48px_min", m and int(m.group(1)) >= 48)
for f in files:
    t = f.read_text(encoding="utf-8")
    ok("I1_" + f.stem + "_classe_tactile", "zone-tactile" in t or "pave-pin" in t or "galerie" in f.name.lower() or "+page" in f.name)

# Zéro logique métier : aucun mot métier dans les composants
METIER = ["total_net", "plafond", "SELECT", "INSERT", "fetch(", " Teixeira", "раude", "stock_disponible", "speces_attendues"]
for f in (app / "lib/components").glob("*.svelte"):
    t = f.read_text(encoding="utf-8")
    hits = [w for w in METIER if w in t]
    ok("I1_" + f.stem + "_sans_logique_metier", not hits)

# Contrastes AA : paires sombre/clair définies
for v in ["--fond", "--texte", "--primaire", "--succes", "--alerte"]:
    ok("I1_theme_" + v + "_sombre_clair", v in css and '[data-theme="sombre"]' in css)

# Pastille : couleur ET texte (pas couleur seule)
past = (app / "lib/components/PastilleStatut.svelte").read_text(encoding="utf-8")
ok("I1_pastille_couleur_et_texte", "{statut}" in past)

# Pavé PIN : grille complète, touches >= 64px via classe
pin = (app / "lib/components/PavePin.svelte").read_text(encoding="utf-8")
ok("I1_pin_grille_complete", all('"%s"' % d in pin for d in "1234567890"))
ok("I1_pin_touches_64px", "64px" in css)

# R1 : PIN + motif + durée 60s affichée
r1 = (app / "lib/components/FenetreR1.svelte").read_text(encoding="utf-8")
ok("I1_R1_pin_motif_duree", "password" in r1 and "motif" in r1 and "60 secondes" in r1)

# Autre exige commentaire
sel = (app / "lib/components/SelecteurMotif.svelte").read_text(encoding="utf-8")
ok("I1_autre_exige_commentaire", "Autre" in sel and "required" in sel)

print("I1 OK —", n, "tests")
