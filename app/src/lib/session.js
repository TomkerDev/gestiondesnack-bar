/* I-INT · Session applicative (pur JS, contract compatible store Svelte :
   subscribe reçoit la valeur, retourne la désinscription).
   SEC-1 : identifiant personnel ≥ 4 chiffres, appareil, rôle, heure de début.
   Le PIN lui-même ne quitte jamais l'appareil ici (SEC-2 : on garde l'identifiant). */

import { creerClient } from "./api.js";

function store(valeur) {
  const abonnes = new Set();
  return {
    subscribe(fn) { abonnes.add(fn); fn(valeur); return () => abonnes.delete(fn); },
    set(v) { valeur = v; for (const ab of abonnes) ab(valeur); }
  };
}

export const VIDES = { identifiant: "", role: "", appareil: "", debut: "", enLigne: true };

export const session = store(VIDES);

export function ouvrirSession({ identifiant, role = "serveur", appareil }, horloge = () => new Date().toISOString()) {
  if (!/^\d{4,}$/.test(String(identifiant))) return { ok: false, raison: "Code personnel : 4 chiffres minimum (SEC-1)" };
  session.set({ identifiant: String(identifiant), role, appareil: appareil ?? "appareil-local", debut: horloge(), enLigne: true });
  return { ok: true, session: { ...VIDES } };
}

export function fermerSession() { session.set(VIDES); return { ok: true }; }

export function majConnexion(enLigne) {
  let courante = VIDES;
  session.subscribe((v) => (courante = v))();
  session.set({ ...courante, enLigne });
}

export { creerClient };
