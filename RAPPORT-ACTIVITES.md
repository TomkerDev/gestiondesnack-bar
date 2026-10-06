# Rapport d'activités — Gestion de snack-bar

**Projet** : application de caisse (POS), de gestion de stock et de suivi de
cuisine pour un snack-bar, conforme à `specification-snack-bar.md` (v1.2).
**Sources** : `prompts-snack-bar.md` (jalons M1–M6, interfaces I1–I8).
**Livraison** : https://github.com/TomkerDev/gestiondesnack-bar

---

## 1. Phase 1 — Cœur métier (M1 → M6) ✅

Référence : modules `.rs` (Rust) dans `core/src/` ; exécution assurée par des
**miroirs Python** (`core/tests_m*/`) car la toolchain Rust est absente de
l'environnement de travail.

| Jalon | Périmètre | Exigences | Tests |
|---|---|---|---|
| **M1** | Schéma SQLite, 5 migrations, ERD, LIMITES, TRACE + scénario de bout en bout | CAI-2 = 13 500 · stock bière (J) = 22 | scénario ✅ |
| **M2** | Commandes : lignes, prix figés, transferts, conversion comptoir/table | CMD-1…7 (dont CMD-2) | 30 |
| **M3** | Ardoises : plafonds, ventes, déblocage R1, remboursements | ARD-1 à ARD-6 | 17 |
| **M4** | Cuisine + statuts, commutativité des mouvements, file de validation, pertes | CUI-3/4, STK-2 à STK-6 | 23 |
| **M5** | Caisse : formule CAI-2, écarts, tolérances, forçage clôture | CAI-1/2/4/5/6, R5 | 14 |
| **M6** | Sécurité : PIN, blocages progressifs, sessions, matrice §3, jeton R1 | SEC-1…3, R1, R3 | 18 |

**Total : 102 tests + scénario de bout en bout — tous verts.**

## 2. Phase 2 — Interfaces (I1 → I8) ✅

Pattern répété pour chaque interface : module JS pur (`src/lib/*.js`) testé par
`node --test` + route Svelte (`src/routes/**`) + test statique Python
(`tests/test_iN.py`) vérifiant la conformité sans compiler.

| Interface | Écran | Tests node | Tests statiques |
|---|---|---|---|
| **I1** | Composants, thème clair/sombre, galerie (48 px, zéro métier) | — | 28 |
| **I2** | Prise de commande : grille unique, 5 filtres, 1 appui = +1, prix figés | panier | 17 |
| **I3** | Liste + détail commandes : groupement par table, actions par rôle/état/offline, DUPLICATA | detail_commande | 17 |
| **I4** | Paiement : espèces/mobile, règlements multiples, pourboire, ardoise + R1 | paiement | 17 |
| **I5** | Cuisine : 3 colonnes, avancement au toucher, annulation sonore | cuisine | 16 |
| **I6** | Ma caisse : CAI-2, sorties, écart justifié, état final | ma_caisse (scénario 57 500) | 17 |
| **I7** | PC gérant : nav, raccourcis 1-2-3, alertes, journée, R3 (jamais les coûts) | pc_gerant | 18 |
| **I8** | PC stock : négatifs, entrées (STK-4), inventaire, pertes, ardoises, prix (PRX-1) | stock_pc | 27 |

**Total phase : 59 tests node + 157 tests statiques — tous verts.**

Correctifs livrés en cours de phase : `Bouton.svelte` qui forward `on:click`,
refus STK-4 sans mouvement inverse, messages de prix sans révélation de coût,
acceptation de la liste de fonds vide (I7), découpage des grosses pages en
blocs d'édition < 6 000 caractères.


## 3. Phase 3 — Passe d'intégration ✅

Jusque-là les pages étaient des coques sans données : aucun accès réseau, pas
de layout, boutons principaux non câblés, app non buildable.

1. **`src/lib/api.js`** — client unique vers le PC caisse (endpoints commandes,
   paiement, cuisine, caisse, stock, ardoises, prix) :
   - **OFF-1** : hors ligne, les ventes continuent — actions en file d'attente ;
   - **OFF-2** : remises, offerts, R1, déblocages, corrections, impression
     refusés avec raison écrite ;
   - **OFF-3** : `resynchroniser()` rejoue la file dans l'ordre, remonte les
     alertes, conserve la file si le PC rejette (réessai suivant).
   - `fetch`/horloge injectés → testable en node (7 tests).
2. **`src/lib/session.js`** — store compatible Svelte, identité SEC-1 (code ≥
   4 chiffres), horodatage, état réseau (4 tests).
3. **`+layout.svelte`** — thème, navigation tactile des 8 écrans, bandeau
   `BandeauConnexion` piloté par les événements `online`/`offline` avec
   resynchronisation automatique au retour du réseau.
4. **Branchement des pages** — « Envoyer en cuisine »/« Payer » (`/commande`),
   actions du détail (`onAction(cle)`), liste (`onNouvelle`/`onOuvrir`) ;
   plus aucun `fetch(` brut dans les routes (vérifié par test).
5. **Build** — `svelte.config.js` (adapter-static, SPA `ssr = false`),
   `vite.config.js` (proxy `/api` → `127.0.0.1:8080`), `app.html`,
   dépendances npm. **`npm run build` vert** — le projet n'était auparavant
   buildable nulle part.
6. **Bug découvert et corrigé** : le script de `pc/stock/+page.svelte` était
   scindé en deux au milieu du markup (3 fonctions perdues) — invisible pour
   les tests statiques, fatal au build.

**Total : 11 tests node + 41 tests statiques d'intégration — tous verts.**

## 4. Phase 4 — Qualité et livraison ✅

- **`npm test` complet : EXIT = 0** — 70 tests node + 157 statiques I1–I8 +
  41 statiques d'intégration = **268 tests front**.
- **Régression cœur** après chaque changement : 102 tests + scénario M1 ✅.
- **`npm run build`** : build de production SPA via adapter-static ✅.
- **README** rédigé (architecture, démarrage, tests, avancement, limites).
- **Historique Git en 6 commits pas à pas**, poussé sur GitHub :

| Commit | Contenu |
|---|---|
| `b670add` | docs: spécification v1.2 et prompts |
| `940f59a` | feat(core): noyau Rust + miroirs Python (M1–M6) |
| `4fec87a` | feat(db): schéma SQLite, migrations, scénario M1 |
| `9d47d03` | feat(app): interfaces I1–I8 (9 écrans) |
| `54359b4` | feat(app): passe d'intégration (API offline, session, layout, build) |
| `1964da3` | docs: README |

## 5. Bilan chiffré

| Indicateur | Valeur |
|---|---|
| Tests totaux (cœur + front) | **371** (102 + scénario + 268) |
| Tests en échec | **0** |
| Interfaces livrées | **8 / 8** (I1–I8) |
| Jalons backend | **6 / 6** (M1–M6) |
| Écrans Svelte | 9 (+ layout global) |
| Modules JS purs testés | 9 (panier, detail_commande, paiement, cuisine, ma_caisse, pc_gerant, stock_pc, api, session) |
| Build de production | ✅ |
| Commits poussés sur GitHub | 6 |

## 6. Limites et suites

1. **Pas de serveur axum réel** dans le dépôt : le front tourne avec des
   données vides tant que le back Rust n'est pas compilé (proxy Vite déjà
   pointé sur `127.0.0.1:8080`).
2. **PIN non câblé** : `session.ouvrirSession` existe et est testé, mais
   aucun écran d'identification ne l'appelle encore.
3. **WebSocket cuisine non ouvert** : l'abonnement `api.abonner()` est prêt,
   aucune connexion n'est établie.
4. Rust/cargo absents de l'environnement : les `.rs` font autorité mais ne
   sont pas compilés ici — les miroirs Python sont exécutés à leur place.
