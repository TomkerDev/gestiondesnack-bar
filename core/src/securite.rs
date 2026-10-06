//! M6 - Securite et audit, Rust pur sans I/O.
//! Spec v1.2 : SEC-1..3, R1 [M7-Q5-A], matrice §3, R3.
//! Miroir : tests_m6/m6_mirror.py.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Role {
    Serveur,
    Gerant,
    Proprietaire,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Action {
    VendreEncaisser,
    RetirerBoissonNonPayee,
    AnnulerAvantPrepa,
    AnnulerApresPrepa,
    RemiseOffert,
    DeblocagePlafond,
    Correction,
    FixerPrixPlafond,
    SaisirEntree,
    ValiderEntree,
    InventaireFondForcageClotureJournee,
    VoirCoutsMarges,
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Erreur {
    PinTropCourt,
    CompteBloque,
    SessionExpiree,
    DroitInsuffisant,
    JetonExpire,
    JetonDejaConsomme,
    JetonInvalide,
    R1HorsLigne,
}
/// SEC-1 : PIN >= 4 chiffres.
pub fn pin_valide(pin: &str) -> Result<(), Erreur> {
    if pin.len() >= 4 && pin.chars().all(|c| c.is_ascii_digit()) {
        Ok(())
    } else {
        Err(Erreur::PinTropCourt)
    }
}
/// SEC-1 [M7-Q5-A] : 5 echecs => 5 min, 6e et + => 15 min. 0 sinon.
pub fn duree_blocage(nb_echecs: u32) -> u64 {
    if nb_echecs < 5 {
        0
    } else if nb_echecs == 5 {
        300
    } else {
        900
    }
}
/// SEC-1 : verrou auto apres 2 min d'inactivite (120 s).
pub fn session_valide(derniere_activite: i64, maintenant: i64) -> Result<(), Erreur> {
    if maintenant - derniere_activite <= 120 {
        Ok(())
    } else {
        Err(Erreur::SessionExpiree)
    }
}
/// Matrice §3. Proprietaire = tout. Gerant = tout sauf VoirCoutsMarges.
/// Serveur = ventes + retraits avant prepa seulement (+ saisie si designe, gere en M4).
pub fn autorise(role: Role, action: Action) -> Result<(), Erreur> {
    let ok = match role {
        Role::Proprietaire => true,
        Role::Gerant => action != Action::VoirCoutsMarges,
        Role::Serveur => matches!(
            action,
            Action::VendreEncaisser | Action::RetirerBoissonNonPayee | Action::AnnulerAvantPrepa
        ),
    };
    if ok {
        Ok(())
    } else {
        Err(Erreur::DroitInsuffisant)
    }
}
/// R1 [M7-Q5-A] : jeton 1 usage, lie (acte, commande, montant, demandeur), expire 60 s.
#[derive(Debug, Clone)]
pub struct Jeton {
    pub acte: String,
    pub commande: Option<String>,
    pub montant: Option<i64>,
    pub demandeur: String,
    pub autorise_par: String,
    pub cree_a: i64,
    pub expire_a: i64,
    pub consomme: bool,
}
pub fn creer_jeton(
    acte: &str,
    commande: Option<&str>,
    montant: Option<i64>,
    demandeur: &str,
    par: &str,
    maintenant: i64,
) -> Jeton {
    Jeton {
        acte: acte.into(),
        commande: commande.map(|s| s.into()),
        montant,
        demandeur: demandeur.into(),
        autorise_par: par.into(),
        cree_a: maintenant,
        expire_a: maintenant + 60,
        consomme: false,
    }
}
/// Verifie + consomme. Offline => refuse (R1 indisponible hors ligne).
pub fn consommer_jeton(
    j: &mut Jeton,
    acte: &str,
    commande: Option<&str>,
    montant: Option<i64>,
    maintenant: i64,
    offline: bool,
) -> Result<(), Erreur> {
    if offline {
        return Err(Erreur::R1HorsLigne);
    }
    if j.consomme {
        return Err(Erreur::JetonDejaConsomme);
    }
    if maintenant > j.expire_a {
        return Err(Erreur::JetonExpire);
    }
    if j.acte != acte || j.commande.as_deref() != commande || j.montant != montant {
        return Err(Erreur::JetonInvalide);
    }
    j.consomme = true;
    Ok(())
}
