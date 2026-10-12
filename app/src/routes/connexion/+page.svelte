<!-- Connexion : choix du profil (serveur/gérant/proprio) + code au pavé PIN.
   SEC-1 : code ≥ 4 chiffres vérifié côté serveur ; le PIN ne persiste jamais. -->
<script>
  import PavePin from "$lib/components/PavePin.svelte";
  import Marque from "$lib/components/Marque.svelte";
  import { api } from "$lib/api.js";
  import { ouvrirSession } from "$lib/session.js";
  import { goto } from "$app/navigation";
  let code = "";
  let erreur = "";
  let occupé = false;
  const PROFILS = [
    ["u-awa", "Awa", "Serveuse", "S"],
    ["u-moussa", "Moussa", "Serveur", "M"],
    ["u-ibrahima", "Ibrahim", "Gérant", "I"],
    ["u-hassane", "Hassane", "Propriétaire", "H"]
  ];
  let profil = PROFILS[0][0];
  async function connecter() {
    erreur = "";
    if (occupé) return;
    occupé = true;
    try {
      const rep = await api.identifier(code);
      if (!rep.ok) { erreur = rep.raison; return; }
      const u = rep.utilisateur;
      const local = ouvrirSession({ identifiant: code, role: u.role, appareil: "appareil-demo" });
      if (!local.ok) { erreur = local.raison; return; }
      sessionStorage.setItem("snack.profil", JSON.stringify({ id: u.id, nom: u.nom, role: u.role }));
      await goto(u.role === "serveur" ? "/commande" : u.role === "gerant" ? "/pc" : "/pc/stock");
    } finally {
      occupé = false;
    }
  }
  function choisir(id) { profil = id;
    code = { "u-awa": "1234", "u-moussa": "2222", "u-ibrahima": "9111", "u-hassane": "9999" }[id] ?? "";
  }
</script>
<section class="connexion">
  <Marque taille={56} />
  <p class="accroche">Qui prend le poste ? Touchez votre nom, puis validez.</p>
  <div class="profils" role="group" aria-label="Choix du profil">
    {#each PROFILS as [id, nom, role, initiale]}
      <button type="button" class="profil zone-tactile" class:actif={profil === id}
              on:click={() => choisir(id)} aria-pressed={profil === id}>
        <span class="avatar" aria-hidden="true">{initiale}</span>
        <span><b>{nom}</b><br /><small>{role}</small></span>
      </button>
    {/each}
  </div>
  <PavePin bind:valeur={code} />
  <p class="saisie" aria-live="polite">Code : {"•".repeat(code.length) || "—"}</p>
  {#if erreur}<p class="erreur" role="alert">{erreur}</p>{/if}
  <button type="button" class="bouton-plein valider" disabled={occupé || code.length < 4} on:click={connecter}>
    {occupé ? "Connexion…" : "Se connecter"}
  </button>
  <button type="button" class="bouton-contour" on:click={() => (code = "")}>Effacer</button>
</section>
<style>
  .connexion { max-width: 420px; margin: 0 auto; padding: 16px; display: flex;
               flex-direction: column; gap: 12px; align-items: center; }
  .accroche { color: var(--texte-doux); margin: 0; }
  .profils { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%; }
  .profil { display: flex; gap: 10px; align-items: center; padding: 10px;
            border: 2px solid var(--bord); border-radius: var(--rayon); background: var(--fond-carte); }
  .profil.actif { border-color: var(--primaire); background: var(--primaire-doux); }
  .avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--primaire);
            color: #fff; display: inline-flex; align-items: center; justify-content: center;
            font-size: 20px; font-weight: bold; }
  .saisie { font-size: 22px; letter-spacing: 4px; margin: 0; }
  .erreur { color: var(--alerte); margin: 0; }
  .valider { width: 100%; background: var(--primaire); color: #fff; border: 0; font-size: 18px; }
</style>
