-- M1 · 004 caisse, sorties, clôtures, corrections · spec v1.2
PRAGMA foreign_keys = ON;

CREATE TABLE caisses ( -- CAI-1/CAI-2/CAI-4 [M7-Q4-A]
  id TEXT PRIMARY KEY,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT,
  serveur_id TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  fond INTEGER NOT NULL DEFAULT 0 CHECK (fond >= 0), -- CAI-1 fixé à l'ouverture
  statut TEXT NOT NULL DEFAULT 'ouverte' CHECK (statut IN ('ouverte','close','forcee')), -- CAI-5
  montant_compte INTEGER,                 -- tiroir compté à la clôture
  ecart INTEGER,                          -- compte - attendues
  ecart_motif TEXT,                       -- obligatoire si |écart| > tolérance
  ecart_commentaire TEXT,
  cloturee_le TEXT,
  forcee_par TEXT REFERENCES users(id) ON DELETE RESTRICT, -- CAI-5 R1
  UNIQUE (journee_id, serveur_id)
);
CREATE TABLE sorties_caisse ( -- CAI-3
  id TEXT PRIMARY KEY,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT,
  serveur_id TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT, -- demandeur
  montant INTEGER NOT NULL CHECK (montant > 0),
  motif TEXT NOT NULL,                    -- liste paramétrable
  commentaire TEXT,
  statut TEXT NOT NULL DEFAULT 'en_attente' CHECK (statut IN ('en_attente','validee','rejetee')),
  validee_par TEXT REFERENCES users(id) ON DELETE RESTRICT,
  validee_le TEXT,
  est_reversement_pourboire INTEGER NOT NULL DEFAULT 0 CHECK (est_reversement_pourboire IN (0,1)) -- PAI-6 tracé à part [M7-Q4-A]
);
CREATE TABLE corrections ( -- R4/R5: enregistrement distinct référençant l'original
  id TEXT PRIMARY KEY,
  commande_origine_id TEXT NOT NULL REFERENCES commandes(id) ON DELETE RESTRICT,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT, -- R5: journée en cours
  type TEXT NOT NULL CHECK (type IN ('financiere','stock')),
  sort_produit TEXT NOT NULL CHECK (sort_produit IN ('retour_stock','perte','sans_objet')),
  montant INTEGER NOT NULL DEFAULT 0,
  motif TEXT NOT NULL,
  autorisation_id TEXT,                   -- R1 (FK en 005)
  cree_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX idx_sorties_journee ON sorties_caisse(journee_id);
CREATE INDEX idx_corrections_origine ON corrections(commande_origine_id);
