//! M3 - Ardoise, Rust pur sans I/O.
//! Spec v1.2 : ARD-1..6, PAI-2 (exclusivite), R1 (jeton verifie en M6).
//! i64 petite unite. Miroir Python : core/tests_m3/m3_mirror.py.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Client {
    pub id: String,
    pub plafond: i64,  // ARD-1 fixe par gerant/proprio
    pub solde_du: i64, // ARD-1
}

/// ARD-2 : decision de vente.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    Accepte,
    Refuse,
    RefuseDeblocable, // ARD-3 : depassement => R1 gerant possible
}

/// ARD-2 : solde + montant <= plafond => accepte ; sinon refuse (deblocable si client identifie).
pub fn decider_vente(client: Option<&Client>, montant: i64) -> Decision {
    if montant <= 0 {
        return Decision::Refuse;
    }
    match client {
        None => Decision::Refuse, // ARD-2 : client identifie exige
        Some(c) => {
            if c.solde_du + montant <= c.plafond {
                Decision::Accepte
            } else {
                Decision::RefuseDeblocable
            }
        }
    }
}

/// ARD-3 : deblocage ponctuel R1, ne modifie PAS le plafond.
/// Retourne le nouveau solde (vente comptabilisee) ; l'appelant trace (autorisations + audit M1).
pub fn appliquer_deblocage(solde_du: i64, montant: i64, r1: bool) -> Result<i64, Erreur> {
    if !r1 {
        return Err(Erreur::DeblocageSansAutorisation);
    }
    if montant <= 0 {
        return Err(Erreur::MontantInvalide);
    }
    Ok(solde_du + montant)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Erreur {
    MontantInvalide,
    DeblocageSansAutorisation,
    DeblocageHorsLigne, // ARD-6 : aucun deblocage offline
    RemboursementInvalide,
}

/// ARD-6 : offline = decision sur instantane, jamais de deblocage.
pub fn decider_vente_offline(
    instantane: Option<&Client>,
    montant: i64,
) -> Result<Decision, Erreur> {
    if montant <= 0 {
        return Err(Erreur::MontantInvalide);
    }
    match instantane {
        None => Ok(Decision::Refuse),
        Some(c) => Ok(if c.solde_du + montant <= c.plafond {
            Decision::Accepte
        } else {
            Decision::Refuse // offline : pas de RefuseDeblocable (ARD-6)
        }),
    }
}

pub fn tenter_deblocage_offline() -> Result<(), Erreur> {
    Err(Erreur::DeblocageHorsLigne) // ARD-6
}

/// ARD-4 : remboursement = encaissement distinct attribue au serveur.
/// Retourne (nouveau_solde, especes_attendues_delta, ca_delta).
/// Espece => especes attendues +montant ; mobile => 0 (rapproche M5).
/// CA inchange (la vente comptait deja).
pub fn appliquer_remboursement(
    solde_du: i64,
    montant: i64,
    mode: &str,
) -> Result<(i64, i64), Erreur> {
    if montant <= 0 {
        return Err(Erreur::RemboursementInvalide);
    }
    if solde_du <= 0 {
        return Err(Erreur::RemboursementInvalide);
    }
    let nouveau = (solde_du - montant).max(0);
    let delta_especes = if mode == "especes" { montant } else { 0 }; // ARD-4 + CAI-2
    Ok((nouveau, delta_especes))
}

/// ARD-6 resynchro : recalcule et signale les depassements.
/// Entrees : (client_id, solde_central_avant, ventes_offline, remboursements_offline).
/// Sortie : liste d'alertes (client_id, nouveau_solde, plafond).
/// Ligne d'historique client pour la resynchro ARD-6 :
/// (id, solde_central_avant, plafond ignore — relu via `plafonds`, ventes, remboursements).
pub type LigneResynchro = (String, i64, i64, Vec<i64>, Vec<i64>);
pub fn controler_resynchro(
    clients: &[LigneResynchro],
    plafonds: &std::collections::HashMap<String, i64>,
) -> Vec<(String, i64, i64)> {
    let mut alertes = Vec::new();
    for (id, solde_avant, _plafond_ignoré, ventes, remb) in clients {
        let plafond = plafonds.get(id).copied().unwrap_or(0);
        let nouveau: i64 = solde_avant + ventes.iter().sum::<i64>() - remb.iter().sum::<i64>();
        if nouveau > plafond {
            alertes.push((id.clone(), nouveau, plafond)); // ARD-5/ARD-6
        }
    }
    alertes
}

/// ARD-4 : la vente ardoise compte en CA mais pas en especes attendues.
pub fn impact_vente_ardoise(montant: i64) -> (i64, i64) {
    (montant, 0) // (ca_delta, especes_delta)
}
