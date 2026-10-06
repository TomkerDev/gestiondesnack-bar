"""Serveur local du snack-bar — miroir EXÉCUTABLE du back axum (Tauri/Rust).

Ce serveur Python (stdlib uniquement) exécute le contrat HTTP consommé par
app/src/lib/api.js (les règles font foi dans core/ Rust, vérifiées par cargo test) :
mêmes chemins, mêmes règles (spec v1.2), mêmes réponses {ok | raison}.

- SQLite + les 5 migrations de db/migrations (M1) ; ajout seul via les triggers.
- Montants entiers ; journée obligatoire pour vendre (R2) ; prix figés par
  ligne au moment de l'insertion (PRX-3).
- SEC-1 : identification par code ≥ 4 chiffres, blocage 5 min puis 15 min.
- STK-4 : entrées « à valider » hors disponible, validation par une autre
  personne, rejet SANS mouvement inverse.
- CAI-2 : fond + espèces − remboursements + pourboires + entrées − sorties.
- Sert aussi le build statique (app/build) si présent : une seule origine.

Usage : python serveur/serveur.py [port]   (défaut 8080)"""

import json
import hashlib
import os
import re
import sqlite3
import sys
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RACINE = Path(__file__).resolve().parents[1]
MIGRATIONS = sorted((RACINE / "db" / "migrations").glob("*.sql"))
BUILD = RACINE / "app" / "build"
# SNACK_DB : base alternative (tests sur base jetable) ; défaut : serveur/snack.db
CHEMIN_BASE = Path(os.environ.get("SNACK_DB", RACINE / "serveur" / "snack.db"))

# ---------------------------------------------------------------- horodatage
def maintenant():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def heure_locale():
    return datetime.now().strftime("%H:%M")

# ------------------------------------------------------------------ base
def base_donnees(chemin=CHEMIN_BASE):
    conn = sqlite3.connect(chemin, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialiser(chemin=CHEMIN_BASE):
    """Applique les migrations M1 si la base est neuve, puis graine les référentiels."""
    conn = base_donnees(chemin)
    deja = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if not deja:
        for f in MIGRATIONS:
            conn.executescript(f.read_text(encoding="utf-8"))
        graine(conn)
        conn.commit()
    conn.close()

def _uuid(): return str(uuid.uuid4())

def _hash_pin(pin, sel): return hashlib.sha256((sel + ":" + pin).encode()).hexdigest()

def graine(conn):
    """Référentiels de démarrage : personnel, catalogue, ardoises, journée ouverte, caisse."""
    now = maintenant()
    users = [
        ("u-awa", "Awa", "serveur", "1234"),
        ("u-moussa", "Moussa", "serveur", "2222"),
        ("u-ibrahima", "Ibrahim", "gerant", "9111"),
        ("u-hassane", "Hassane", "proprietaire", "9999"),
    ]
    for uid, nom, role, pin in users:
        sel = uuid.uuid4().hex[:8]
        conn.execute(
            "INSERT INTO users (id, nom, role, pin_hash, pin_salt, peut_saisir_entrees, cree_le) VALUES (?,?,?,?,?,?,?)",
            (uid, nom, role, _hash_pin(pin, sel), sel, 1 if role != "serveur" else 0, now))
    produits = [
        # (id, nom, type, alcoolise, suivi_stock, prix_vente, prix_achat, cout_estime)
        ("p-biere65", "Bière 65cl", "boisson", 1, 1, 1500, 900, 700),
        ("p-biere33", "Bière 33cl", "boisson", 1, 1, 1000, 600, 450),
        ("p-eau", "Eau 1,5L", "boisson", 0, 1, 700, 400, 300),
        ("p-soda", "Soda 33cl", "boisson", 0, 1, 500, 250, 200),
        ("p-jus", "Jus d'orange", "boisson", 0, 1, 1000, 550, 400),
        ("p-whisky", "Whisky 70cl (bouteille)", "boisson", 1, 1, 15000, 10500, 9000),
        ("p-attiéké", "Attiéké poisson", "plat", 0, 0, 2500, None, 1400),
        ("p-poulet", "Poulet braisé", "plat", 0, 0, 3000, None, 1800),
    ]
    for pid, nom, typ, alco, stock, pv, pa, ce in produits:
        conn.execute(
            "INSERT INTO products (id, nom, type, est_alcoolise, suivi_stock, prix_vente, prix_achat, cout_estime, cree_le) VALUES (?,?,?,?,?,?,?,?,?)",
            (pid, nom, typ, alco, stock, pv, pa, ce, now))
    conn.execute("INSERT INTO clients (id, nom, telephone, plafond, cree_le) VALUES ('c-koffi','Koffi','+225 01 02 03', 10000, ?)", (now,))
    conn.execute("INSERT INTO clients (id, nom, telephone, plafond, cree_le) VALUES ('c-adja','Adja',NULL, 5000, ?)", (now,))
    conn.execute("INSERT INTO journees (id, statut, ouverte_le, ouverte_par) VALUES ('j-1','ouverte',?, 'u-ibrahima')", (now,))
    conn.execute("INSERT INTO caisses (id, journee_id, serveur_id, fond, statut) VALUES ('k-1','j-1','u-awa', 5000, 'ouverte')", ())

def categorie(p):
    """Catégories de l'écran I2 (filtres imposés) dérivées du référentiel M1."""
    if p["type"] == "plat": return "Plats"
    if p["est_alcoolise"] and "bière" in p["nom"].lower(): return "Bières"
    if p["est_alcoolise"]: return "Alcools"
    return "Softs"

STATUT_CUISINE_UI = {"non_envoye": "non envoyé", "envoye": "envoyé", "envoye_papier": "envoyé",
                     "en_preparation": "en préparation", "pret": "prêt", "servi": "prêt", "annule": "annulé"}
STATUT_COMMANDE_UI = {"ouverte": "ouverte", "payee": "payée", "payee_sans_addition": "payée", "annulee": "annulé"}


# ------------------------------------------------------------- helpers métier
def journee_ouverte(conn):
    return conn.execute("SELECT * FROM journees WHERE statut='ouverte' ORDER BY ouverte_le DESC LIMIT 1").fetchone()

def dispo(conn, produit_id, journee_id):
    """STK-2 : disponible = somme des mouvements (pas d'écriture recalculée)."""
    row = conn.execute("SELECT COALESCE(SUM(quantite),0) AS s FROM mouvements_stock WHERE produit_id=? AND journee_id=?",
                       (produit_id, journee_id)).fetchone()
    return row["s"]

def attente(conn, produit_id, journee_id):
    """STK-4 : quantités saisies « à valider », hors disponible."""
    row = conn.execute("""SELECT COALESCE(SUM(el.quantite),0) AS s FROM entree_lignes el
                          JOIN entrees_stock e ON e.id = el.entree_id
                          WHERE el.produit_id=? AND e.journee_id=? AND e.statut='a_valider'""",
                       (produit_id, journee_id)).fetchone()
    return row["s"]

def solde_ardoise(conn, client_id):
    row = conn.execute("""SELECT COALESCE(SUM(CASE WHEN sens='vente' THEN montant ELSE -montant END),0) AS s
                          FROM ardoise_mouvements WHERE client_id=?""", (client_id,)).fetchone()
    return row["s"]

def _table_existe(conn, nom):
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (nom,)).fetchone() is not None

def etat_caisse(conn, serveur_id, journee_id):
    """CAI-2 : fond + espèces − remboursements + pourboires + entrées − sorties."""
    k = conn.execute("SELECT * FROM caisses WHERE journee_id=? AND serveur_id=?", (journee_id, serveur_id)).fetchone()
    if not k: return None
    q = lambda sql, *a: conn.execute(sql, *a).fetchone()["s"]
    especes = q("""SELECT COALESCE(SUM(r.montant),0) AS s FROM reglements r
                   JOIN commandes c ON c.id=r.commande_id
                   WHERE r.mode='especes' AND r.serveur_id=? AND c.journee_id=?""", serveur_id, journee_id)
    remboursements = q("""SELECT COALESCE(SUM(m.montant),0) AS s FROM ardoise_mouvements m
                          WHERE m.sens='remboursement' AND m.serveur_id=? AND m.journee_id=?""", serveur_id, journee_id)
    pourboires = q("""SELECT COALESCE(SUM(r.pourboire),0) AS s FROM reglements r
                      JOIN commandes c ON c.id=r.commande_id WHERE r.serveur_id=? AND c.journee_id=?""",
                   serveur_id, journee_id)
    entrees = q("SELECT COALESCE(SUM(montant),0) AS s FROM entrees_caisse WHERE serveur_id=? AND journee_id=?",
                serveur_id, journee_id) if _table_existe(conn, "entrees_caisse") else 0
    sorties = q("SELECT COALESCE(SUM(montant),0) AS s FROM sorties_caisse WHERE serveur_id=? AND journee_id=? AND statut='validee'",
                serveur_id, journee_id)
    attendu = k["fond"] + especes - remboursements + pourboires + entrees - sorties
    return {"fondCaisse": k["fond"], "especesEncaissees": especes, "remboursementsArdoise": remboursements,
            "pourboires": pourboires, "entreesCaisse": entrees, "sortiesCaisse": sorties,
            "attendu": attendu, "statut": k["statut"], "ecart": k["ecart"], "caisseId": k["id"]}

def commande_vers_ui(conn, cid):
    """Forme attendue par les écrans I3 (destination/table/lignes/statutCuisine)."""
    c = conn.execute("SELECT * FROM commandes WHERE id=?", (cid,)).fetchone()
    if not c: return None
    lignes = conn.execute("""SELECT l.*, p.nom FROM lignes l JOIN products p ON p.id=l.produit_id
                             WHERE l.commande_id=? ORDER BY l.cree_le""", (cid,)).fetchall()
    return {"id": c["id"], "destination": c["mode"], "table": c["table_nom"],
            "serveur": c["serveur_id"], "statut": STATUT_COMMANDE_UI.get(c["statut"], c["statut"]),
            "total": c["total_net"], "nAddition": c["n_addition"],
            "lignes": [{"id": l["id"], "nom": l["nom"], "quantite": l["quantite"],
                        "prix": l["prix_unitaire_fige"], "net": l["quantite"] * l["prix_unitaire_fige"],
                        "statutCuisine": STATUT_CUISINE_UI.get(l["statut_cuisine"], l["statut_cuisine"])}
                       for l in lignes]}

def _utilisateur_public(u):
    return {"id": u["id"], "nom": u["nom"], "role": u["role"]}

def _montant(valeur, nom="montant"):
    """Valide un montant entier > 0 (spec : i64 petite unité, jamais de flottant)."""
    if isinstance(valeur, bool) or not isinstance(valeur, int) or valeur <= 0:
        raise ValueError("Montant invalide pour « %s » : entier > 0 attendu" % nom)
    return valeur

def _journee_id(conn):
    """R2 : toute vente se rattache à la journée ouverte, jamais à la date civile."""
    j = journee_ouverte(conn)
    if not j:
        raise ValueError("Aucune journée ouverte (R2)")
    return j["id"]

def identifier(conn, code):
    """SEC-1 : code >= 4 chiffres ; 5 echecs => 5 min, 6e et + => 15 min."""
    code = (code or "").strip()
    if len(code) < 4 or not code.isdigit():
        return None, "Code trop court (SEC-1 : 4 chiffres minimum)"
    now = maintenant()
    users = conn.execute("SELECT * FROM users WHERE est_actif=1").fetchall()
    for u in users:
        if u["bloque_jusquau"] and u["bloque_jusquau"] > now:
            continue  # encore bloque, on ne revele pas qui
        if u["pin_hash"] == _hash_pin(code, u["pin_salt"]):
            if u["bloque_jusquau"] and u["bloque_jusquau"] <= now:
                pass  # bloc expire, on laisse passer
            conn.execute("UPDATE users SET echecs_pin=0, bloque_jusquau=NULL WHERE id=?", (u["id"],))
            conn.commit()
            return _utilisateur_public(u), None
    # echec : on penalise le premier compte non bloque (anti-enumeration sommaire)
    candidat = [u for u in users if not (u["bloque_jusquau"] and u["bloque_jusquau"] > now)]
    if candidat:
        u = candidat[0]
        nb = (u["echecs_pin"] or 0) + 1
        if nb == 5:
            from datetime import timedelta
            b = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            conn.execute("UPDATE users SET echecs_pin=?, bloque_jusquau=? WHERE id=?", (nb, b, u["id"]))
        elif nb >= 6:
            from datetime import timedelta
            b = (datetime.now(timezone.utc) + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            conn.execute("UPDATE users SET echecs_pin=?, bloque_jusquau=? WHERE id=?", (nb, b, u["id"]))
        else:
            conn.execute("UPDATE users SET echecs_pin=? WHERE id=?", (nb, u["id"]))
        conn.commit()
    return None, "Code inconnu"

def catalogue(conn):
    """I2 : produits actifs + dispo STK-2 + attente STK-4."""
    j = journee_ouverte(conn)
    jid = j["id"] if j else None
    rows = conn.execute("SELECT * FROM products WHERE est_actif=1 ORDER BY nom").fetchall()
    out = []
    for p in rows:
        d = dict(p)
        d["categorie"] = categorie(d)
        d["prix"] = d["prix_vente"]
        d["dispo"] = dispo(conn, d["id"], jid) if jid else 0
        d["attente"] = attente(conn, d["id"], jid) if jid else 0
        out.append({k: d[k] for k in ("id", "nom", "type", "prix", "categorie", "dispo", "attente")})
    return out

def bons_cuisine(conn):
    """I5 : bons envoyes + lignes rattachees."""
    bons = conn.execute("""SELECT * FROM bons_cuisine WHERE statut='envoye' AND EXISTS (
        SELECT 1 FROM lignes WHERE lignes.bon_id = bons_cuisine.id
        AND lignes.statut_cuisine NOT IN ('servi','annule')) ORDER BY n_bon""").fetchall()
    out = []
    for b in bons:
        cu = commande_vers_ui(conn, b["commande_id"])
        out.append({"id": b["id"], "nBon": b["n_bon"], "commandeId": b["commande_id"],
                    "commande": cu, "creeLe": b["cree_le"]})
    return out

def entrees(conn):
    """I7 : entrees a valider + validees du jour, avec lignes."""
    rows = conn.execute("SELECT * FROM entrees_stock ORDER BY saisie_le DESC LIMIT 50").fetchall()
    out = []
    for e in rows:
        lignes = conn.execute("""SELECT el.*, p.nom FROM entree_lignes el
                                 JOIN products p ON p.id=el.produit_id WHERE el.entree_id=?""",
                              (e["id"],)).fetchall()
        out.append({"id": e["id"], "statut": e["statut"], "saisiePar": e["saisie_par"],
                    "valideePar": e["validee_par"], "motifRejet": e["motif_rejet"],
                    "lignes": [{"produit": l["produit_id"], "nom": l["nom"],
                                "quantite": l["quantite"]} for l in lignes]})
    return out

def ardoises(conn):
    """I6 : clients + plafond + solde courant."""
    rows = conn.execute("SELECT * FROM clients WHERE est_actif=1 ORDER BY nom").fetchall()
    return [{"id": c["id"], "nom": c["nom"], "telephone": c["telephone"],
             "plafond": c["plafond"], "solde": solde_ardoise(conn, c["id"])} for c in rows]

def commandes(conn, serveur):
    """I3 : commandes du serveur (ou toutes si vide), forme UI."""
    if serveur:
        rows = conn.execute("SELECT id FROM commandes WHERE serveur_id=? ORDER BY cree_le DESC LIMIT 50",
                            (serveur,)).fetchall()
    else:
        rows = conn.execute("SELECT id FROM commandes ORDER BY cree_le DESC LIMIT 50").fetchall()
    return [c for c in (commande_vers_ui(conn, r["id"]) for r in rows) if c]

def caisse(conn, journee_id, serveur_id):
    """Wrapper : le routeur appelle caisse(conn, journee, serveur)."""
    e = etat_caisse(conn, serveur_id, journee_id)
    if e is None:
        return {"fondCaisse": 0, "especesEncaissees": 0, "remboursementsArdoise": 0,
                "pourboires": 0, "entreesCaisse": 0, "sortiesCaisse": 0,
                "attendu": 0, "statut": "sans_caisse", "ecart": 0, "caisseId": None}
    return e

def auditer(conn, qui, quoi, commande_id=None, motif=None, detail=None):
    conn.execute("INSERT INTO audit_log (qui, quoi, commande_id, motif, detail) VALUES (?,?,?,?,?)",
                 (qui, quoi, commande_id, motif, detail))

# --------------------------------------------------------------- HTTP
class Gestionnaire(BaseHTTPRequestHandler):
    server_version = "SnackBar/1.0"

    def log_message(self, fmt, *args):  # trace minimaliste en console
        if self.path.startswith("/api/"):
            sys.stderr.write("[serveur] %s %s\n" % (self.command, self.path))

    def _json(self, data, status=200):
        corps = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)

    def _erreur(self, raison, status=409):
        self._json({"ok": False, "raison": raison}, status)

    def _corps(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n == 0: return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8")) or {}
        except (ValueError, UnicodeDecodeError):
            return {}

    def do_GET(self):
        u = urlparse(self.path)
        if u.path.startswith("/api/"):
            self._route("GET", u.path, parse_qs(u.query))
        else:
            self._statique(u.path)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path.startswith("/api/"):
            self._route("POST", u.path, parse_qs(u.query), self._corps())
        else:
            self._erreur("Route inconnue", 404)

    def _route(self, methode, chemin, query, corps=None):
        corps = corps or {}
        conn = base_donnees()
        try:
            self._router(conn, methode, chemin, query, corps)
        except ValueError as e:  # règle métier violée (spec v1.2) → 409 + raison
            conn.rollback()
            self._erreur(str(e), 409)
        except sqlite3.IntegrityError as e:
            self._erreur("Règle de base violée : " + str(e), 409)
        except Exception as e:  # jamais d'exception brute côté client (contrat api.js)
            conn.rollback()
            self._erreur("Erreur serveur : " + str(e), 500)
        finally:
            conn.close()

    # ---------------------------------------------------------- statique
    def _statique(self, chemin):
        if not BUILD.is_dir():
            return self._erreur("Aucun build front — lancez npm run build", 503)
        rel = chemin.lstrip("/") or "index.html"
        f = (BUILD / rel).resolve()
        if not str(f).startswith(str(BUILD.resolve())) or not f.is_file():
            f = BUILD / "index.html"  # SPA fallback
            if not f.is_file():
                return self._erreur("Fichier introuvable", 404)
        data = f.read_bytes()
        types = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
                 ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
                 ".json": "application/json; charset=utf-8", ".ico": "image/x-icon", ".woff2": "font/woff2"}
        self.send_response(200)
        self.send_header("Content-Type", types.get(f.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---------------------------------------------------------- routeur
    def _router(self, conn, methode, chemin, query, corps):
        # --- GET lecture ------------------------------------------------
        if methode == "GET" and chemin == "/api/produits":
            return self._json({"ok": True, "produits": catalogue(conn)})
        if methode == "GET" and chemin == "/api/cuisine/bons":
            return self._json({"ok": True, "bons": bons_cuisine(conn)})
        if methode == "GET" and chemin == "/api/stock/entrees":
            return self._json({"ok": True, "entrees": entrees(conn)})
        if methode == "GET" and chemin == "/api/ardoises":
            return self._json({"ok": True, "ardoises": ardoises(conn)})
        if methode == "GET" and chemin == "/api/commandes":
            srv = (query.get("serveur") or [""])[0]
            return self._json({"ok": True, "commandes": commandes(conn, srv)})
        if methode == "GET" and chemin == "/api/caisse":
            srv = (query.get("serveur") or [""])[0]
            j = journee_ouverte(conn)
            if not j:
                return self._erreur("Aucune journée ouverte (R2)")
            return self._json({"ok": True, "caisse": caisse(conn, j["id"], srv)})
        # --- POST session (SEC-1) ------------------------------------------
        if methode == "POST" and chemin == "/api/session":
            code = str(corps.get("code") or "")
            return self._session(conn, code)
        # --- POST commandes (CMD-1/CMD-4/CMD-6, R2, PRX-3) -------------------
        if methode == "POST" and chemin == "/api/commandes":
            return self._creer_commande(conn, corps)
        m = re.match(r"^/api/commandes/([^/]+)/lignes$", chemin)
        if methode == "POST" and m:
            return self._ajouter_lignes(conn, m.group(1), corps)
        m = re.match(r"^/api/commandes/([^/]+)/envoyer$", chemin)
        if methode == "POST" and m:
            return self._envoyer_cuisine(conn, m.group(1))
        m = re.match(r"^/api/commandes/([^/]+)/paiement$", chemin)
        if methode == "POST" and m:
            regs = corps.get("reglements") or []
            return self._payer(conn, m.group(1), regs)
        # --- POST cuisine (CUI-3) --------------------------------------------
        m = re.match(r"^/api/cuisine/bons/([^/]+)/avancer$", chemin)
        if methode == "POST" and m:
            return self._avancer_bon(conn, m.group(1))
        # --- POST caisse / journée (CAI-1..5, R2/R5) --------------------------
        if methode == "POST" and chemin == "/api/caisse/sortie":
            return self._sortie_caisse(conn, corps)
        if methode == "POST" and chemin == "/api/caisse/cloture":
            return self._cloturer_caisse(conn, corps)
        if methode == "POST" and chemin == "/api/journee/cloturer":
            return self._cloturer_journee(conn)
        # --- POST stock (STK-4/STK-5, double contrôle) -----------------------
        m = re.match(r"^/api/stock/entrees/([^/]+)/valider$", chemin)
        if methode == "POST" and m:
            return self._valider_entree(conn, m.group(1), corps)
        m = re.match(r"^/api/stock/entrees/([^/]+)/rejeter$", chemin)
        if methode == "POST" and m:
            return self._rejeter_entree(conn, m.group(1), corps)
        if methode == "POST" and chemin == "/api/stock/inventaire":
            return self._inventaire(conn, corps)
        # --- POST ardoises / prix (ARD, PRX-1/R3, audit SEC-3) ---------------
        m = re.match(r"^/api/ardoises/([^/]+)/plafond$", chemin)
        if methode == "POST" and m:
            return self._plafond(conn, m.group(1), corps)
        m = re.match(r"^/api/ardoises/([^/]+)/remboursement$", chemin)
        if methode == "POST" and m:
            return self._remboursement(conn, m.group(1), corps)
        m = re.match(r"^/api/produits/([^/]+)/prix$", chemin)
        if methode == "POST" and m:
            return self._changer_prix(conn, m.group(1), corps)
        return self._erreur("Route inconnue", 404)

    # ------------------------------------------------- handlers POST
    def _serveur(self, conn, corps):
        """Serveur auteur de l'acte (v1 : champ optionnel, défaut Awa)."""
        sid = corps.get("serveur") or "u-awa"
        u = conn.execute("SELECT id FROM users WHERE id=? AND est_actif=1", (sid,)).fetchone()
        return u["id"] if u else "u-awa"

    def _role(self, conn, uid):
        u = conn.execute("SELECT role FROM users WHERE id=?", (uid,)).fetchone()
        return u["role"] if u else None

    def _exige_roles(self, conn, uid, roles, acte):
        if self._role(conn, uid) not in roles:
            raise ValueError("Droit insuffisant pour « %s » (rôle requis : %s)" % (acte, "/".join(roles)))

    def _net_lignes(self, lignes):
        total = 0
        for l in lignes:
            if l["est_offert"]:
                continue
            brut = l["quantite"] * l["prix_unitaire_fige"]
            if l["remise_type"] == "montant":
                total += brut - (l["remise_valeur"] or 0)
            elif l["remise_type"] == "pourcent":
                total += brut * (100 - (l["remise_valeur"] or 0)) // 100
            else:
                total += brut
        return total

    def _recalculer_totaux(self, conn, cid):
        lignes = conn.execute("SELECT * FROM lignes WHERE commande_id=?", (cid,)).fetchall()
        brut = sum(l["quantite"] * l["prix_unitaire_fige"] for l in lignes)
        net = self._net_lignes([dict(l) for l in lignes])
        conn.execute("UPDATE commandes SET total_brut=?, total_net=?, version=version+1 WHERE id=?",
                     (brut, net, cid))

    def _inserer_ligne(self, conn, cid, item):
        pid = item.get("produit") or item.get("produit_id") or item.get("id")
        qte = item.get("quantite", item.get("qte", 1))
        if isinstance(qte, bool) or not isinstance(qte, int) or qte <= 0:
            raise ValueError("Quantité invalide pour la ligne")
        p = conn.execute("SELECT * FROM products WHERE id=? AND est_actif=1", (pid,)).fetchone()
        if not p:
            raise ValueError("Produit inconnu ou inactif : %s" % pid)
        lid = _uuid()
        conn.execute(
            "INSERT INTO lignes (id, commande_id, produit_id, quantite, prix_unitaire_fige, cout_unitaire_fige)"
            " VALUES (?,?,?,?,?,?)",
            (lid, cid, pid, qte, p["prix_vente"], p["cout_estime"] or 0))  # PRX-3 : prix/coût figés
        return lid

    def _ouverte(self, conn, cid):
        c = conn.execute("SELECT * FROM commandes WHERE id=?", (cid,)).fetchone()
        if not c:
            raise ValueError("Commande introuvable")
        if c["statut"] != "ouverte":
            raise ValueError("Commande déjà %s (R4 : correction = nouvel enregistrement)" % c["statut"])
        return c

    # --- session (SEC-1) ---
    def _session(self, conn, code):
        u, raison = identifier(conn, code)
        if not u:
            return self._erreur(raison, 401)
        return self._json({"ok": True, "utilisateur": u})

    # --- commandes (CMD-1/CMD-4/CMD-6, R2, PRX-3) ---
    def _creer_commande(self, conn, corps):
        lignes = corps.get("lignes") or []
        if not lignes:
            raise ValueError("Commande vide : ajoutez au moins une ligne")
        jid = _journee_id(conn)  # R2 : jamais sans journée ouverte
        serveur = self._serveur(conn, corps)
        mode = corps.get("mode") if corps.get("mode") in ("table", "comptoir") else "comptoir"
        cid = _uuid()
        conn.execute(
            "INSERT INTO commandes (id, journee_id, serveur_id, table_nom, mode) VALUES (?,?,?,?,?)",
            (cid, jid, serveur, corps.get("table"), mode))  # CMD-6 : UUID local, CMD-1 : mode
        for item in lignes:
            self._inserer_ligne(conn, cid, item)
        self._recalculer_totaux(conn, cid)
        auditer(conn, serveur, "commande_creee", cid, None,
                json.dumps({"lignes": len(lignes)}, ensure_ascii=False))
        conn.commit()
        return self._json({"ok": True, "commande": commande_vers_ui(conn, cid)})

    def _ajouter_lignes(self, conn, cid, corps):
        c = self._ouverte(conn, cid)
        lignes = corps.get("lignes") or []
        if not lignes:
            raise ValueError("Aucune ligne à ajouter")
        for item in lignes:
            self._inserer_ligne(conn, cid, item)
        self._recalculer_totaux(conn, cid)
        auditer(conn, c["serveur_id"], "lignes_ajoutees", cid, None,
                json.dumps({"lignes": len(lignes)}, ensure_ascii=False))
        conn.commit()
        return self._json({"ok": True, "commande": commande_vers_ui(conn, cid)})

    # --- envoi cuisine (CUI-1) ---
    def _envoyer_cuisine(self, conn, cid):
        c = self._ouverte(conn, cid)
        reste = conn.execute(
            "SELECT * FROM lignes WHERE commande_id=? AND statut_cuisine='non_envoye'",
            (cid,)).fetchall()
        if not reste:
            raise ValueError("Aucune ligne a envoyer en cuisine")
        conn.execute("UPDATE compteurs SET valeur=valeur+1 WHERE nom='n_bon'")
        n = conn.execute("SELECT valeur FROM compteurs WHERE nom='n_bon'").fetchone()["valeur"]
        bid = _uuid()
        conn.execute("INSERT INTO bons_cuisine (id, n_bon, commande_id) VALUES (?,?,?)",
                     (bid, n, cid))
        conn.execute("UPDATE lignes SET statut_cuisine='envoye', bon_id=?"
                     " WHERE commande_id=? AND statut_cuisine='non_envoye'", (bid, cid))
        auditer(conn, c["serveur_id"], "bon_envoye", cid, None,
                json.dumps({"bon": bid, "n_bon": n}, ensure_ascii=False))
        conn.commit()
        return self._json({"ok": True, "bon": bid, "nBon": n})

    # --- paiement (PAI-1..4, PAI-6, ARD-2, STK-3, R2) ---
    def _payer(self, conn, cid, regs):
        c = self._ouverte(conn, cid)
        if not regs:
            raise ValueError("Aucun reglement")
        jid = _journee_id(conn)
        net = c["total_net"]
        somme = 0
        ardoise = None
        for r in regs:
            mode = r.get("mode")
            if mode not in ("especes", "mobile", "ardoise"):
                raise ValueError("Mode de reglement inconnu")
            montant = _montant(r.get("montant"))
            tip = r.get("pourboire") or 0
            if isinstance(tip, bool) or not isinstance(tip, int) or tip < 0:
                raise ValueError("Pourboire invalide (PAI-6 : hors total)")
            if mode == "especes":
                recu = r.get("montant_recu")
                rendue = r.get("monnaie_rendue") or 0
                if not isinstance(recu, int) or recu < montant or recu - montant != rendue:
                    raise ValueError("Especes incoherentes (PAI-3)")
            if mode == "mobile":
                if not r.get("operateur") or not r.get("reference_operateur"):
                    raise ValueError("Mobile : operateur et reference obligatoires (PAI-4)")
            if mode == "ardoise":
                ardoise = r
            somme += montant
        if ardoise and len(regs) > 1:
            raise ValueError("Ardoise : paiement exclusif (PAI-2)")
        if somme != net:
            raise ValueError("Total inexact : %d attendu, %d recu (PAI-2)" % (net, somme))
        alertes = []
        if ardoise:
            cli = ardoise.get("client_id") or ardoise.get("client")
            if not cli:
                raise ValueError("Ardoise : client identifie exige (ARD-2)")
            cl = conn.execute("SELECT * FROM clients WHERE id=? AND est_actif=1", (cli,)).fetchone()
            if not cl:
                raise ValueError("Client ardoise inconnu")
            solde = solde_ardoise(conn, cli)
            if solde + net > cl["plafond"]:
                raise ValueError("Plafond depasse (ARD-2)")
            conn.execute("INSERT INTO ardoise_mouvements"
                         " (id, client_id, commande_id, journee_id, sens, montant, serveur_id)"
                         " VALUES (?,?,?,?,?,?,?)",
                         (_uuid(), cli, cid, jid, "vente", net, c["serveur_id"]))
        for r in regs:
            rappro = "a_rapprocher" if r.get("mode") == "mobile" else "non_applicable"
            cli_r = (ardoise.get("client_id") or ardoise.get("client")) if r.get("mode") == "ardoise" else None
            conn.execute("INSERT INTO reglements (id, commande_id, journee_id, serveur_id,"
                         " mode, montant, montant_recu, monnaie_rendue, operateur,"
                         " reference_operateur, statut_rapprochement, pourboire, client_id)"
                         " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (_uuid(), cid, jid, c["serveur_id"], r.get("mode"), _montant(r.get("montant")),
                          r.get("montant_recu"), r.get("monnaie_rendue") or 0,
                          r.get("operateur"), r.get("reference_operateur"), rappro,
                          r.get("pourboire") or 0, cli_r))
        for l in conn.execute("SELECT * FROM lignes WHERE commande_id=?", (cid,)).fetchall():
            p = conn.execute("SELECT suivi_stock FROM products WHERE id=?", (l["produit_id"],)).fetchone()
            if p and p["suivi_stock"]:
                conn.execute("INSERT INTO mouvements_stock"
                             " (id, produit_id, journee_id, quantite, type, commande_id, cree_par)"
                             " VALUES (?,?,?,?,?,?,?)",
                             (_uuid(), l["produit_id"], jid, -l["quantite"], "vente", cid, c["serveur_id"]))
                if dispo(conn, l["produit_id"], jid) < 0:
                    alertes.append("Stock negatif apres vente (STK-3)")
                    break
        conn.execute("UPDATE commandes SET statut='payee', version=version+1 WHERE id=?", (cid,))
        auditer(conn, c["serveur_id"], "commande_payee", cid, None,
                json.dumps({"total": net}, ensure_ascii=False))
        conn.commit()
        return self._json({"ok": True, "commande": commande_vers_ui(conn, cid), "alertes": alertes})
    # --- avancement bon cuisine (CUI-3) ---
    def _avancer_bon(self, conn, bid):
        b = conn.execute("SELECT * FROM bons_cuisine WHERE id=?", (bid,)).fetchone()
        if not b:
            raise ValueError("Bon cuisine introuvable")
        lignes = conn.execute(
            "SELECT * FROM lignes WHERE bon_id=? AND statut_cuisine NOT IN ('servi','annule') ORDER BY cree_le",
            (bid,)).fetchall()
        if not lignes:
            raise ValueError("Bon deja termine (toutes lignes servies/annulees)")
        ordre = ["envoye", "en_preparation", "pret", "servi"]
        statuts = {l["statut_cuisine"] for l in lignes}
        if "envoye_papier" in statuts or "non_envoye" in statuts:
            raise ValueError("Bon papier ou lignes non envoyees : avancement au fil cuisine")
        courant = min((ordre.index(s) for s in statuts if s in ordre), default=0)
        if courant >= len(ordre) - 1:
            raise ValueError("Bon deja termine")
        vise = ordre[courant + 1]
        conn.execute("UPDATE lignes SET statut_cuisine=? WHERE bon_id=? AND statut_cuisine NOT IN ('servi','annule')",
                     (vise, bid))
        auditer(conn, "cuisine", "bon_avance", b["commande_id"], None,
                json.dumps({"bon": bid, "vers": vise}, ensure_ascii=False))
    # --- sortie caisse (CAI-3 : en_attente, validee par gerant/proprio) ---
    def _sortie_caisse(self, conn, corps):
        jid = _journee_id(conn)
        serveur = self._serveur(conn, corps)
        montant = _montant(corps.get("montant"))
        motif = str(corps.get("motif") or "").strip()
        if not motif:
            raise ValueError("Motif de sortie obligatoire (CAI-3)")
        sid = _uuid()
        conn.execute("INSERT INTO sorties_caisse (id, journee_id, serveur_id, montant, motif, commentaire)"
                     " VALUES (?,?,?,?,?,?)",
                     (sid, jid, serveur, montant, motif, corps.get("commentaire")))
        auditer(conn, serveur, "sortie_caisse", None, motif,
                json.dumps({"sortie": sid, "montant": montant}, ensure_ascii=False))
        conn.commit()
        return self._json({"ok": True, "sortie": sid, "statut": "en_attente"})
        conn.commit()
        return self._json({"ok": True, "bon": bid, "statut": vise})
    # --- cloture caisse (CAI-4 tolerance + CAI-5 forcage R1) ---
    def _cloturer_caisse(self, conn, corps):
        jid = _journee_id(conn)
        serveur = corps.get("serveur") or self._serveur(conn, corps)
        k = conn.execute("SELECT * FROM caisses WHERE journee_id=? AND serveur_id=?",
                         (jid, serveur)).fetchone()
        if not k:
            raise ValueError("Aucune caisse ouverte pour ce serveur")
        if k["statut"] != "ouverte":
            raise ValueError("Caisse deja %s" % k["statut"])
        compte = _montant(corps.get("compte"), nom="montant compte")
        attendu = etat_caisse(conn, serveur, jid)["attendu"]
        ecart = compte - attendu
        tol = conn.execute("SELECT valeur FROM parametres WHERE cle='tolerance_ecart'").fetchone()
        tolerance = int(tol["valeur"]) if tol else 0
        if corps.get("forcee"):  # CAI-5 : gerant/proprio + motif
            self._exige_roles(conn, self._serveur(conn, corps), ("gerant", "proprietaire"), "forcage caisse")
            motif = str(corps.get("motif") or corps.get("ecart_motif") or "").strip()
            if not motif:
                raise ValueError("Forcage : motif obligatoire (CAI-5)")
            conn.execute("UPDATE caisses SET statut='forcee', montant_compte=?, ecart=?,"
                         " ecart_motif=?, ecart_commentaire=?, cloturee_le=?, forcee_par=? WHERE id=?",
                         (compte, ecart, motif, corps.get("commentaire"), maintenant(),
                          self._serveur(conn, corps), k["id"]))
            auditer(conn, self._serveur(conn, corps), "caisse_forcee", None, motif,
                    json.dumps({"caisse": k["id"], "ecart": ecart}, ensure_ascii=False))
            conn.commit()
            return self._json({"ok": True, "statut": "forcee", "ecart": ecart})
        if abs(ecart) > tolerance:  # CAI-4 : motif + commentaire
            motif = str(corps.get("motif") or corps.get("ecart_motif") or "").strip()
            comm = str(corps.get("commentaire") or corps.get("ecart_commentaire") or "").strip()
            if not motif or not comm:
                raise ValueError("Ecart %d hors tolerance %d : motif + commentaire obligatoires (CAI-4)"
                                 % (ecart, tolerance))
            conn.execute("UPDATE caisses SET statut='close', montant_compte=?, ecart=?,"
                         " ecart_motif=?, ecart_commentaire=?, cloturee_le=? WHERE id=?",
                         (compte, ecart, motif, comm, maintenant(), k["id"]))
        else:
            conn.execute("UPDATE caisses SET statut='close', montant_compte=?, ecart=?, cloturee_le=? WHERE id=?",
                         (compte, ecart, maintenant(), k["id"]))
        auditer(conn, serveur, "caisse_cloturee", None, None,
                json.dumps({"caisse": k["id"], "ecart": ecart}, ensure_ascii=False))
        conn.commit()
        return self._json({"ok": True, "statut": "close", "ecart": ecart})
