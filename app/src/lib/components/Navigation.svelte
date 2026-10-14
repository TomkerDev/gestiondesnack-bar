<!-- I1 · Navigation tactile : barre supérieure à contrôle segmenté sur écran large,
     barre inférieure icône + libellé sur téléphone. Le menu est FILTRÉ PAR RÔLE
     en amont (lib/droits.js → liensPour) : un serveur ne voit ni « PC caisse »
     ni « Stock & prix ». Aucune couleur en dur : jetons uniquement. -->
<script>
  import { Store, ClipboardList, ChefHat, Wallet, Monitor, Boxes, LayoutGrid } from "@lucide/svelte";

  export let liens = [];        // [[href, libellé], …] déjà filtrés par rôle
  export let chemin = "";       // chemin courant pour l'onglet actif

  // Icône par destination — mappe sur les 7 écrans métier + Galerie.
  const ICONES = {
    "/commande": Store,
    "/commandes": ClipboardList,
    "/cuisine": ChefHat,
    "/paiement": Wallet,
    "/ma-caisse": Wallet,
    "/pc": Monitor,
    "/pc/stock": Boxes,
    "/galerie": LayoutGrid
  };

  // L'onglet actif : le plus long préfixe correspondant (évite que /pc
  // n'éclaire aussi /pc/stock).
  function actif(href) {
    if (href === "/") return chemin === "/";
    return chemin === href || chemin.startsWith(href + "/");
  }
</script>

<!-- barre supérieure : écran large -->
<nav class="nav-haut zone-tactile" aria-label="Application">
  <ul class="nav-segmentes">
    {#each liens as [href, lib]}
      <li>
        <a class="nav-segmente zone-tactile" class:nav-segmente--actif={actif(href)}
           {href} aria-current={actif(href) ? "page" : undefined}>
          <svelte:component this={ICONES[href] ?? LayoutGrid} size={18} strokeWidth={2} aria-hidden="true" />
          <span>{lib}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>

<!-- barre inférieure : téléphone -->
<nav class="nav-bas" aria-label="Application (mobile)">
  <ul class="nav-bas-liste">
    {#each liens as [href, lib]}
      <li class="nav-bas-item">
        <a class="nav-bas-lien zone-tactile" class:nav-bas-lien--actif={actif(href)}
           {href} aria-current={actif(href) ? "page" : undefined}>
          <svelte:component this={ICONES[href] ?? LayoutGrid} size={22} strokeWidth={2} aria-hidden="true" />
          <span class="nav-bas-libelle">{lib}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>

<style>
  /* ---------- barre supérieure (tablette / PC) ---------- */
  .nav-haut { display: none; }

  .nav-segmentes {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    list-style: none;
    margin: 0;
    padding: var(--sp-1);
    background: var(--surface-haute);
    border: var(--bordure-large) solid var(--bordure);
    border-radius: var(--rayon-bouton);
    overflow-x: auto;
  }

  /* contrôle segmenté : l'onglet actif est rempli en accent */
  .nav-segmente {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
    min-height: 40px;
    padding: 0 var(--sp-3);
    border-radius: calc(var(--rayon-bouton) - 4px);
    color: var(--texte-secondaire);
    font-size: var(--t-sm);
    font-weight: 600;
    text-decoration: none;
    white-space: nowrap;
    transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
  }
  .nav-segmente:hover { color: var(--texte); background: var(--surface); }
  .nav-segmente--actif {
    background: var(--accent);
    color: var(--sur-accent);
  }
  .nav-segmente--actif:hover { background: var(--accent); color: var(--sur-accent); }

  /* ---------- barre inférieure (téléphone) ---------- */
  .nav-bas {
    position: sticky;
    bottom: 0;
    z-index: 20;
    background: var(--surface);
    border-top: var(--bordure-large) solid var(--bordure);
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .nav-bas-liste {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    overflow-x: auto;
  }

  .nav-bas-item { flex: 1 0 auto; }

  .nav-bas-lien {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--sp-1);
    min-width: 64px;
    min-height: 56px;
    padding: var(--sp-2) var(--sp-1);
    color: var(--texte-secondaire);
    font-size: var(--t-xs);
    font-weight: 600;
    text-decoration: none;
    border-top: 3px solid transparent;
    transition: color var(--dur) var(--ease), border-color var(--dur) var(--ease);
  }
  .nav-bas-lien--actif {
    color: var(--accent);
    border-top-color: var(--accent);
  }

  .nav-bas-libelle {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* ---------- bascule ---------- */
  @media (min-width: 721px) {
    .nav-haut { display: block; }
    .nav-bas { display: none; }
  }
</style>
