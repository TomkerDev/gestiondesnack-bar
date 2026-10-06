-- M1 · Schéma SQLite complet · spec v1.2
-- Règles: UUID TEXT PK (CMD-6, OFF-3), montants INTEGER petite unité (jamais REAL),
-- aucun DELETE physique (RESTRICT), audit + mouvements en ajout seul (triggers),
-- pas de CHECK stock>=0 (STK-3), prix/coûts figés par ligne (PRX-3).
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============ RÉFÉRENTIELS ============
CREATE TABLE users (
  id TEXT PRIMARY KEY,                    -- UUID généré localement (CMD-6)
  nom TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('serveur','gerant','proprietaire')), -- §3
  pin_hash TEXT NOT NULL,                 -- argon2id (M6), jamais le PIN (SEC-2)
  pin_salt TEXT NOT NULL,
  peut_saisir_entrees INTEGER NOT NULL DEFAULT 0 CHECK (peut_saisir_entrees IN (0,1)), -- STK-4
  est_actif INTEGER NOT NULL DEFAULT 1 CHECK (est_actif IN (0,1)),
  echecs_pin INTEGER NOT NULL DEFAULT 0,  -- SEC-1
  bloque_jusquau TEXT,                    -- ISO8601, 5min puis 15min [M7-Q5-A]
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE products (
  id TEXT PRIMARY KEY,
  nom TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('boisson','plat')),
  est_alcoolise INTEGER NOT NULL DEFAULT 0 CHECK (est_alcoolise IN (0,1)),
  suivi_stock INTEGER NOT NULL DEFAULT 1 CHECK (suivi_stock IN (0,1)), -- STK-1: 0 pour plats v1
  prix_vente INTEGER NOT NULL CHECK (prix_vente >= 0),                 -- plus petite unité
  prix_achat INTEGER CHECK (prix_achat IS NULL OR prix_achat >= 0),    -- R3 proprio seul
  cout_estime INTEGER CHECK (cout_estime IS NULL OR cout_estime >= 0), -- PRX-2 plats
  est_actif INTEGER NOT NULL DEFAULT 1 CHECK (est_actif IN (0,1)),
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE clients (
  id TEXT PRIMARY KEY,
  nom TEXT NOT NULL,
  telephone TEXT,
  plafond INTEGER NOT NULL CHECK (plafond >= 0), -- ARD-1
  est_actif INTEGER NOT NULL DEFAULT 1 CHECK (est_actif IN (0,1)),
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE journees (
  id TEXT PRIMARY KEY,
  statut TEXT NOT NULL DEFAULT 'ouverte' CHECK (statut IN ('ouverte','en_cloture','close')), -- M5
  ouverte_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  fermee_le TEXT,
  ouverte_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,  -- CAI-1
  fermee_par TEXT REFERENCES users(id) ON DELETE RESTRICT
);
CREATE TABLE compteurs ( -- M7: numéros séquentiels additions/bons, trou = alerte
  nom TEXT PRIMARY KEY CHECK (nom IN ('n_addition','n_bon')),
  valeur INTEGER NOT NULL DEFAULT 0
);
INSERT INTO compteurs (nom, valeur) VALUES ('n_addition', 0), ('n_bon', 0);
CREATE TABLE parametres ( -- R3: tolérance modifiable proprio seul
  cle TEXT PRIMARY KEY,
  valeur TEXT NOT NULL,
  modifie_par TEXT REFERENCES users(id) ON DELETE RESTRICT,
  modifie_le TEXT
);
INSERT INTO parametres (cle, valeur) VALUES
  ('devise','XOF'), ('tolerance_ecart','0'), ('motifs_remise','["offert maison","client fidèle","erreur de service","geste commercial","promotion","consommation du personnel","Autre"]'),
  ('motifs_casse','["bouteille ou verre cassé","produit périmé ou avarié","boisson renversée","plat raté ou renvoyé","Autre"]'),
  ('motifs_sortie','["achat urgent","avance à un livreur ou fournisseur","avance au personnel","reversement de pourboire","Autre"]'),
  ('motifs_ecart_caisse','["erreur de monnaie rendue","vente non enregistrée","confusion de mode de paiement","sortie de caisse non saisie","remboursement d''ardoise non saisi","erreur de comptage","Autre"]'),
  ('motifs_ecart_inventaire','["casse non déclarée","offert non saisi","livraison non saisie","vente non saisie","erreur de comptage","vol suspecté","Autre"]');
