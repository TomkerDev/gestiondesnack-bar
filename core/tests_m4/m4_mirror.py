"""Miroir Python de core/src/stock.rs."""
from dataclasses import dataclass

class Erreur(Exception): pass
class SaisieNonAutorisee(Erreur): pass
class ValidationParSaisisseur(Erreur): pass
class InventaireSansMotif(Erreur): pass
class AnnulationHorsLigne(Erreur): pass
class TransitionCuisineInvalide(Erreur): pass

@dataclass
class Mvt:
    produit: str
    qte: int
    type: str = "vente"

def dispo(mvts, produit):
    return sum(m.qte for m in mvts if m.produit == produit)  # STK-2 somme

def vente(mvts, produit, qte):
    mvts.append(Mvt(produit, -qte, "vente"))
    return dispo(mvts, produit) < 0  # STK-3 alerte

def negatifs(mvts):
    tot = {}
    for m in mvts:
        tot[m.produit] = tot.get(m.produit, 0) + m.qte
    return sorted(p for p, s in tot.items() if s < 0)

def valider_entree(saisie_par, validee_par, peut_saisir, lignes):
    if not peut_saisir:
        raise SaisieNonAutorisee()  # STK-4
    if saisie_par == validee_par:
        raise ValidationParSaisisseur()  # M7 separation
    return [Mvt(p, q, "achat") for p, q in lignes]

def rejeter(validee, lignes):
    return [] if not validee else [Mvt(p, -q, "rejet_entree") for p, q in lignes]

def inventaire(produit, theorique, comptee, motif):
    ecart = comptee - theorique
    if ecart == 0:
        return None
    if not motif.strip():
        raise InventaireSansMotif()  # STK-5
    return Mvt(produit, ecart, "correction")

def valorisation(pertes, proprio):
    if not proprio:
        return None  # R3
    return sum(q * c for _, q, c in pertes)

TRANSITIONS = {("envoye", "preparation"), ("envoye", "annule"),
               ("preparation", "pret"), ("preparation", "annule"),
               ("pret", "servi"), ("pret", "annule")}

def transition(actuel, vise, offline=False):
    if offline:
        raise AnnulationHorsLigne()  # CUI-5
    if (actuel, vise) not in TRANSITIONS:
        raise TransitionCuisineInvalide()  # CUI-3
    return vise

def perte_apres_prepa(statut):
    return statut in ("preparation", "pret", "servi")  # CUI-4
