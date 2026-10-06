import test from "node:test";
import assert from "node:assert/strict";
import { creerClient, INTERDIT_HORS_LIGNE, FILE_HORS_LIGNE } from "../src/lib/api.js";

const rep = (body = {}, status = 200) => ({ ok: status < 400, status, json: async () => body });

test("INT-1 en ligne : l'appel HTTP part avec la bonne route et le JSON encodé", async () => {
  const appels = [];
  const c = creerClient({ base: "http://pc", fetchImpl: async (u, o) => { appels.push([u, o]); return rep({ id: 1 }); } });
  const r = await c.creerCommande([{ id: 9, q: 2 }]);
  assert.equal(r.ok, true);
  assert.equal(appels[0][0], "http://pc/api/commandes");
  assert.equal(appels[0][1].method, "POST");
  assert.equal(appels[0][1].body, JSON.stringify({ lignes: [{ id: 9, q: 2 }] }));
});

test("INT-2 erreur serveur : raison propagée, jamais d'exception", async () => {
  const c = creerClient({ fetchImpl: async () => rep({ raison: "Journée clôturée" }, 409) });
  const r = await c.creerCommande([]);
  assert.equal(r.ok, false);
  assert.equal(r.raison, "Journée clôturée");
});

test("INT-3 coupure en pleine requête → bascule hors ligne + action en file (OFF-1)", async () => {
  let compteur = 0;
  const c = creerClient({
    fetchImpl: async () => { compteur++; if (compteur === 1) throw new Error("réseau"); return rep({ ok: 1 }); },
    horloge: () => "2026-10-06T10:00:00Z"
  });
  const r1 = await c.creerCommande([{ id: 1 }]);
  assert.equal(c.etat.enLigne, false);
  assert.equal(r1.ok, true);          // la vente continue (OFF-1)
  assert.equal(r1.differe, true);
  assert.equal(c.etat.file.length, 1);
  assert.equal(c.etat.file[0].action, "prise_commande");
});

test("INT-4 hors ligne : encaissement en file, remise/R1/correction refusés avec raison (OFF-2)", async () => {
  const c = creerClient({ fetchImpl: async () => { throw new Error("réseau"); } });
  await c.paiement(1, [{ mode: "especes", montant: 3000 }]);
  assert.equal(c.etat.file.length, 1);
  for (const action of Object.keys(INTERDIT_HORS_LIGNE)) {
    const r = await c.demander(action, "/api/x");
    assert.equal(r.ok, false, action);
    assert.equal(r.horsLigne, true, action);
    assert.ok(/OFF-2/.test(r.raison), action);
  }
  assert.equal(c.etat.file.length, 1); // rien n'a été ajouté par les refus
  // lecture seule hors ligne : refusée aussi (pas de donnée fraîche)
  const lecture = await c.catalogue();
  assert.equal(lecture.ok, false);
});

test("INT-5 resynchronisation : rejoue la file dans l'ordre et remonte les alertes (OFF-3)", async () => {
  let prises = 0;
  const c = creerClient({
    fetchImpl: async (u, o) => {
      if (o.method === "POST" && u.endsWith("/api/commandes")) {
        prises++;
        if (prises === 1) throw new Error("réseau"); // 1re passe : échec → file
        return rep({ alertes: ["Plafond ardoise dépassé : Koffi"] });
      }
      if (o.method === "POST" && u.endsWith("/paiement")) return rep({});
      return rep({ produits: [] });
    }
  });
  await c.creerCommande([{ id: 1 }]);
  await c.paiement(7, [{ mode: "especes", montant: 1000 }]);
  assert.equal(c.etat.file.length, 2);
  const evenements = [];
  c.abonner((e) => evenements.push(e));
  const r = await c.resynchroniser();
  assert.equal(c.etat.enLigne, true);
  assert.equal(r.rejouees, 2);
  assert.equal(c.etat.file.length, 0);
  assert.deepEqual(r.alertes, ["Plafond ardoise dépassé : Koffi"]);
  assert.ok(evenements.some((e) => e.type === "resynchro"));
});

test("INT-6 le PC rejette encore → la file reste intacte (réessai suivant)", async () => {
  const c = creerClient({
    fetchImpl: async (u, o) => (o.method === "POST" ? rep({ raison: "Toujours hors serveur" }, 503) : rep({}))
  });
  c.basculerLigne(false);
  await c.creerCommande([{ id: 1 }]);
  assert.equal(c.etat.file.length, 1);
  const r = await c.resynchroniser();
  assert.equal(r.rejouees, 0);
  assert.equal(c.etat.file.length, 1); // conservée
});

test("INT-7 chaque action du catalogue API a sa classe hors ligne définie", () => {
  const attendues = ["prise_commande", "modification_commande", "encaissement_especes",
                     "encaissement_mobile", "vente_ardoise"];
  assert.deepEqual(FILE_HORS_LIGNE, attendues);
});
