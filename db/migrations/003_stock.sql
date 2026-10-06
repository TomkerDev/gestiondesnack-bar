-- M1 · 003 stock, entrées, inventaire · spec v1.2
PRAGMA foreign_keys = ON;

CREATE TABLE mouvements_stock ( -- STK-2 ajout seul, jamais modifiés (M6 triggers)
  id TEXT PRIMARY KEY,
  produit_id TEXT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT, -- R2
  quantite INTEGER NOT NULL CHECK (quantite != 0), -- PAS de CHECK >=0 (STK-3)
  type TEXT NOT NULL CHECK (type IN ('vente','achat','casse','correction','rejet_entree','retour','offert','annulation')),
  commande_id TEXT REFERENCES commandes(id) ON DELETE RESTRICT,
  entree_id TEXT,                         -- entrée validée source
  motif TEXT,                             -- STK-5/STK-6 listes paramétrables
  commentaire TEXT,
  cree_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE entrees_stock ( -- STK-4 [M7-Q1-A]: à valider hors disponible
  id TEXT PRIMARY KEY,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT,
  statut TEXT NOT NULL DEFAULT 'a_valider' CHECK (statut IN ('a_valider','validee','rejetee')),
  saisie_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  validee_par TEXT REFERENCES users(id) ON DELETE RESTRICT, -- != saisie_par (M7)
  saisie_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  validee_le TEXT,
  motif_rejet TEXT
);
CREATE TABLE entree_lignes (
  id TEXT PRIMARY KEY,
  entree_id TEXT NOT NULL REFERENCES entrees_stock(id) ON DELETE RESTRICT,
  produit_id TEXT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantite INTEGER NOT NULL CHECK (quantite > 0) -- quantités seules (STK-4)
);
CREATE TABLE inventaires ( -- STK-5 après caisses, avant clôture journée [M7-Q3-A]
  id TEXT PRIMARY KEY,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT,
  produit_id TEXT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantite_theorique INTEGER NOT NULL,    -- calculée dispo (hors en attente)
  quantite_comptee INTEGER NOT NULL CHECK (quantite_comptee >= 0),
  ecart INTEGER NOT NULL,                 -- comptee - theorique
  motif TEXT NOT NULL,                    -- obligatoire si écart != 0
  mouvement_id TEXT REFERENCES mouvements_stock(id) ON DELETE RESTRICT,
  compte_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE (journee_id, produit_id)
);
CREATE INDEX idx_mvt_produit ON mouvements_stock(produit_id);
CREATE INDEX idx_mvt_journee ON mouvements_stock(journee_id);
