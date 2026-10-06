"""Miroir Python de core/src/securite.rs."""
class Erreur(Exception): pass
class PinTropCourt(Erreur): pass
class CompteBloque(Erreur): pass
class SessionExpiree(Erreur): pass
class DroitInsuffisant(Erreur): pass
class JetonExpire(Erreur): pass
class JetonDejaConsomme(Erreur): pass
class JetonInvalide(Erreur): pass
class R1HorsLigne(Erreur): pass

def pin_valide(pin):
    if len(pin) >= 4 and pin.isdigit():
        return True
    raise PinTropCourt()  # SEC-1

def duree_blocage(n):
    if n < 5: return 0
    return 300 if n == 5 else 900  # 5min puis 15min [M7-Q5-A]

def session_valide(derniere, maintenant):
    if maintenant - derniere <= 120:
        return True
    raise SessionExpiree()  # 2 min

GERANT_OK = {"vendre", "retirer", "annuler_avant", "annuler_apres", "remise", "deblocage",
             "correction", "prix", "saisir", "valider", "inventaire"}
SERVEUR_OK = {"vendre", "retirer", "annuler_avant"}

def autorise(role, action):
    if role == "proprietaire":
        return True
    if role == "gerant":
        if action == "couts":
            raise DroitInsuffisant()  # R3
        return True
    if action in SERVEUR_OK:
        return True
    raise DroitInsuffisant()  # §3

class Jeton:
    def __init__(self, acte, commande, montant, demandeur, par, t):
        self.acte, self.commande, self.montant = acte, commande, montant
        self.demandeur, self.par = demandeur, par
        self.expire, self.consomme = t + 60, False  # R1 60s

def consommer(j, acte, commande, montant, t, offline=False):
    if offline:
        raise R1HorsLigne()  # R1 indisponible offline
    if j.consomme:
        raise JetonDejaConsomme()
    if t > j.expire:
        raise JetonExpire()
    if j.acte != acte or j.commande != commande or j.montant != montant:
        raise JetonInvalide()
    j.consomme = True
