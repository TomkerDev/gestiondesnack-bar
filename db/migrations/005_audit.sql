-- M1 · 005 audit, prix, autorisations R1 + triggers ajout seul · spec v1.2
PRAGMA foreign_keys = ON;

CREATE TABLE autorisations ( -- R1 [M7-Q5-A]: jeton 1 usage, 60s
  id TEXT PRIMARY KEY,
  acte TEXT NOT NULL,                     -- ex: remise, offert, deblocage, correction, forçage, annulation_apres_prepa
  commande_id TEXT REFERENCES commandes(id) ON DELETE RESTRICT,
  demandeur_id TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  autorise_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  montant_concerne INTEGER,
  motif TEXT NOT NULL,
  statut TEXT NOT NULL DEFAULT 'consommee' CHECK (statut IN ('consommee','expiree','rejetee')),
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  expire_le TEXT NOT NULL
);
CREATE TABLE prix_historique ( -- PRX-1 tracé qui/ancien/nouveau/quand
  id TEXT PRIMARY KEY,
  produit_id TEXT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  ancien_prix INTEGER NOT NULL,
  nouveau_prix INTEGER NOT NULL,
  change_par TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE audit_log ( -- SEC-3 ajout seul
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  qui TEXT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  quoi TEXT NOT NULL,                     -- annulation, remise, deblocage, correction, prix, plafond, entree, forçage
  commande_id TEXT REFERENCES commandes(id) ON DELETE RESTRICT,
  motif TEXT,
  detail TEXT,                            -- JSON libre (montants, ancien/nouveau)
  quand TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Rattache les FK croisées (ardoise_mouvements.autorisation_id, corrections.autorisation_id)
-- SQLite ne permet pas ADD CONSTRAINT: on s'appuie sur le typage + contrôles applicatifs,
-- et on documente ici l'intention référentielle.
-- (choix volontaire documenté M1: FK ajoutées dès la création en 006 si base neuve)

-- Triggers: journal et mouvements en ajout seul (SEC-3, STK-2)
CREATE TRIGGER trg_audit_no_update BEFORE UPDATE ON audit_log BEGIN
  SELECT RAISE(ABORT, 'audit_log: UPDATE interdit (SEC-3)');
END;
CREATE TRIGGER trg_audit_no_delete BEFORE DELETE ON audit_log BEGIN
  SELECT RAISE(ABORT, 'audit_log: DELETE interdit (SEC-3)');
END;
CREATE TRIGGER trg_mvt_no_update BEFORE UPDATE ON mouvements_stock BEGIN
  SELECT RAISE(ABORT, 'mouvements_stock: UPDATE interdit (STK-2)');
END;
CREATE TRIGGER trg_mvt_no_delete BEFORE DELETE ON mouvements_stock BEGIN
  SELECT RAISE(ABORT, 'mouvements_stock: DELETE interdit (STK-2)');
END;
-- Suppressions physiques interdites: RESTRICT déjà posé sur toutes les FK.
-- Règle applicative: désactivation via est_actif, jamais DELETE.
