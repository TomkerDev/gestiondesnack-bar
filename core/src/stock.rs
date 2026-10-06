//! M4 - Stock et cuisine, Rust pur sans I/O.
//! Spec v1.2 : STK-1..6, PRX-3 (cout fige), CUI-3/CUI-4 (statuts, pertes).
//! DIVERGENCE signalee : prompt M4 dit "comptee des la saisie" ;
//! spec v1.2 [M7-Q1-A] prime : a_valider hors disponible.
//! i64 quantites (pieces), i64 montants. Miroir : tests_m4/m4_mirror.py.
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Mouvement {
    pub produit: String,
    pub quantite: i64,
    pub type_: String,
}

/// STK-2 : stock = somme des mouvements. Commutatif par construction (addition).
pub fn stock_disponible(mouvements: &[Mouvement], produit: &str) -> i64 {
    mouvements
        .iter()
        .filter(|m| m.produit == produit)
        .map(|m| m.quantite)
        .sum()
}

/// STK-3 : vente autorisee meme a zero/negatif. Retourne alerte si stock apres < 0.
pub fn appliquer_vente(mouvements: &mut Vec<Mouvement>, produit: &str, qte: u32) -> bool {
    mouvements.push(Mouvement {
        produit: produit.to_string(),
        quantite: -(qte as i64),
        type_: "vente".into(),
    });
    stock_disponible(mouvements, produit) < 0 // true = alerter gerant
}

/// STK-3 : liste des produits negatifs.
pub fn produits_negatifs(mouvements: &[Mouvement]) -> Vec<String> {
    let mut tot: HashMap<&str, i64> = HashMap::new();
    for m in mouvements {
        *tot.entry(m.produit.as_str()).or_insert(0) += m.quantite;
    }
    tot.into_iter()
        .filter(|(_, s)| *s < 0)
        .map(|(p, _)| p.to_string())
        .collect()
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Erreur {
    SaisieNonAutorisee,
    ValidationParSaisisseur,
    StatutEntreeInvalide,
    InventaireSansMotif,
    AnnulationHorsLigne,
    TransitionCuisineInvalide,
}

/// STK-4 [M7-Q1-A] : entree a_valider hors dispo ; validee => mouvement achat.
/// Rejet => mouvement inverse (annule l'effet si validee, sinon trace a zero).
pub fn valider_entree(
    saisie_par: &str,
    validee_par: &str,
    peut_saisir: bool,
    lignes: &[(String, i64)],
) -> Result<Vec<Mouvement>, Erreur> {
    if !peut_saisir {
        return Err(Erreur::SaisieNonAutorisee);
    }
    if saisie_par == validee_par {
        return Err(Erreur::ValidationParSaisisseur);
    } // M7 separation
    Ok(lignes
        .iter()
        .map(|(p, q)| Mouvement {
            produit: p.clone(),
            quantite: *q,
            type_: "achat".into(),
        })
        .collect())
}

pub fn rejeter_entree(validee: bool, lignes: &[(String, i64)]) -> Vec<Mouvement> {
    if !validee {
        return vec![];
    } // jamais entree en dispo => rien a inverser
    lignes
        .iter()
        .map(|(p, q)| Mouvement {
            produit: p.clone(),
            quantite: -*q,
            type_: "rejet_entree".into(),
        })
        .collect()
}

/// STK-5 : ecart = comptee - theorique (convention M1 inventaires.ecart).
/// Ecart != 0 => motif obligatoire ; mouvement correction du montant de l'ecart.
pub fn mouvement_inventaire(
    produit: &str,
    theorique: i64,
    comptee: i64,
    motif: &str,
) -> Result<Option<Mouvement>, Erreur> {
    let ecart = comptee - theorique;
    if ecart == 0 {
        return Ok(None);
    }
    if motif.trim().is_empty() {
        return Err(Erreur::InventaireSansMotif);
    }
    Ok(Some(Mouvement {
        produit: produit.to_string(),
        quantite: ecart,
        type_: "correction".into(),
    }))
}

/// STK-6 : pertes en quantites (casses, annulations apres prepa, offerts, ecarts negatifs).
/// Valorisation au cout reservee proprio (R3) : le module renvoie quantites + cout unitaire fige,
/// l'affichage valeur est filtre par role en UI (I7/I8).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Perte {
    pub produit: String,
    pub quantite: i64,
    pub cout_unitaire: i64,
    pub origine: String,
}
pub fn valorisation_pertes(pertes: &[Perte], est_proprietaire: bool) -> Option<i64> {
    if !est_proprietaire {
        return None;
    } // R3
    Some(pertes.iter().map(|p| p.quantite * p.cout_unitaire).sum())
}

/// CUI-3 : statuts plat. Premier enregistre gagne (arbitrage central en persistance M1) ;
/// ici : transition autorisee ou refusee. CUI-5 : envoye_papier sans statuts, annulation offline impossible.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StatutPlat {
    Envoye,
    EnvoyePapier,
    EnPreparation,
    Pret,
    Servi,
    Annule,
}

pub fn transition_cuisine(
    actuel: StatutPlat,
    vise: StatutPlat,
    offline: bool,
) -> Result<StatutPlat, Erreur> {
    if offline {
        return Err(Erreur::AnnulationHorsLigne);
    } // CUI-5 : pas d'annulation offline (ni statuts papier)
    let ok = matches!(
        (actuel, vise),
        (StatutPlat::Envoye, StatutPlat::EnPreparation)
        | (StatutPlat::Envoye, StatutPlat::Annule) // CUI-4 serveur tant qu'envoye
        | (StatutPlat::EnPreparation, StatutPlat::Pret)
        | (StatutPlat::EnPreparation, StatutPlat::Annule) // CUI-4 gerant R1 (verifie M6)
        | (StatutPlat::Pret, StatutPlat::Servi)
        | (StatutPlat::Pret, StatutPlat::Annule) // CUI-4 gerant R1, perte
    );
    if ok {
        Ok(vise)
    } else {
        Err(Erreur::TransitionCuisineInvalide)
    }
}

/// CUI-4 : annulation apres preparation (en_preparation/pret) = perte.
pub fn est_perte_apres_preparation(statut_au_moment: StatutPlat) -> bool {
    matches!(
        statut_au_moment,
        StatutPlat::EnPreparation | StatutPlat::Pret | StatutPlat::Servi
    )
}
