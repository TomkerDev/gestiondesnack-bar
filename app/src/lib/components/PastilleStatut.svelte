<!-- I1 · Pastille de statut : point coloré + texte (JAMAIS la couleur seule —
     le libellé est toujours rendu). Statuts cuisine CUI-3.
     Neutre = envoyé · alerte = en préparation · succès = prêt · danger = annulé.
     Le mapping tolère les accents et les variantes (« prêt » / « pret »). -->
<script>
  export let statut = "";

  // Cartographie statut → ton. Aucune couleur en dur : uniquement des jetons.
  function tonDe(s) {
    const v = String(s || "").toLowerCase().trim();
    if (v.startsWith("prêt") || v.startsWith("pret")) return "succes";
    if (v.startsWith("prépar") || v.startsWith("prepar")) return "alerte";
    if (v.startsWith("annul")) return "danger";
    return "neutre"; // envoyé, en attente, non connu
  }
  $: ton = tonDe(statut);
</script>

<span class="pastille zone-tactile" class:pastille--succes={ton === "succes"}
      class:pastille--alerte={ton === "alerte"} class:pastille--danger={ton === "danger"}
      data-statut={statut} data-ton={ton}>
  <span class="pastille-point" aria-hidden="true"></span>
  <span class="pastille-libelle">{statut}</span>
</span>

<style>
  .pastille {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
    min-height: 28px;
    padding: var(--sp-1) var(--sp-3);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-pastille);
    background: var(--surface-haute);
    color: var(--texte);
    font-size: var(--t-sm);
    font-weight: 600;
    white-space: nowrap;
    max-width: 100%;
  }

  /* point coloré : la couleur porte l'état, le texte le nomme */
  .pastille-point {
    width: 8px;
    height: 8px;
    flex: none;
    border-radius: var(--rayon-pastille);
    background: var(--neutre);
  }

  .pastille-libelle { overflow: hidden; text-overflow: ellipsis; }

  .pastille--succes { border-color: color-mix(in srgb, var(--succes) 55%, transparent); }
  .pastille--succes .pastille-point { background: var(--succes); }

  .pastille--alerte { border-color: color-mix(in srgb, var(--alerte) 55%, transparent); }
  .pastille--alerte .pastille-point { background: var(--alerte); }

  .pastille--danger { border-color: color-mix(in srgb, var(--danger) 55%, transparent); }
  .pastille--danger .pastille-point { background: var(--danger); }
</style>

