"""Miroir Python de core/src/caisse.rs."""
class Erreur(Exception): pass
class JourneeDejaClose(Erreur): pass
class JourneeNonEnCloture(Erreur): pass
class CaissesNonCloses(Erreur): pass
class EcartNonJustifie(Erreur): pass
class ForcageSansAutorisation(Erreur): pass

def fermer_journee(statut, toutes_closes):
    if statut == "close":
        raise JourneeDejaClose()  # R5
    if statut == "ouverte":
        raise JourneeNonEnCloture()
    if not toutes_closes:
        raise CaissesNonCloses()  # CAI-1
    return "close"

def attendues(fond, especes, monnaie, tips, remb, sorties):
    return fond + especes - monnaie + tips + remb - sorties  # CAI-2 [M7-Q4-A]

def cloturer(compte, dues, tol, motif, comm, r1=False, forcee=False):
    if forcee:
        if not r1 or not motif.strip():
            raise ForcageSansAutorisation()  # CAI-5
        return ("forcee", compte - dues)
    ecart = compte - dues
    if abs(ecart) <= tol:
        return ("close", ecart)  # CAI-4 tolerance
    if not motif.strip() or not comm.strip():
        raise EcartNonJustifie()
    return ("close", ecart)

def rapprocher(regs, releve):
    d = dict(releve)
    ok = [i for i, m in regs if d.get(i) == m]
    return ok, [i for i, m in regs if d.get(i) != m]  # CAI-6

def imputer_correction(journee_courante):
    return journee_courante  # R5
