//! M3 ardoise (ARD-1..6) + M4 stock/cuisine (STK-1..6, CUI-3..5).
use snack_core::{ardoise, stock};

#[test]
fn decision_vente_plafond() {
    let client = ardoise::Client {
        id: "cl-1".into(),
        plafond: 5000,
        solde_du: 4000,
    };
    assert_eq!(
        ardoise::decider_vente(Some(&client), 1000),
        ardoise::Decision::Accepte
    );
    assert_eq!(
        ardoise::decider_vente(Some(&client), 1500),
        ardoise::Decision::RefuseDeblocable
    );
    assert_eq!(ardoise::decider_vente(None, 500), ardoise::Decision::Refuse);
}

#[test]
fn deblocage_exige_r1_jamais_offline() {
    assert_eq!(
        ardoise::appliquer_deblocage(4000, 2000, false),
        Err(ardoise::Erreur::DeblocageSansAutorisation)
    );
    assert_eq!(ardoise::appliquer_deblocage(4000, 2000, true), Ok(6000));
    assert_eq!(
        ardoise::tenter_deblocage_offline(),
        Err(ardoise::Erreur::DeblocageHorsLigne)
    );
}

#[test]
fn remboursement_especes_augmente_attendues() {
    let (nouveau, delta) = ardoise::appliquer_remboursement(3000, 1000, "especes").unwrap();
    assert_eq!((nouveau, delta), (2000, 1000));
    let (nm, dm) = ardoise::appliquer_remboursement(3000, 1000, "mobile").unwrap();
    assert_eq!((nm, dm), (2000, 0));
}

#[test]
fn stock_somme_et_vente_negative() {
    let mut mvts = vec![stock::Mouvement {
        produit: "biere".into(),
        quantite: 24,
        type_: "achat".into(),
    }];
    assert_eq!(stock::stock_disponible(&mvts, "biere"), 24);
    let alerte = stock::appliquer_vente(&mut mvts, "biere", 30);
    assert!(alerte);
    assert_eq!(stock::stock_disponible(&mvts, "biere"), -6);
    assert_eq!(stock::produits_negatifs(&mvts), vec!["biere".to_string()]);
}

#[test]
fn entree_double_controle() {
    let lignes = vec![("biere".to_string(), 24)];
    assert_eq!(
        stock::valider_entree("awa", "awa", true, &lignes),
        Err(stock::Erreur::ValidationParSaisisseur)
    );
    assert_eq!(
        stock::valider_entree("awa", "ibrahim", false, &lignes),
        Err(stock::Erreur::SaisieNonAutorisee)
    );
    assert_eq!(
        stock::valider_entree("awa", "ibrahim", true, &lignes)
            .unwrap()
            .len(),
        1
    );
    assert_eq!(stock::rejeter_entree(false, &lignes).len(), 0);
}

#[test]
fn inventaire_motif_obligatoire() {
    assert_eq!(
        stock::mouvement_inventaire("biere", 20, 18, ""),
        Err(stock::Erreur::InventaireSansMotif)
    );
    let m = stock::mouvement_inventaire("biere", 20, 18, "casse")
        .unwrap()
        .unwrap();
    assert_eq!(m.quantite, -2);
    assert!(stock::mouvement_inventaire("biere", 20, 20, "")
        .unwrap()
        .is_none());
}

#[test]
fn cuisine_transitions() {
    use stock::StatutPlat::*;
    assert_eq!(
        stock::transition_cuisine(Envoye, EnPreparation, false),
        Ok(EnPreparation)
    );
    assert_eq!(
        stock::transition_cuisine(Envoye, Servi, false),
        Err(stock::Erreur::TransitionCuisineInvalide)
    );
    assert!(stock::est_perte_apres_preparation(Pret));
    assert!(!stock::est_perte_apres_preparation(Envoye));
}
