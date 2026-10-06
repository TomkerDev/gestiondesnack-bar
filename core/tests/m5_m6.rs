//! M5 caisse/journee (CAI-1..6, R2, R5) + M6 securite (SEC-1..3, R1, matrice).
use snack_core::{caisse, securite};

#[test]
fn especes_attendues_formule() {
    // fond + especes - monnaie + tips_esp + remb_esp - sorties
    assert_eq!(
        caisse::especes_attendues(5000, 13500, 500, 200, 1000, 300),
        18900
    );
}

#[test]
fn cloture_tolerance_et_forcage() {
    let (st, ecart) = caisse::cloturer_caisse(18900, 18900, 500, "", "", false, false).unwrap();
    assert_eq!((st, ecart), (caisse::StatutCaisse::Close, 0));
    assert_eq!(
        caisse::cloturer_caisse(19000, 18000, 500, "", "", false, false),
        Err(caisse::Erreur::EcartNonJustifie)
    );
    assert_eq!(
        caisse::cloturer_caisse(19000, 18000, 500, "", "", false, true),
        Err(caisse::Erreur::ForcageSansAutorisation)
    );
    let (stf, _) =
        caisse::cloturer_caisse(19000, 18000, 500, "tiroir bloque", "vu gerant", true, true)
            .unwrap();
    assert_eq!(stf, caisse::StatutCaisse::Forcee);
}

#[test]
fn journee_cycle_fermeture() {
    use caisse::StatutJournee::*;
    assert_eq!(
        caisse::fermer_journee(Ouverte, true),
        Err(caisse::Erreur::JourneeNonEnCloture)
    );
    assert_eq!(
        caisse::fermer_journee(EnCloture, false),
        Err(caisse::Erreur::CaissesNonCloses)
    );
    assert_eq!(caisse::fermer_journee(EnCloture, true), Ok(Close));
    assert_eq!(
        caisse::fermer_journee(Close, true),
        Err(caisse::Erreur::JourneeDejaClose)
    );
}

#[test]
fn rapprochement_mobile() {
    let regs = vec![("pay-1".to_string(), 2000), ("pay-2".to_string(), 1500)];
    let releve = vec![("pay-1".to_string(), 2000)];
    let (ok, litiges) = caisse::rapprocher_mobile(&regs, &releve);
    assert_eq!(ok, vec!["pay-1".to_string()]);
    assert_eq!(litiges, vec!["pay-2".to_string()]);
}

#[test]
fn pin_et_blocage() {
    assert!(securite::pin_valide("1234").is_ok());
    assert_eq!(
        securite::pin_valide("123"),
        Err(securite::Erreur::PinTropCourt)
    );
    assert_eq!(
        securite::pin_valide("abcd"),
        Err(securite::Erreur::PinTropCourt)
    );
    assert_eq!(securite::duree_blocage(4), 0);
    assert_eq!(securite::duree_blocage(5), 300);
    assert_eq!(securite::duree_blocage(6), 900);
    assert!(securite::session_valide(1000, 1100).is_ok());
    assert_eq!(
        securite::session_valide(1000, 1200),
        Err(securite::Erreur::SessionExpiree)
    );
}

#[test]
fn matrice_droits() {
    use securite::{Action::*, Role::*};
    assert!(securite::autorise(Serveur, VendreEncaisser).is_ok());
    assert_eq!(
        securite::autorise(Serveur, RemiseOffert),
        Err(securite::Erreur::DroitInsuffisant)
    );
    assert!(securite::autorise(Gerant, RemiseOffert).is_ok());
    assert_eq!(
        securite::autorise(Gerant, VoirCoutsMarges),
        Err(securite::Erreur::DroitInsuffisant)
    );
    assert!(securite::autorise(Proprietaire, VoirCoutsMarges).is_ok());
}

#[test]
fn jeton_r1_usage_unique_60s() {
    let mut j = securite::creer_jeton("remise", Some("cmd-1"), Some(500), "awa", "ibrahim", 1000);
    securite::consommer_jeton(&mut j, "remise", Some("cmd-1"), Some(500), 1030, false).unwrap();
    assert_eq!(
        securite::consommer_jeton(&mut j, "remise", Some("cmd-1"), Some(500), 1040, false),
        Err(securite::Erreur::JetonDejaConsomme)
    );
    let mut j2 = securite::creer_jeton("remise", Some("cmd-1"), Some(500), "awa", "ibrahim", 1000);
    assert_eq!(
        securite::consommer_jeton(&mut j2, "remise", Some("cmd-1"), Some(500), 1061, false),
        Err(securite::Erreur::JetonExpire)
    );
    let mut j3 = securite::creer_jeton("remise", Some("cmd-1"), Some(500), "awa", "ibrahim", 1000);
    assert_eq!(
        securite::consommer_jeton(&mut j3, "remise", Some("cmd-1"), Some(500), 1030, true),
        Err(securite::Erreur::R1HorsLigne)
    );
}
