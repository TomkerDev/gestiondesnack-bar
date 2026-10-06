"""Tests statiques I2 : structure écran (filtres, barre, hors-ligne, 1 appui).
Usage: python app/tests/test_i2.py (stdlib uniquement)."""
import pathlib
app = pathlib.Path(__file__).resolve().parents[1] / "src"
page = (app / "routes/commande/+page.svelte").read_text(encoding="utf-8")
panier = (app / "lib/panier.js").read_text(encoding="utf-8")
n = 0

def ok(nom, cond=True):
    global n
    assert cond, "FAIL " + nom
    n += 1; print("OK", nom)

# Catalogue : grille unique, 5 filtres imposés, pas de recherche ni favoris
for f in ["Tout", "Bières", "Softs", "Alcools", "Plats"]:
    ok("I2_filtre_" + f, '"%s"' % f in page)
ok("I2_pas_de_recherche", "recherche" not in page.lower() and "placeholder" not in page)
ok("I2_pas_de_favoris", "favori" not in page.lower())

# Barre fixe : articles, total, Envoyer en cuisine (côté aside + barre)
ok("I2_bouton_envoyer", "Envoyer en cuisine" in page)
ok("I2_bouton_payer", "Payer" in page)
ok("I2_compteur_articles", "nbArticles" in page and "total" in page)

# Un appui = +1 : la page appelle ajouter() une fois par clic, pas de quantité explicite
ok("I2_un_appui_un_ajout", page.count("ajouter(panier, produit)") == 1 and "+= 1" not in page)

# Retrait via pastille + Annuler discret
ok("I2_retrait_pastille", "touchePastille" in page and "retirer(" in page)
ok("I2_annuler_discret", "annuler" in page and "Annuler" in page)

# Prix figé dans le module panier (copie du prix)
ok("I2_prix_figé_copié", "prix: produit.prix" in panier)

# Stock zéro non bloquant : aucune CONDITION de stock dans l'UI (le mot en commentaire est admis)
sans_commentaires = "\n".join(
    l.split("<!--")[0] for l in page.splitlines() if not l.strip().startswith(("<!--", "*/", "*"))
)
ok("I2_stock_non_bloquant", not any(t in sans_commentaires for t in ["stock <", "stock >", "quantiteStock", "rupture", "disponible"]))

# Hors ligne : bandeau présent, fonctionne comme en ligne
ok("I2_bandeau_hors_ligne", "BandeauConnexion" in page and "enLigne" in page)

# Cuisine : statut envoyé figé
ok("I2_envoi_cuisine_statut", 'statutCuisine: "envoyé"' in panier)

print("I2 OK —", n, "tests")
