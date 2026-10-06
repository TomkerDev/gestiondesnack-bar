# M1 · Exigence → table.colonne

| Exigence | Table.colonne (preuve) |
|---|---|
| CMD-1 mode table/comptoir | commandes.mode |
| CMD-2 multi-commandes, transfert lignes | commandes.table_nom + lignes.transferee_de |
| CMD-3 comptoir→table | commandes.convertie_comptoir_vers_table |
| CMD-4 propriété + transfert | commandes.serveur_id |
| CMD-5 retrait boisson | lignes.retire_motif + mouvements_stock.retour |
| CMD-6 UUID local | toutes PK TEXT UUID |
| CMD-7 addition + DUPLICATA + offline | commandes.n_addition, addition_imprimee_le, statut payee_sans_addition |
| CUI-1 bon unique | bons_cuisine.n_bon UNIQUE |
| CUI-3 statuts + horodat central | lignes.statut_cuisine |
| CUI-4 annulation + perte | lignes.statut_cuisine=annule + mouvements_stock.annulation + audit_log |
| CUI-5 papier offline | lignes.statut_cuisine=envoye_papier |
| PAI-1/2/3/4 paiement | reglements.mode/montant/montant_recu/monnaie_rendue/operateur/reference_operateur |
| PAI-5 remise/offert R1 | lignes.remise_* + est_offert + autorisations |
| PAI-6 pourboire | reglements.pourboire + sorties_caisse.est_reversement_pourboire |
| ARD-1→6 | clients.plafond + ardoise_mouvements + reglements.client_id |
| STK-1 suivi | products.suivi_stock |
| STK-2 ajout seul | mouvements_stock + triggers no UPDATE/DELETE |
| STK-3 pas de stock>=0 | aucun CHECK >=0 sur quantités |
| STK-4 entrée à valider hors dispo | entrees_stock.statut + entree_lignes |
| STK-5 inventaire | inventaires + ordre M7-Q3-A |
| STK-6 pertes | mouvements_stock.type + motif |
| CAI-1→6 | journees + caisses + sorties_caisse |
| PRX-1/2/3 | prix_historique + products.prix_achat/cout_estime + lignes.prix_unitaire_fige/cout_unitaire_fige |
| OFF-1→4 | UUID + version + statut payee_sans_addition |
| R1/R3/R4/R5 | autorisations + audit_log + corrections |
| SEC-1→3 | users.pin_hash/salt/echecs/bloque + audit_log ajout seul |
| RPT-1 | requêtes sur reglements/mouvements/caisses |
