import test from "node:test";
import assert from "node:assert/strict";
import { session, ouvrirSession, fermerSession, majConnexion, VIDES } from "../src/lib/session.js";

test("SEC-1 : code personnel < 4 chiffres refusé", () => {
  const r = ouvrirSession({ identifiant: "12" });
  assert.equal(r.ok, false);
  assert.match(r.raison, /SEC-1/);
});

test("SEC-1 : code valide → session ouverte avec horodatage, store notifié", () => {
  let recu = null;
  const desab = session.subscribe((v) => (recu = v));
  const r = ouvrirSession({ identifiant: "1234", role: "serveur", appareil: "tel-1" },
                          () => "2026-10-06T12:00:00Z");
  assert.equal(r.ok, true);
  assert.equal(recu.identifiant, "1234");
  assert.equal(recu.role, "serveur");
  assert.equal(recu.debut, "2026-10-06T12:00:00Z");
  assert.equal(recu.enLigne, true);
  desab();
});

test("fermerSession remet l'état vide", () => {
  ouvrirSession({ identifiant: "9999" });
  let recu = null;
  const desab = session.subscribe((v) => (recu = v));
  fermerSession();
  assert.deepEqual(recu, VIDES);
  desab();
});

test("majConnexion propage l'état réseau sans perdre l'identité", () => {
  ouvrirSession({ identifiant: "5555", role: "gerant" });
  majConnexion(false);
  let recu = null;
  const desab = session.subscribe((v) => (recu = v));
  assert.equal(recu.enLigne, false);
  assert.equal(recu.identifiant, "5555");
  desab();
});
