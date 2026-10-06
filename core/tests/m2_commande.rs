//! M2 - Commandes et paiement (spec v1.2 : CMD-1..6, PAI-1..3, PAI-5, PAI-6, R4).
use snack_core::commande;

fn ligne(id: &str, produit: &str, qte: u32, prix: i64) -> commande::Ligne {
    commande::Ligne {
        id: id.into(),
        produit_id: produit.into(),
        quantite: qte,
        prix_unitaire_fige: prix,
        cout_unitaire_fige: 0,
        remise_montant: 0,
        est_offert: false,
    }
}

fn reg_especes(montant: i64, recu: i64, monnaie: i64) -> commande::Reglement {
    commande::Reglement {
        mode: "especes".into(),
        montant,
        montant_recu: Some(recu),
        monnaie_rendue: monnaie,
        pourboire: 0,
    }
}

const MODES: &[&str] = &["especes", "mobile", "ardoise"];

#[test]
fn ouvrir_ajouter_total() {
    let mut c = commande::ouvrir("cmd-1", "srv-awa", Some("T3"), commande::Mode::Table);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-biere", 2, 1500)).unwrap();
    commande::ajouter_ligne(&mut c, ligne("l2", "p-eau", 1, 500)).unwrap();
    assert_eq!(commande::total_net(&c), 3500);
}

#[test]
fn retrait_exige_motif() {
    let mut c = commande::ouvrir("cmd-2", "srv-awa", None, commande::Mode::Comptoir);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-biere", 1, 1500)).unwrap();
    assert_eq!(
        commande::retirer_ligne(&mut c, "l1", "   "),
        Err(commande::Erreur::BoissonSansMotif)
    );
    commande::retirer_ligne(&mut c, "l1", "client parti").unwrap();
    assert_eq!(commande::total_net(&c), 0);
}

#[test]
fn reglement_exact_et_monnaie() {
    let mut c = commande::ouvrir("cmd-3", "srv-awa", None, commande::Mode::Comptoir);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-eau", 2, 500)).unwrap();
    commande::regler(&mut c, vec![reg_especes(1000, 1500, 500)], MODES, false).unwrap();
    assert_eq!(c.statut, commande::Statut::Payee);
}

#[test]
fn reglement_inexact_refuse() {
    let mut c = commande::ouvrir("cmd-4", "srv-awa", None, commande::Mode::Comptoir);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-eau", 2, 500)).unwrap();
    assert_eq!(
        commande::regler(&mut c, vec![reg_especes(800, 800, 0)], MODES, false),
        Err(commande::Erreur::TotalInexact)
    );
}

#[test]
fn ardoise_exclusive_et_totale() {
    let mut c = commande::ouvrir("cmd-5", "srv-awa", None, commande::Mode::Comptoir);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-eau", 2, 500)).unwrap();
    let mixte = vec![
        commande::Reglement {
            mode: "ardoise".into(),
            montant: 500,
            montant_recu: None,
            monnaie_rendue: 0,
            pourboire: 0,
        },
        reg_especes(500, 500, 0),
    ];
    assert_eq!(
        commande::regler(&mut c, mixte, MODES, false),
        Err(commande::Erreur::ArdoiseNonExclusive)
    );
}

#[test]
fn r4_pas_de_modif_apres_paiement() {
    let mut c = commande::ouvrir("cmd-6", "srv-awa", None, commande::Mode::Comptoir);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-eau", 1, 500)).unwrap();
    commande::regler(&mut c, vec![reg_especes(500, 500, 0)], MODES, false).unwrap();
    assert_eq!(
        commande::interdire_modification_si_payee(&c),
        Err(commande::Erreur::CommandePayee)
    );
}

#[test]
fn conversion_comptoir_vers_table() {
    let mut c = commande::ouvrir("cmd-7", "srv-awa", None, commande::Mode::Comptoir);
    commande::convertir_comptoir_vers_table(&mut c, "srv-awa", "T1").unwrap();
    assert_eq!(c.mode, commande::Mode::Table);
    assert_eq!(
        commande::convertir_comptoir_vers_table(&mut c, "srv-awa", "T2"),
        Err(commande::Erreur::ConversionInterdite)
    );
}

#[test]
fn remise_exige_r1() {
    let mut c = commande::ouvrir("cmd-8", "srv-awa", None, commande::Mode::Comptoir);
    commande::ajouter_ligne(&mut c, ligne("l1", "p-eau", 1, 500)).unwrap();
    assert_eq!(
        commande::appliquer_remise(&mut c, "l1", 100, false, false),
        Err(commande::Erreur::RemiseSansAutorisation)
    );
    commande::appliquer_remise(&mut c, "l1", 100, false, true).unwrap();
    assert_eq!(commande::total_net(&c), 400);
}
