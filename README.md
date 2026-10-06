# Gestion de snack-bar — POS, stock et cuisine

Application de caisse (POS), de gestion de stock et de suivi de cuisine pour un
snack-bar, conforme à la spécification française **`specification-snack-bar.md`
(v1.2)** — chaque exigence porte un identifiant (CMD-1, STK-3, CAI-2, R1, OFF-1…).

## Fonctionnalités

| Écran | Route | Public | Rôle |
|---|---|---|---|
| Prise de commande | `/commande` | Serveurs (téléphone/tablette) | Grille unique, 1 appui = +1, prix figés, hors ligne OK |
| Mes commandes | `/commandes`, `/commandes/[id]` | Serveurs | Liste par table, actions selon rôle/état/offline |
| Paiement | `/paiement` | Serveurs | Espèces + mobile money, pourboire, ardoise (R1) |
| Écran cuisine | `/cuisine` | Cuisine (tablette fixe) | 3 colonnes, 1 appui = avancer, annulation sonore |
| Ma caisse | `/ma-caisse` | Serveurs | CAI-2, sorties, clôture avec écart justifié |
| PC caisse | `/pc`, `/pc/stock` | Gérant / propriétaire | Alertes, journée, caisses, stock, ardoises, prix |

Points transverses : **montants entiers** dans la plus petite unité (jamais de
flottants), **fonctionnement hors ligne** pour les serveurs (OFF-1/2/3),
interface **100 % en français**, cibles tactiles ≥ 48 px, thème clair/sombre.

## Arborescence

```
gestiondesnack-bar/
├── specification-snack-bar.md   # Source de vérité (v1.2)
├── prompts-snack-bar.md         # Prompts de développement (M1–M6, interfaces)
├── core/                        # Cœur métier
│   ├── src/                     # .rs = référence (noyau métier, compilé par cargo)
│   │   ├── lib.rs  commande.rs  caisse.rs  ardoise.rs  securite.rs  stock.rs
│   ├── tests/                   # Suite cargo test native (22 tests M2–M6)
│   │   ├── m2_commande.rs  m3_m4.rs  m5_m6.rs
│   ├── rust-toolchain.toml      # Pin stable + clippy + rustfmt
│   └── tests_m2 … tests_m6/     # Miroirs Python (secours sans Rust)
├── db/                          # SQLite (migrations, ERD, LIMITES, TRACE)
│   └── test_scenario_m1.py      # Scénario bout en bout (CAI-2, stock)
└── app/                         # Front SvelteKit (SPA, PWA installable)
    ├── src/lib/                 # Logique pure testable (panier, paiement…)
    │   ├── api.js  session.js   # Couche d'intégration vers le PC caisse
    │   └── components/           # Composants UI (zéro métier)
    ├── src/routes/              # Les 8 interfaces + layout global
    └── tests/                   # node --test + tests statiques Python
```

## État d'avancement

- ✅ **M1–M6** : cœur métier (commandes, caisse, ardoises, stock, sécurité,
  clôture) — 102 tests + scénario de bout en bout.
- ✅ **I1–I8** : les 8 interfaces livrées — 59 tests node, 173 tests statiques.
- ✅ **Passe d'intégration** : client API (`src/lib/api.js`), session
  (`session.js`), layout global, build SvelteKit — 52 tests supplémentaires.
- ⏳ À faire : serveur local axum réel (Rust), WebSocket temps réel, écran
  d'identification PIN connecté à `session`.

## Prérequis

- **Node.js ≥ 20** et npm
- **Python ≥ 3.11** (serveur local + tests statiques, stdlib uniquement)
- **Toolchain Rust stable** (natif GNU Windows : `rustc 1.99`) — `cargo build`,
  `cargo test`, `cargo clippy`, `cargo fmt` dans `core/`

## Démarrage

```bash
npm install        # dépendances du front
npm run dev        # serveur de dev (proxy /api → 127.0.0.1:8080)
npm run build      # build de production (SPA statique → dossier build/)
npm test           # suite complète : node + Python (voir ci-dessous)
```

Le proxy Vite (`vite.config.js`) redirige `/api` vers `http://127.0.0.1:8080`,
port attendu du serveur local **axum** du PC caisse (HTTP + WebSocket).

## Tests

```bash
npm test
# ├── node --test tests/*.test.js   # logique pure (panier, paiement, api…)
# ├── python tests/test_i1.py … test_i8.py   # conformité statique par interface
# └── python tests/test_integration.py       # branchement + scaffolding
```

Côté cœur métier, la référence est la suite Rust native :

```bash
cd core
cargo test              # 22 tests M2–M6 (spec v1.2)
cargo clippy --all-targets -- -D warnings   # zéro warning
cargo fmt --all --check                     # format verrouillé
```

Les miroirs Python restent en secours (environnement sans Rust) :

```bash
python core/tests_m2/test_m2.py   # … jusqu'à test_m6
python db/test_scenario_m1.py     # scénario complet (CAI-2 = 13 500)
```

## Choix d'architecture

- **SPA (`ssr = false`, adapter-static)** : les appareils serveurs/cuisine
  doivent fonctionner hors ligne, aucune rendu côté serveur.
- **Logique pure dans `src/lib/*.js`** : chaque module est testé par
  `node --test` sans compiler Svelte ; les composants UI contiennent zéro
  métier (vérifié par `test_i1.py`).
- **Les `.rs font autorité** : les miroirs Python/JS sont des exécutables de
  secours pour les environnements sans Rust, pas des sources alternatives.
- **Intégration** : `api.js` parle au PC caisse ; hors ligne, les actions
  autorisées (OFF-1) sont mises en file et rejouées à la resynchronisation
  (OFF-3), les actions interdites (OFF-2 : remises, R1, corrections…) sont
  refusées avec une raison écrite affichée à l'utilisateur.

## Limites connues

1. Serveur local = **miroir Python** (`serveur/serveur.py`, stdlib) qui reproduit
   le contrat HTTP du futur back axum : le front tourne avec des données
   réelles en local, mais le back Rust reste à écrire.
2. Pas d'écran de connexion PIN branché (`session.ouvrirSession` existe et est
   testé, mais n'est pas encore appelé par une route).
3. Les événements WebSocket cuisine ne sont pas ouverts (l'abonnement
   `api.abonner()` est prêt).
