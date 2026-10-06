-- M1 · 002 commandes, lignes, règlements, ardoises · spec v1.2
PRAGMA foreign_keys = ON;

CREATE TABLE commandes (
  id TEXT PRIMARY KEY,                    -- UUID local (CMD-6)
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT, -- R2
  serveur_id TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,    -- CMD-4
  table_nom TEXT,                         -- NULL = comptoir sans table
  mode TEXT NOT NULL CHECK (mode IN ('table','comptoir')), -- CMD-1
  statut TEXT NOT NULL DEFAULT 'ouverte'
    CHECK (statut IN ('ouverte','payee','payee_sans_addition','annulee')), -- CMD-7 [M7-Q2-A]
  total_brut INTEGER NOT NULL DEFAULT 0,
  total_net INTEGER NOT NULL DEFAULT 0,
  n_addition INTEGER,                     -- M7 compteur séquentiel (CMD-7)
  addition_imprimee_le TEXT,
  convertie_comptoir_vers_table INTEGER NOT NULL DEFAULT 0 CHECK (convertie_comptoir_vers_table IN (0,1)), -- CMD-3
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  version INTEGER NOT NULL DEFAULT 1      -- OFF-3 resynchro par version
);
CREATE TABLE lignes (
  id TEXT PRIMARY KEY,                    -- UUID local (conflit transfert, OFF-3)
  commande_id TEXT NOT NULL REFERENCES commandes(id) ON DELETE RESTRICT,
  produit_id TEXT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantite INTEGER NOT NULL CHECK (quantite > 0),
  prix_unitaire_fige INTEGER NOT NULL CHECK (prix_unitaire_fige >= 0), -- PRX-3
  cout_unitaire_fige INTEGER NOT NULL DEFAULT 0 CHECK (cout_unitaire_fige >= 0), -- PRX-3
  remise_type TEXT CHECK (remise_type IN ('pourcent','montant')),
  remise_valeur INTEGER CHECK (remise_valeur IS NULL OR remise_valeur >= 0),
  remise_motif TEXT,                      -- PAI-5 liste paramétrable
  est_offert INTEGER NOT NULL DEFAULT 0 CHECK (est_offert IN (0,1)), -- PAI-5 100%
  statut_cuisine TEXT NOT NULL DEFAULT 'non_envoye'
    CHECK (statut_cuisine IN ('non_envoye','envoye','envoye_papier','en_preparation','pret','servi','annule')), -- CUI-3/CUI-5
  bon_id TEXT,                            -- bon cuisine (CUI-1)
  transferee_de TEXT,                     -- CMD-2 traçage transfert lignes
  retire_motif TEXT,                      -- CMD-5
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE bons_cuisine (
  id TEXT PRIMARY KEY,
  n_bon INTEGER NOT NULL UNIQUE,          -- CUI-1 numéro unique séquentiel
  commande_id TEXT NOT NULL REFERENCES commandes(id) ON DELETE RESTRICT,
  statut TEXT NOT NULL DEFAULT 'envoye' CHECK (statut IN ('envoye','annule')),
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE reglements (
  id TEXT PRIMARY KEY,
  commande_id TEXT NOT NULL REFERENCES commandes(id) ON DELETE RESTRICT,
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT, -- R2
  serveur_id TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  mode TEXT NOT NULL CHECK (mode IN ('especes','mobile','ardoise')), -- PAI-1/PAI-2
  montant INTEGER NOT NULL CHECK (montant > 0),
  montant_recu INTEGER,                   -- PAI-3 espèces
  monnaie_rendue INTEGER NOT NULL DEFAULT 0, -- PAI-3
  operateur TEXT,                         -- PAI-4 obligatoire mobile
  reference_operateur TEXT,               -- PAI-4 obligatoire mobile
  statut_rapprochement TEXT NOT NULL DEFAULT 'non_applicable'
    CHECK (statut_rapprochement IN ('non_applicable','a_rapprocher','rapproche','litige')), -- CAI-6
  pourboire INTEGER NOT NULL DEFAULT 0 CHECK (pourboire >= 0), -- PAI-6 hors total/CA
  client_id TEXT REFERENCES clients(id) ON DELETE RESTRICT, -- ardoise
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE ardoise_mouvements (
  id TEXT PRIMARY KEY,
  client_id TEXT NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
  commande_id TEXT REFERENCES commandes(id) ON DELETE RESTRICT, -- vente liée
  journee_id TEXT NOT NULL REFERENCES journees(id) ON DELETE RESTRICT,
  sens TEXT NOT NULL CHECK (sens IN ('vente','remboursement','deblocage')),
  montant INTEGER NOT NULL CHECK (montant > 0),
  serveur_id TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT, -- ARD-4
  autorisation_id TEXT,                   -- ARD-3 R1 (FK ajoutée en 005)
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX idx_commandes_journee ON commandes(journee_id);
CREATE INDEX idx_commandes_serveur ON commandes(serveur_id);
CREATE INDEX idx_lignes_commande ON lignes(commande_id);
CREATE INDEX idx_reglements_commande ON reglements(commande_id);
CREATE INDEX idx_ardoise_client ON ardoise_mouvements(client_id);
