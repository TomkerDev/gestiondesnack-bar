"""Miroir Python de core/src/ardoise.rs."""
from dataclasses import dataclass

class Erreur(Exception): pass
class MontantInvalide(Erreur): pass
class DeblocageSansAutorisation(Erreur): pass
class DeblocageHorsLigne(Erreur): pass
class RemboursementInvalide(Erreur): pass

@dataclass
class Client:
    id: str
    plafond: int
    solde: int

def decider(client, montant):
    if montant <= 0 or client is None:
        return "refuse"  # ARD-2
    return "accepte" if client.solde + montant <= client.plafond else "refuse_deblocable"  # ARD-2/ARD-3

def appliquer_deblocage(solde, montant, r1):
    if not r1:
        raise DeblocageSansAutorisation()  # ARD-3
    if montant <= 0:
        raise MontantInvalide()
    return solde + montant  # plafond inchange

def decider_offline(snap, montant):
    if montant <= 0:
        raise MontantInvalide()
    if snap is None:
        return "refuse"
    return "accepte" if snap.solde + montant <= snap.plafond else "refuse"  # ARD-6: pas de deblocage

def tenter_deblocage_offline():
    raise DeblocageHorsLigne()  # ARD-6

def appliquer_remboursement(solde, montant, mode):
    if montant <= 0 or solde <= 0:
        raise RemboursementInvalide()  # ARD-4
    return max(0, solde - montant), (montant if mode == "especes" else 0)

def controler_resynchro(lignes, plafonds):
    alertes = []
    for cid, avant, ventes, remb in lignes:
        nouveau = avant + sum(ventes) - sum(remb)
        if nouveau > plafonds.get(cid, 0):
            alertes.append((cid, nouveau, plafonds[cid]))  # ARD-5/ARD-6
    return alertes

def impact_vente(montant):
    return (montant, 0)  # ARD-4 : CA oui, especes non
