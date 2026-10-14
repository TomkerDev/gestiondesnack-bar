/* Captures Playwright « avant/après » — références de régression visuelle.
   4 écrans × 2 thèmes × 3 formats = 24 images par passe.
   Usage : node scripts/captures.mjs avant   |   node scripts/captures.mjs apres
   Aucun réseau externe : tout est servi en local (Vite 5173 + proxy /api 8080). */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RACINE = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const ETIQUETTE = process.argv[2] === "apres" ? "apres" : "avant";
const SORTIE = path.join(RACINE, "captures", ETIQUETTE);
const BASE = "http://127.0.0.1:5173";

const FORMATS = [
  { cle: "390x844", width: 390, height: 844 },
  { cle: "820x1180", width: 820, height: 1180 },
  { cle: "1280x800", width: 1280, height: 800 }
];
const THEMES = ["sombre", "clair"];
const ECRANS = [
  { cle: "galerie", chemin: "/galerie" },
  { cle: "commande", chemin: "/commande" },
  { cle: "paiement", chemin: "/paiement" },
  { cle: "cuisine", chemin: "/cuisine" }
];

// Profil injecté avant chaque chargement : la garde de routes exige une session
// (sinon /galerie redirige vers /connexion). Rôle serveur = portée maximale.
const PROFIL = JSON.stringify({ id: "u-awa", nom: "Awa", role: "serveur" });

const nomsEcrans = {
  "/galerie": "Galerie",
  "/commande": "Prise de commande",
  "/paiement": "Paiement",
  "/cuisine": "Cuisine"
};

async function capturer() {
  await mkdir(SORTIE, { recursive: true });
  const navigateur = await chromium.launch();
  let total = 0;

  for (const format of FORMATS) {
    const contexte = await navigateur.newContext({
      viewport: { width: format.width, height: format.height },
      locale: "fr-FR",
      deviceScaleFactor: 1
    });

    for (const theme of THEMES) {
      for (const ecran of ECRANS) {
        const page = await contexte.newPage();
        // Thème posé avant le premier rendu + session restaurée.
        await page.addInitScript(
          ([th, profil]) => {
            document.documentElement.setAttribute("data-theme", th);
            try { sessionStorage.setItem("snack.profil", profil); } catch { /* stockage absent */ }
          },
          [theme, PROFIL]
        );
        await page.goto(BASE + ecran.chemin, { waitUntil: "networkidle" });
        // La Galerie porte son propre data-theme : on aligne le basculeur d'état.
        const bascule = page.locator('button:has-text("Basculer")');
        if (ecran.chemin === "/galerie" && (await bascule.count()) > 0) {
          const etat = await bascule.first().innerText();
          const veutSombre = theme === "sombre";
          const estSombre = etat.includes("sombre");
          if (veutSombre !== estSombre) await bascule.first().click();
        }
        await page.waitForTimeout(350); // transitions 120-180 ms + chargement catalogue
        const fichier = path.join(
          SORTIE,
          `${ecran.cle}--${theme}--${format.cle}.png`
        );
        await page.screenshot({ path: fichier, fullPage: true });
        total += 1;
        const titre = await page.title();
        console.log(
          `  ${ETIQUETTE}  ${ecran.cle}  ${theme}  ${format.cle}  (${titre || nomsEcrans[ecran.chemin]})`
        );
        await page.close();
      }
    }
    await contexte.close();
  }

  await navigateur.close();
  console.log(`\n${total} captures écrites dans ${SORTIE}`);
}

capturer().catch((err) => { console.error(err); process.exit(1); });
