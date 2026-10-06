//! M2 - Commandes et paiement, Rust pur sans I/O.
//! Spec v1.2 : CMD-1..6, PAI-1..3, PAI-5, PAI-6, R4. i64 only, IDs UUID (CMD-6).
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Table,
    Comptoir,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Statut {
    Ouverte,
    Payee,
    PayeeSansAddition,
    Annulee,
}
// CMD-7 [M7-Q2-A] : PayeeSansAddition = offline, reimpression avant cloture.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Reglement {
    pub mode: String,
    pub montant: i64,
    pub montant_recu: Option<i64>, // PAI-3
    pub monnaie_rendue: i64,       // PAI-3
    pub pourboire: i64,            // PAI-6 hors total/CA
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Ligne {
    pub id: String,
    pub produit_id: String,
    pub quantite: u32,
    pub prix_unitaire_fige: i64, // PRX-3
    pub cout_unitaire_fige: i64, // PRX-3
    pub remise_montant: i64,     // PAI-5 resolu
    pub est_offert: bool,        // PAI-5 100%
}

impl Ligne {
    pub fn net(&self) -> i64 {
        if self.est_offert {
            return 0;
        }
        (self.quantite as i64) * self.prix_unitaire_fige - self.remise_montant
    }
}

#[derive(Debug, Clone)]
pub struct Commande {
    pub id: String,
    pub serveur_id: String, // CMD-4
    pub table: Option<String>,
    pub mode: Mode, // CMD-1
    pub statut: Statut,
    pub lignes: HashMap<String, Ligne>,
    pub reglements: Vec<Reglement>,
    pub addition_imprimee: bool, // CMD-7
    pub version: u64,            // OFF-3
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Erreur {
    CommandePayee,
    CommandeAnnulee,
    ConversionInterdite,
    ConversionParAutre,
    TransfertLignesTableDifferente,
    LigneIntrouvable,
    BoissonSansMotif,
    MontantInvalide,
    TotalInexact,
    ArdoiseNonExclusive,
    ModeInconnu,
    RemiseSansAutorisation,
}

/// CMD-1/CMD-4/CMD-6 : ouvrir (UUID fourni par l'appareil).
pub fn ouvrir(id: &str, serveur_id: &str, table: Option<&str>, mode: Mode) -> Commande {
    Commande {
        id: id.to_string(),
        serveur_id: serveur_id.to_string(),
        table: table.map(|t| t.to_string()),
        mode,
        statut: Statut::Ouverte,
        lignes: HashMap::new(),
        reglements: Vec::new(),
        addition_imprimee: false,
        version: 1,
    }
}

fn exige_ouverte(c: &Commande) -> Result<(), Erreur> {
    match c.statut {
        Statut::Ouverte => Ok(()),
        Statut::Payee | Statut::PayeeSansAddition => Err(Erreur::CommandePayee), // R4
        Statut::Annulee => Err(Erreur::CommandeAnnulee),
    }
}

pub fn ajouter_ligne(c: &mut Commande, ligne: Ligne) -> Result<(), Erreur> {
    exige_ouverte(c)?;
    if ligne.quantite == 0 || ligne.prix_unitaire_fige < 0 {
        return Err(Erreur::MontantInvalide);
    }
    c.lignes.insert(ligne.id.clone(), ligne);
    c.version += 1;
    Ok(())
}

/// CMD-5 : retrait boisson avant paiement, motif obligatoire.
pub fn retirer_ligne(c: &mut Commande, ligne_id: &str, motif: &str) -> Result<(), Erreur> {
    exige_ouverte(c)?;
    if motif.trim().is_empty() {
        return Err(Erreur::BoissonSansMotif);
    }
    c.lignes
        .remove(ligne_id)
        .map(|_| ())
        .ok_or(Erreur::LigneIntrouvable)?;
    c.version += 1;
    Ok(())
}

/// CMD-2 : transfert lignes entre commandes meme table, avant paiement.
pub fn transferer_lignes(
    src: &mut Commande,
    dst: &mut Commande,
    ids: &[&str],
    trace: &mut Vec<String>,
) -> Result<(), Erreur> {
    exige_ouverte(src)?;
    exige_ouverte(dst)?;
    if src.table != dst.table {
        return Err(Erreur::TransfertLignesTableDifferente);
    }
    for id in ids {
        let l = src.lignes.remove(*id).ok_or(Erreur::LigneIntrouvable)?;
        trace.push(l.id.clone());
        dst.lignes.insert(l.id.clone(), l);
    }
    src.version += 1;
    dst.version += 1;
    Ok(())
}

/// CMD-3 : comptoir -> table par createur seul. Inverse impossible.
pub fn convertir_comptoir_vers_table(
    c: &mut Commande,
    demandeur: &str,
    table: &str,
) -> Result<(), Erreur> {
    exige_ouverte(c)?;
    match c.mode {
        Mode::Comptoir => {
            if c.serveur_id != demandeur {
                return Err(Erreur::ConversionParAutre);
            }
            c.mode = Mode::Table;
            c.table = Some(table.to_string());
            c.version += 1;
            Ok(())
        }
        Mode::Table => Err(Erreur::ConversionInterdite),
    }
}

/// CMD-4 : transfert serveur (acceptation verifiee en M6).
pub fn transferer_serveur(c: &mut Commande, nouveau: &str) -> Result<(), Erreur> {
    exige_ouverte(c)?;
    c.serveur_id = nouveau.to_string();
    c.version += 1;
    Ok(())
}

/// Total net hors pourboires (PAI-6).
pub fn total_net(c: &Commande) -> i64 {
    c.lignes.values().map(|l| l.net()).sum()
}

/// PAI-5 : remise/offert par ligne, R1 obligatoire (verifie en M6).
pub fn appliquer_remise(
    c: &mut Commande,
    ligne_id: &str,
    remise: i64,
    offert: bool,
    r1: bool,
) -> Result<(), Erreur> {
    exige_ouverte(c)?;
    if !r1 {
        return Err(Erreur::RemiseSansAutorisation);
    }
    if remise < 0 {
        return Err(Erreur::MontantInvalide);
    }
    let l = c.lignes.get_mut(ligne_id).ok_or(Erreur::LigneIntrouvable)?;
    l.remise_montant = remise;
    l.est_offert = offert;
    c.version += 1;
    Ok(())
}

/// PAI-2 : somme == net ; especes+mobile combinables ; ardoise exclusive+totale.
/// PAI-3 : especes => recu - montant == monnaie, recu >= montant.
pub fn regler(
    c: &mut Commande,
    regs: Vec<Reglement>,
    modes: &[&str],
    sans_addition: bool,
) -> Result<(), Erreur> {
    exige_ouverte(c)?;
    let net = total_net(c);
    let mut somme = 0i64;
    let mut ardoise = false;
    for r in &regs {
        if !modes.contains(&r.mode.as_str()) {
            return Err(Erreur::ModeInconnu);
        }
        if r.montant <= 0 || r.pourboire < 0 {
            return Err(Erreur::MontantInvalide);
        }
        if r.mode == "ardoise" {
            ardoise = true;
        }
        if r.mode == "especes" {
            let recu = r.montant_recu.ok_or(Erreur::MontantInvalide)?;
            if recu < r.montant || recu - r.montant != r.monnaie_rendue {
                return Err(Erreur::MontantInvalide);
            }
        }
        somme += r.montant; // PAI-6 : pourboire exclu
    }
    if ardoise && regs.len() > 1 {
        return Err(Erreur::ArdoiseNonExclusive);
    }
    if ardoise && somme != net {
        return Err(Erreur::ArdoiseNonExclusive);
    }
    if somme != net {
        return Err(Erreur::TotalInexact);
    }
    c.reglements = regs;
    c.statut = if sans_addition {
        Statut::PayeeSansAddition
    } else {
        Statut::Payee
    };
    c.version += 1;
    Ok(())
}

/// R4 : refus modification directe si payee ; correction = enregistrement distinct.
pub fn interdire_modification_si_payee(c: &Commande) -> Result<(), Erreur> {
    exige_ouverte(c)
}
