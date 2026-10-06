//! M5 - Caisse et journee, Rust pur sans I/O.
//! Spec v1.2 : CAI-1..6, PAI-4, R2, R5. Formule [M7-Q4-A], tolerance affichee.
//! Miroir : tests_m5/m5_mirror.py.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StatutJournee {
    Ouverte,
    EnCloture,
    Close,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StatutCaisse {
    Ouverte,
    Close,
    Forcee,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Erreur {
    JourneeClose,
    JourneeDejaClose,
    JourneeNonEnCloture,
    CaissesNonCloses,
    CaisseDejaClose,
    EcartNonJustifie,
    ForcageSansAutorisation,
    MontantInvalide,
}

/// R2 : tout se rattache a la journee, pas a la date civile.
/// R5 : close = definitive, jamais rouverte.
pub fn fermer_journee(
    statut: StatutJournee,
    caisses_toutes_closes: bool,
) -> Result<StatutJournee, Erreur> {
    match statut {
        StatutJournee::Close => Err(Erreur::JourneeDejaClose),
        StatutJournee::Ouverte => Err(Erreur::JourneeNonEnCloture), // passer par EnCloture d'abord
        StatutJournee::EnCloture => {
            if !caisses_toutes_closes {
                return Err(Erreur::CaissesNonCloses);
            } // CAI-1
            Ok(StatutJournee::Close)
        }
    }
}

/// CAI-2 [M7-Q4-A] : attendues = fond + especes - monnaie + tips_esp + remb_esp - sorties_validees.
/// Mobile (ventes + remboursements) exclu : rapproche a part (CAI-6).
pub fn especes_attendues(
    fond: i64,
    especes: i64,
    monnaie: i64,
    tips_esp: i64,
    remb_esp: i64,
    sorties: i64,
) -> i64 {
    fond + especes - monnaie + tips_esp + remb_esp - sorties
}

/// CAI-4 [M7-Q4-A] : |ecart| <= tolerance => sans motif (enregistre) ; sinon motif+commentaire obligatoires.
pub fn cloturer_caisse(
    compte: i64,
    attendues: i64,
    tolerance: i64,
    motif: &str,
    commentaire: &str,
    r1: bool,
    forcee: bool,
) -> Result<(StatutCaisse, i64), Erreur> {
    if forcee {
        if !r1 || motif.trim().is_empty() {
            return Err(Erreur::ForcageSansAutorisation);
        } // CAI-5
        return Ok((StatutCaisse::Forcee, compte - attendues));
    }
    let ecart = compte - attendues;
    if ecart.abs() <= tolerance {
        return Ok((StatutCaisse::Close, ecart));
    }
    if motif.trim().is_empty() || commentaire.trim().is_empty() {
        return Err(Erreur::EcartNonJustifie);
    }
    Ok((StatutCaisse::Close, ecart))
}

/// CAI-6 + PAI-4 : rapprochement mobile. Retourne (rapproches, litiges).
/// Un reglement mobile sans reference/operateur est refuse en amont (M2 ModeInconnu/Montant).
pub fn rapprocher_mobile(
    reglements: &[(String, i64)],
    releve: &[(String, i64)],
) -> (Vec<String>, Vec<String>) {
    let mut ok = vec![];
    let mut litiges = vec![];
    for (id, montant) in reglements {
        match releve.iter().find(|(r, m)| r == id && m == montant) {
            Some(_) => ok.push(id.clone()),
            None => litiges.push(id.clone()),
        }
    }
    (ok, litiges)
}

/// R5 : correction journee passee => comptabilisee journee en cours, reference origine.
/// Retourne la journee d'imputation (toujours la courante).
pub fn imputer_correction(journee_origine_close: bool, journee_en_cours: &str) -> &str {
    let _ = journee_origine_close;
    journee_en_cours
}
