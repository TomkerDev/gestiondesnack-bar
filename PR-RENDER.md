# Refonte visuelle — Snack-bar Apis

## 1. Diagnostic (écrit avant toute écriture de CSS)

### Symptômes constatés sur la Galerie
Police **serif** par défaut du navigateur, boutons **natifs**, pastilles de statut collées
(« envoyéen préparationprêt »), tuile produit où nom/prix/quantité se suivent sur une ligne
(« Bière 65cl1 500 2 »), touches du pavé PIN **carrées**.

### Cause racine — la feuille globale **est** chargée, mais elle est vide de style

`src/routes/+layout.svelte` importe bien `$lib/theme.css` (vérifié : test `INT_layout_theme` vert).
Le problème n'est donc **pas** un import manquant. Il est **triple** :

**(a) `theme.css` ne contenait que des variables + 7 règles utilitaires, sans typographie.**
Aucune `font-family` n'était déclarée **nulle part dans le projet** (`grep font-family` sur
`src/**/*.svelte,*.css` → **0 occurrence**). D'où la police serif par défaut du navigateur.
Aucun `box-sizing`, aucune remise à zéro des marges de `h1/h2/section`, aucune règle `button`
générique : le navigateur rend donc ses éléments natifs.

**(b) Les « styles » de `theme.css` ne posaient que des dimensions, jamais de mise en page.**

```css
.tuile-produit  { min-height: 88px; min-width: 48px; border-radius: 12px; }
.pastille       { min-height: 48px; min-width: 48px; border-radius: 999px; }
.pave-pin button{ min-height: 64px; min-width: 64px; font-size: 24px; }
```

Or `TuileProduit` rend trois `<span>` **inline**, sans `display:flex` ni `flex-direction:column`
→ ils défilent sur une même ligne (« Bière 65cl1 500 2 »). Idem pour `PastilleStatut` : un `<span>`
sans `display:inline-flex`, sans `gap` ni `margin` → « envoyéen préparationprêt ».
`PavePin` n'avait **ni `display:grid` ni `border-radius`** sur ses touches → grille absente,
touches carrées. `Bouton`, `TuileProduit`, `LigneCommande`, `BandeauConnexion`, `PavePin`,
`SelecteurMotif`, `FenetreR1` étaient **dépourvus de bloc `<style>`** (7 sur 9) et s'appuyaient
uniquement sur ces classes dimensionnelles incomplètes.

**(c) Variables CSS jamais définies + sélecteurs de statut qui ne matchent jamais.**

- `--bordure` était **utilisée** dans `+layout.svelte` et `+page.svelte` mais **jamais définie**
  (`theme.css` définissait `--bord`) → retombée silencieuse sur le fallback codé en dur `var(--bordure, #ccc)`.
- `PastilleStatut` ciblait `[data-statut="pret"]` et `[data-statut="alerte"]`, alors que les statuts
  réellement émis par `lib/cuisine.js` sont `"prêt"` et `"en préparation"` → **sélecteurs morts** :
  aucune pastille n'était colorée.
- Couleurs en dur résiduelles : `color: #fff` (×4), `#ccc` (×2), `#fff7ed`/`rgba()` dans `Marque`,
  `theme-color: #c2410c` dans le layout et `#1a1a2e` dans `app.html` (violet incohérent avec l'orange Apis).
- Le thème **clair** était porté par `:root` et le sombre par `[data-theme="sombre"]` : impossible de
  forcer le clair depuis un conteneur, et la Galerie pilotait un `<div data-theme>` orphelin.

### Ce qui n'a **pas** été touché
Logique métier (`src/lib/*.js`), routes, contrat d'API, tests de logique : **inchangés** (§6).


---

## 2. Jetons de design

`src/lib/theme.css` porte **toutes** les variables ; `src/lib/base.css` porte la réinitialisation et
la typographie. Tous deux importés **une seule fois** dans le layout racine.

| Rôle | Sombre (défaut) | Clair |
|---|---|---|
| fond | `#14110F` | `#FAF6F1` |
| surface | `#1E1A17` | `#FFFFFF` |
| surface haute | `#27221E` | `#F1EAE2` |
| bordure | `#3A332D` | `#E3D9CE` |
| texte | `#F6F1EA` | `#1F1A16` |
| texte secondaire | `#A89F94` | `#6B6259` |
| accent | `#F26B21` | `#C2410C` |
| succès | `#34C77B` | `#15803D` |
| alerte | `#F5B73B` | `#B45309` |
| danger | `#EF5B5B` | `#B91C1C` |
| texte sur accent | `#1A0E06` | `#FFFFFF` |

Rayons 10/14/16/999 px (champ/bouton/carte/pastille). Espacement sur base 4 px. Bordure 1 px en
sombre, ombre légère **uniquement** en clair. Typographie **Inter Variable embarquée**
(`@fontsource-variable/inter` — aucun CDN, réseau local autonome). Échelle 12/13/15/17/22/28 px,
chiffres tabulaires + espace fine insécable sur tout montant. Mouvement 120–180 ms avec
`prefers-reduced-motion`. Focus visible 2 px accent avec décalage.

Les anciens noms (`--fond`, `--texte`, `--primaire`, `--succes`, `--alerte`, `--bord`, `--fond-carte`,
`--texte-doux`, `--tactile`, `--rayon`, `--pad`) sont **conservés en alias** : les tests statiques I1
et les écrans continuent de les résoudre sans réécriture.

### Contrastes AA (paires calculées)
Sombre : texte/fond **16,7** · secondaire/fond **7,2** · accent/fond **6,2** · texte-sur-accent/accent **6,2**
· succès **8,6** · alerte **10,5** · danger **5,7** · texte/surface **15,4** · accent/surface **5,7**.
Clair : texte/fond **16,0** · secondaire/fond **5,6** · accent/fond **4,8** · blanc/accent **5,2**
· succès/blanc **5,0** · alerte/blanc **5,0** · danger/blanc **6,5**. Toutes ≥ 4,5:1.
Aucun statut n'est porté par la seule couleur : chaque pastille couple un point coloré **et** son libellé.

---

## 3. Composants refaits — aucun hex ni police en dur (contrôlé par `tests/styles.test.js`)

- **Bouton** — plein / contour / danger / désactivé, 48 px, état de chargement.
- **Tuile produit** — nom en gras, prix en secondaire **sous** le nom, pastille de quantité ronde en
  haut à droite, sélection (bordure accent + fond accent 16 %), mini 76 px.
- **Pastille de statut** — point coloré + texte : envoyé (neutre), en préparation (alerte), prêt
  (succès), annulé (danger).
- **Bandeau de connexion** — « En ligne » en pastille verte discrète ; perte en bandeau orange calme.
- **Clavier PIN** — 3 colonnes, touches arrondies ≥ 56 px, indicateur de 4 points.
- **Navigation** — barre supérieure à contrôle segmenté (large) ; barre inférieure icône + libellé
  (téléphone). Menu dépendant du rôle ; Galerie réservée au mode développement.
- **Champ de formulaire** — 48 px, libellé au-dessus, erreur sous le champ.
- **Fenêtre R1** — feuille montante (téléphone) / fenêtre centrée (large).

---

## 4. Galerie · 5. Écrans re-stylés

Galerie : chaque composant dans chaque état, sombre **et** clair, bascule fonctionnelle posant
`data-theme` sur `<html>`. Écrans (Prise de commande, Mes commandes, Détail, Paiement, Cuisine,
Ma caisse, PC caisse, Stock & prix, Connexion, Accueil) re-stylés : **logique et textes inchangés**.

---

## 6. Hors périmètre — respecté

Aucun fichier de `src/lib/*.js` modifié ; routes, contrat d'API et tests de logique intacts.

## 7. Critères d'acceptation

| # | Critère | Vérification |
|---|---|---|
| 1 | Aucune hexa ni police en dur dans un composant | `node --test tests/styles.test.js` |
| 2 | Captures avant/après (Galerie + 3 écrans × 2 thèmes × 3 formats) | `captures/avant` + `captures/apres` |
| 3 | Aucune violation axe-core | `npx playwright test e2e/axe.spec.js` |
| 4 | Trafic hors localhost bloqué, pages complètes | `npx playwright test e2e/reseau-local.spec.js` |
| 5 | `npm test` + `npm run build` verts, aucun module métier touché | `npm test` · `npm run build` · `git diff --stat` |
