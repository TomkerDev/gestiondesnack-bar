"""Tests statiques d'intégration : layout, branchement des pages, client API, session.
Usage: python app/tests/test_integration.py (stdlib uniquement)."""
import pathlib
app = pathlib.Path(__file__).resolve().parents[1]
src = app / "src"
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

def lire(p): return (src / p).read_text(encoding="utf-8")

# --- 1. Scaffolding buildable (SvelteKit + adapter static) ---
for f in ["app.html", "routes/+layout.svelte", "routes/+layout.js"]:
    ok("INT_fichier_" + f.replace("/", "_"), (src / f).exists())
ok("INT_svelte_config", (app / "svelte.config.js").exists())
ok("INT_vite_config", (app / "vite.config.js").exists())
ok("INT_adapter_static", "adapter-static" in (app / "svelte.config.js").read_text(encoding="utf-8"))
ok("INT_spa_ssr_off", "ssr = false" in lire("routes/+layout.js"))

# --- 2. Layout : thème importé, bandeau global, navigation tactiles ---
layout = lire("routes/+layout.svelte")
ok("INT_layout_theme", '$lib/theme.css' in layout)
ok("INT_layout_bandeau", "BandeauConnexion" in layout and "majConnexion" in layout)
ok("INT_layout_offline_events", '"online"' in layout and '"offline"' in layout)
ok("INT_layout_resynchro", "resynchroniser" in layout)
ok("INT_layout_nav", all(h in layout for h in ["/commande", "/commandes", "/cuisine", "/paiement", "/ma-caisse", "/pc", "/pc/stock"]))

# --- 3. Client API : couche unique, pas de fetch brut dans les pages ---
api = lire("lib/api.js")
for extrait in ["INTERDIT_HORS_LIGNE", "FILE_HORS_LIGNE", "resynchroniser", "creerCommande",
                "paiement", "bonsCuisine", "cloturerCaisse", "validerEntree", "remboursement", "changerPrix"]:
    ok("INT_api_" + extrait, extrait in api)
ok("INT_api_off2", "OFF-2" in api and "OFF-3" in api)
routes = [p for p in (src / "routes").rglob("+page.svelte")]
for r in routes:
    t = r.read_text(encoding="utf-8")
    ok("INT_pas_de_fetch_brut_" + r.parent.name.replace("[id]", "detail"),
       "fetch(" not in t.split("</script>")[0].replace("fetchImpl", ""))

# --- 4. Pages branchées : chaque action principale a un handler ---
commande = lire("routes/commande/+page.svelte")
ok("INT_commande_envoyer_branche", 'on:click={envoyer}' in commande and "api.creerCommande" in commande)
ok("INT_commande_payer_branche", 'on:click={payer}' in commande)
ok("INT_commande_hors_ligne_message", "differe" in commande)

detail = lire("routes/commandes/[id]/+page.svelte")
ok("INT_detail_actions_branchees", "onAction?.(a.cle)" in detail)

liste = lire("routes/commandes/+page.svelte")
ok("INT_liste_nouvelle_branchee", "onNouvelle()" in liste and "onOuvrir(c.id)" in liste)

# --- 5. Session : SEC-1 testée, store branché au layout ---
session = lire("lib/session.js")
ok("INT_session_sec1", "SEC-1" in session and "identifiant" in session)
ok("INT_session_store_compatible", "subscribe" in session and "set" in session)

# --- 6. npm test inclut la passe d'intégration ---
pkg = (app / "package.json").read_text(encoding="utf-8")
ok("INT_npm_test_integration", "test_integration.py" in pkg)
ok("INT_npm_test_api", "node --test" in pkg)

print("Integration OK —", n, "tests")
