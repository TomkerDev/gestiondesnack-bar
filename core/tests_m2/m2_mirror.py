"""Miroir Python de core/src/commande.rs — memes regles, memes noms de tests.
Rust non installe ici : ce miroir est EXECUTE. Le .rs reste la reference.
"""
from dataclasses import dataclass, field

class Erreur(Exception):
    pass

class CommandePayee(Erreur): pass
class CommandeAnnulee(Erreur): pass
class ConversionInterdite(Erreur): pass
class ConversionParAutre(Erreur): pass
class TransfertTableDifferente(Erreur): pass
class LigneIntrouvable(Erreur): pass
class BoissonSansMotif(Erreur): pass
class MontantInvalide(Erreur): pass
class TotalInexact(Erreur): pass
class ArdoiseNonExclusive(Erreur): pass
class ModeInconnu(Erreur): pass
class RemiseSansAutorisation(Erreur): pass

@dataclass
class Reglement:
    mode: str
    montant: int
    montant_recu: int | None = None
    monnaie_rendue: int = 0
    pourboire: int = 0

@dataclass
class Ligne:
    id: str
    produit_id: str
    quantite: int
    prix: int
    cout: int = 0
    remise: int = 0
    offert: bool = False
    def net(self):
        return 0 if self.offert else self.quantite * self.prix - self.remise

@dataclass
class Commande:
    id: str
    serveur: str
    table: str | None
    mode: str  # table|comptoir
    statut: str = "ouverte"
    lignes: dict = field(default_factory=dict)
    reglements: list = field(default_factory=list)
    version: int = 1

def _ouverte(c):
    if c.statut in ("payee", "payee_sans_addition"):
        raise CommandePayee("R4")
    if c.statut == "annulee":
        raise CommandeAnnulee()

def ajouter_ligne(c, l):
    _ouverte(c)
    if l.quantite <= 0 or l.prix < 0:
        raise MontantInvalide()
    c.lignes[l.id] = l
    c.version += 1

def retirer_ligne(c, lid, motif):
    _ouverte(c)
    if not motif.strip():
        raise BoissonSansMotif()  # CMD-5
    if lid not in c.lignes:
        raise LigneIntrouvable()
    del c.lignes[lid]
    c.version += 1

def transferer_lignes(src, dst, ids, trace):
    _ouverte(src); _ouverte(dst)
    if src.table != dst.table:
        raise TransfertTableDifferente()  # CMD-2
    for i in ids:
        if i not in src.lignes:
            raise LigneIntrouvable()
        trace.append(i)
        dst.lignes[i] = src.lignes.pop(i)
    src.version += 1; dst.version += 1

def convertir(c, demandeur, table):
    _ouverte(c)
    if c.mode == "table":
        raise ConversionInterdite()  # CMD-3
    if c.serveur != demandeur:
        raise ConversionParAutre()
    c.mode = "table"; c.table = table; c.version += 1

def transferer_serveur(c, nouveau):
    _ouverte(c); c.serveur = nouveau; c.version += 1  # CMD-4

def total_net(c):
    return sum(l.net() for l in c.lignes.values())  # PAI-6: tips exclus

def appliquer_remise(c, lid, remise, offert, r1):
    _ouverte(c)
    if not r1:
        raise RemiseSansAutorisation()  # PAI-5
    if remise < 0:
        raise MontantInvalide()
    if lid not in c.lignes:
        raise LigneIntrouvable()
    c.lignes[lid].remise = remise; c.lignes[lid].offert = offert; c.version += 1

def regler(c, regs, modes, sans_addition=False):
    _ouverte(c)
    net = total_net(c)
    somme, ardoise = 0, False
    for r in regs:
        if r.mode not in modes:
            raise ModeInconnu()  # PAI-1
        if r.montant <= 0 or r.pourboire < 0:
            raise MontantInvalide()
        if r.mode == "ardoise":
            ardoise = True
        if r.mode == "especes":
            if r.montant_recu is None or r.montant_recu < r.montant:
                raise MontantInvalide()  # PAI-3
            if r.montant_recu - r.montant != r.monnaie_rendue:
                raise MontantInvalide()
        somme += r.montant
    if ardoise and len(regs) > 1:
        raise ArdoiseNonExclusive()  # PAI-2
    if ardoise and somme != net:
        raise ArdoiseNonExclusive()
    if somme != net:
        raise TotalInexact()  # PAI-2
    c.reglements = regs
    c.statut = "payee_sans_addition" if sans_addition else "payee"
    c.version += 1
