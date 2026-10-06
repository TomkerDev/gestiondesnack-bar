# Prompts de développement : application de gestion de snack-bar

Ces prompts s'utilisent avec la spécification `specification-snack-bar.md` (version 1.1). Ils sont écrits pour fonctionner dans n'importe quel outil d'IA (Claude Code, Claude.ai, autre). Joins toujours la spécification.

## Comment s'en servir

1. Une session par prompt. Commence chaque session par le **prompt maître** (section 1), puis colle le prompt de la tâche.
2. Pour les interfaces, ajoute aussi le **bloc UI** (section 3) après le prompt maître.
3. Chaque prompt demande à l'IA de lister ses hypothèses et de poser au plus 5 questions avant de coder. Réponds-y : c'est là que les erreurs coûteuses se règlent.
4. Termine chaque session avec le **prompt de revue** (section 4), qui vérifie le résultat exigence par exigence.

Ordre conseillé :

| Étape | Prompts | Correspond à la phase |
|---|---|---|
| Avant de coder | M7 (relecture critique de la spécification) | Cadrage |
| Noyau métier | M1, puis M2 à M6 | Phase 1 |
| Caisse sur le PC | I1, I2, I3, I4 | Phase 2 |
| Cuisine, caisse serveur | I5, I6 | Phases 4 et 6 |
| Pilotage gérant | I7, I8 | Phases 5 et 6 |

---

## 1. Prompt maître (à coller au début de chaque session)

```
Tu es un ingénieur senior qui m'aide à construire une application de gestion de snack-bar. J'apprends en construisant : explique brièvement tes choix importants.

CONTEXTE
- Établissement : snack-bar (boissons alcoolisées ou non, whisky vendu à la bouteille, cuisine associée). Plusieurs serveurs sur téléphones ou tablettes, un PC caisse, un écran cuisine (tablette fixe).
- Stack : Tauri 2 (Rust) sur le PC caisse ; SQLite via rusqlite en mode WAL ; serveur local axum (HTTP et WebSocket) ; interface Svelte 5 (runes) en TypeScript ; pages web installables (PWA) pour les serveurs et la cuisine, avec fonctionnement hors ligne pour les serveurs.
- Source de vérité : le document specification-snack-bar.md (joint). Chaque exigence a un identifiant (CMD-1, STK-3, R1...).

RÈGLES DE TRAVAIL
1. La spécification prime. Ne crée aucune règle métier qui n'y figure pas. Si un cas n'est pas couvert, signale-le et propose des options au lieu de choisir en silence.
2. Cite les identifiants d'exigences dans le code (commentaires courts) et dans les noms de tests.
3. Écris les tests avec le code. Chaque exigence a au moins un test.
4. Montants : entiers dans la plus petite unité de la devise, jamais de flottants.
5. Identifiants de commande générés localement, uniques sans coordination : le hors ligne est prévu dès maintenant.
6. Les mouvements de stock sont additifs et jamais modifiés. Une commande payée est immuable : une correction est un enregistrement distinct (R4).
7. Interface en français, sobre : phrases courtes, verbe d'action, sans point final sur les libellés.
8. Avant de coder : liste tes hypothèses et pose au plus 5 questions. Après : résume ce qui est fait, ce qui reste et les risques.
```

---

## 2. Prompts métier

### M7. Relecture critique de la spécification (à faire en premier)

```
Relis specification-snack-bar.md comme un auditeur hostile. Ne produis aucun code.

Cherche :
1. Les contradictions entre exigences (cite les deux identifiants).
2. Les cas non couverts : états impossibles à atteindre, actions sans règle, transitions manquantes.
3. Les conditions de course : deux appareils agissent en même temps (dernière bouteille, annulation contre début de préparation, transfert de commande).
4. Les scénarios de fraude ou d'erreur d'un serveur, d'un gérant, d'un propriétaire.
5. Les ambiguïtés : toute phrase que deux développeurs implémenteraient différemment.
6. Les conséquences du mode hors ligne sur chaque règle.

Livrable : un tableau (identifiant, problème, gravité haute/moyenne/faible, correction proposée). Termine par les 5 questions qu'il faut trancher avant de coder.
```

### M1. Schéma de données

```
OBJECTIF : concevoir le schéma SQLite complet.

À partir des sections 2 à 5 de la spécification, produis :
1. Les migrations SQL (tables, contraintes, index) pour : utilisateurs et rôles ; produits (indicateur alcool, suivi de stock, prix de vente, prix d'achat ou coût estimé pour un plat) ; clients et ardoises ; journées d'exploitation ; commandes ; lignes (prix et coût figés, remise, statut cuisine) ; règlements (mode, référence mobile money, opérateur, monnaie rendue, pourboire) ; mouvements de stock ; entrées de stock (à valider ou validées) ; caisses serveur et clôtures ; sorties de caisse ; corrections (R4) ; journal d'audit.
2. Un diagramme entité-relation en Mermaid.
3. Un tableau « exigence -> table et colonne » prouvant que chaque exigence est stockable.

CONTRAINTES
- Identifiants uniques sans coordination (UUID ou préfixe d'appareil et compteur).
- Aucune suppression physique.
- Le journal d'audit n'accepte que des insertions (triggers refusant update et delete).
- Pas de contrainte stock >= 0 (STK-3).
- Les prix et coûts de chaque ligne sont copiés au moment de l'ajout (PRX-3).

CRITÈRES D'ACCEPTATION
- Le schéma s'applique sur une base vide sans erreur.
- Un script de test insère un scénario complet : commande, paiement mixte, ardoise, correction.
- Tu listes les cas que le schéma ne sait pas représenter.
```

### M2. Commandes et paiement

```
OBJECTIF : écrire le module métier « commande et paiement » en Rust pur, sans accès disque ni réseau (fonctions et types seulement), pour qu'il soit testable seul.

EXIGENCES À COUVRIR : CMD-1 à CMD-6, PAI-1 à PAI-3, PAI-5, PAI-6, R4.

À FAIRE
- Modéliser la commande comme une machine à états (ouverte, payée, annulée) avec des transitions typées et des erreurs explicites.
- Fonctions : ouvrir, ajouter ou retirer une ligne, transférer des lignes, convertir comptoir -> table, transférer à un autre serveur, régler.
- Règle de paiement : la somme des règlements égale le total net ; espèces et mobile money combinables ; l'ardoise est exclusive et couvre la totalité ; le pourboire est hors total et hors chiffre d'affaires.
- Une commande payée refuse toute modification directe ; une correction est une opération distincte qui référence l'original.

CRITÈRES D'ACCEPTATION
- Tests nommés avec les identifiants d'exigences.
- Cas limites testés : règlement trop faible, trop élevé, mode mixte avec ardoise (refusé), commande payée modifiée (refusée), retrait d'une ligne inexistante.
- Aucun f32 ni f64 dans le module.
```

### M3. Ardoise

```
OBJECTIF : module « ardoise » en Rust pur.

EXIGENCES : ARD-1 à ARD-6, PAI-2 (ardoise exclusive), D2 et D5 de la spécification.

À FAIRE
- Fonction de décision : (client, solde, plafond, montant) -> accepté, refusé, ou refusé avec déblocage possible par le gérant.
- Un déblocage est ponctuel et ne modifie pas le plafond ; il exige une autorisation R1.
- Remboursement d'ardoise : encaissement distinct, attribué au serveur.
- Mode hors ligne : la décision s'appuie sur un instantané du solde ; à la resynchronisation, une fonction recalcule les soldes et produit une alerte de dépassement.

CRITÈRES D'ACCEPTATION
- Tests : montant exactement au plafond (accepté), un de plus (refusé), déblocage, deux ventes hors ligne sur le même client dépassant ensemble le plafond (alerte à la synchronisation).
- La vente sur ardoise ne compte pas dans les espèces attendues mais compte dans le chiffre d'affaires.
```

### M4. Stock

```
OBJECTIF : module « stock » en Rust pur.

EXIGENCES : STK-1 à STK-6, PRX-3, CUI-4 (pertes après préparation).

À FAIRE
- Le stock courant se calcule comme la somme des mouvements ; aucune écriture directe de quantité.
- Vente à stock nul ou négatif : autorisée, avec alerte ; liste des produits négatifs.
- Entrée de stock : quantités seulement, comptée dès la saisie, état « à valider » puis « validée » ; un rejet crée le mouvement inverse.
- Inventaire quotidien des boissons : écart = théorique - compté ; chaque écart crée un mouvement de correction avec motif.
- Pertes : casses déclarées, annulations après préparation, offerts, écarts d'inventaire négatifs ; calcul en quantités, valorisation au coût réservée au rôle propriétaire (R3).

CRITÈRES D'ACCEPTATION
- Test de commutativité : appliquer les mêmes mouvements dans n'importe quel ordre donne le même stock (condition du mode hors ligne).
- Tests : dernière bouteille vendue deux fois, entrée rejetée, inventaire avec manque et excédent.
```

### M5. Caisse et journée d'exploitation

```
OBJECTIF : module « caisse et journée » en Rust pur.

EXIGENCES : CAI-1 à CAI-6, PAI-4, R2, R5, D14.

À FAIRE
- Machine à états de la journée (ouverte, en clôture, close) ; une journée close n'est jamais rouverte (R5).
- Formule : espèces attendues = fond de caisse + espèces encaissées (monnaie rendue déduite, pourboires en espèces inclus) + remboursements d'ardoise en espèces - sorties de caisse validées.
- Clôture d'une caisse serveur : écart non nul (manque ou excédent) -> justification obligatoire (motif et commentaire) avant clôture ; tolérance configurable, zéro par défaut.
- Forcer une clôture : exige R1 et un motif consigné.
- La journée ne se clôture que si toutes les caisses sont closes.
- Une correction sur une journée passée est comptabilisée dans la journée en cours (R5).

CRITÈRES D'ACCEPTATION
- Tests avec des scénarios chiffrés complets (fond, ventes, rendu de monnaie, ardoise, pourboire reversé, sortie de caisse).
- Test : correction d'une commande de la veille.
```

### M6. Autorisations, identification et audit

```
OBJECTIF : module « sécurité » : codes PIN, autorisation gérant (R1) et journal d'audit.

EXIGENCES : R1, R3, SEC-1 à SEC-3, matrice des droits (section 3).

À FAIRE
- PIN : hachage avec sel (argon2id), minimum 4 chiffres, blocage temporaire après 5 échecs, verrouillage de session après 2 minutes d'inactivité.
- Hors ligne : seules des empreintes salées sont stockées sur les appareils.
- Autorisation R1 : une fonction demande une autorisation pour un acte précis (type, commande, motif) et renvoie un jeton à usage unique lié à cet acte ; le gérant ressaisit son PIN à chaque fois.
- Contrôle des droits : une fonction unique (rôle, action) -> permis ou refusé, couvrant toute la matrice de la section 3.
- Journal d'audit en ajout seul : qui, quoi, quand, motif, commande.

CRITÈRES D'ACCEPTATION
- Tests : chaque ligne de la matrice des droits ; jeton réutilisé (refusé) ; jeton utilisé pour un autre acte (refusé) ; sixième échec de PIN.
- Aucun PIN ni empreinte n'apparaît dans les journaux de debug.
```

---

## 3. Prompts interfaces

### Bloc UI (à coller après le prompt maître pour toute session d'interface)

```
CONTRAINTES COMMUNES À TOUTES LES INTERFACES
- Svelte 5 et TypeScript. Un seul code pour téléphone et tablette : moins de 640 px de large, une colonne avec une barre d'action fixe en bas ; 640 px et plus, deux volets.
- Thème sombre par défaut, contrastes élevés, zones tactiles d'au moins 48 px, pas de glisser-déposer obligatoire, actions principales dans la zone du pouce.
- Une seule action principale par écran (bouton plein) ; les autres en contour.
- Pas de confirmation, sauf pour les actions irréversibles ; sinon un « Annuler » discret juste après l'action.
- L'état de connexion est toujours visible : pastille « En ligne », ou bandeau orange calme « Hors ligne ». Le serveur connecté et la table en cours restent affichés.
- Rôles : n'affiche jamais ce que le rôle ne permet pas (les coûts sont invisibles hors propriétaire, R3). Toute action soumise à R1 ouvre la même fenêtre d'autorisation gérant.
- Libellés en français, minuscules sauf initiale, verbe d'action, sans point final. Erreur : ce qui s'est passé, puis quoi faire. Jamais de message technique.
- Accessibilité : un statut est toujours couleur et texte ; libellés pour lecteurs d'écran ; navigation au clavier sur le PC.
- Les données passent par une couche d'accès unique et typée, pour que la même interface marche via les commandes Tauri (PC) ou via HTTP (appareils).
- Chaque écran gère quatre états : chargement, vide, hors ligne, erreur.
```

### I1. Fondations visuelles et composants

```
OBJECTIF : créer le socle de l'interface avant tout écran.

À FAIRE
- Variables de thème (couleurs, espacements, rayons, tailles de texte) en mode sombre et clair.
- Composants : bouton plein et bouton contour ; tuile produit avec pastille de quantité ; pastille de statut (couleur et texte) ; bandeau de connexion ; clavier numérique PIN ; fenêtre d'autorisation gérant (R1) avec PIN et choix du motif dans une liste ; sélecteur de motif ; ligne de commande.
- Une page « galerie » qui montre chaque composant dans chaque état.

CRITÈRES D'ACCEPTATION
- Tous les composants respectent 48 px minimum de zone tactile.
- Tests de composants avec testing-library.
- Aucun composant ne contient de logique métier.
```

### I2. Prise de commande

```
OBJECTIF : écran de prise de commande, téléphone et tablette.

EXIGENCES : CMD-1, CMD-2, CMD-6, CUI-1, STK-3, PRX-3.

DESCRIPTION
- Catalogue de moins de 30 produits : une grille unique, filtres de catégorie en haut (Tout, Bières, Softs, Alcools, Plats). Pas de recherche ni de favoris.
- Un appui sur une tuile ajoute une unité ; chaque appui augmente la quantité ; la pastille de quantité s'affiche sur la tuile. Pour retirer, on touche la pastille ou la ligne, avec un « Annuler » discret ensuite.
- Téléphone : barre fixe en bas (nombre d'articles, total, « Envoyer en cuisine »). Tablette : grille à gauche, commande en cours à droite avec « Envoyer » et « Payer ».
- Stock nul : la vente passe, sans blocage ; l'alerte part vers le gérant, pas vers le serveur.
- Hors ligne : l'écran fonctionne comme en ligne ; le bandeau indique le mode.

CRITÈRES D'ACCEPTATION
- Ajouter un produit coûte exactement un appui.
- Les prix et coûts de la ligne sont figés à l'ajout.
- Tests : trois produits ajoutés, un retiré puis annulé, envoi vers la cuisine.
```

### I3. Mes commandes et détail d'une commande

```
OBJECTIF : écran d'accueil du serveur et détail d'une commande.

EXIGENCES : CMD-2, CMD-3, CMD-4, CMD-5, CMD-7, CUI-4, OFF-2.

DESCRIPTION
- Liste des commandes ouvertes du serveur, groupées par table, avec total et état cuisine. Bouton « Nouvelle commande » (choix table ou comptoir) comme action principale.
- Détail : lignes, statut cuisine de chaque plat, actions : annuler un plat (le serveur tant qu'il est « envoyé », sinon demande d'autorisation gérant), retirer une boisson, transférer des lignes, transférer la commande à un collègue (acceptation par PIN), convertir comptoir -> table, imprimer l'addition (DUPLICATA si déjà imprimée).
- Hors ligne : les actions indisponibles (OFF-2) sont visibles mais expliquées, jamais cachées silencieusement.

CRITÈRES D'ACCEPTATION
- Une commande payée n'affiche plus d'action de modification, seulement « Demander une correction ».
- Tests : annulation avant et après passage « en préparation ».
```

### I4. Paiement

```
OBJECTIF : écran de paiement.

EXIGENCES : PAI-1 à PAI-6, ARD-2, ARD-3, ARD-6, D7.

DESCRIPTION
- En haut : total net, reste à payer, monnaie à rendre. Une seule action principale : « Valider le paiement », active seulement quand le reste à payer est nul.
- Règlements : espèces (montant reçu, monnaie calculée) et mobile money (montant, opérateur, référence de transaction, tous obligatoires). Ajouter plusieurs règlements est possible.
- Pourboire : champ séparé, hors total.
- Ardoise : bouton distinct ; choisir le client, afficher solde et plafond ; si le plafond serait dépassé, refus clair avec « Demander un déblocage » (R1). L'ardoise exclut tout autre mode.
- Hors ligne : l'ardoise utilise la dernière copie des soldes, sans déblocage possible.

CRITÈRES D'ACCEPTATION
- Scénario : total 3 700 payé 2 000 en espèces et 1 700 en mobile money avec référence ; pourboire de 300 en espèces.
- Scénario : ardoise refusée au-delà du plafond, puis débloquée par le gérant.
- Après validation, la commande est immuable.
```

### I5. Écran cuisine

```
OBJECTIF : écran cuisine, tablette fixe en paysage près du passe.

EXIGENCES : CUI-1 à CUI-5, D3, D4, D17.

DESCRIPTION
- Trois colonnes : Envoyé, En préparation, Prêt. Chaque bon est une grande carte : numéro de table, plats, heure d'envoi, mention DUPLICATA si réimprimé.
- Un appui sur la carte fait avancer le statut (passage à « en préparation » horodaté par le PC).
- Un bon annulé passe en rouge avec le mot « ANNULÉ » et un signal sonore.
- Texte très lisible à deux mètres ; indicateur de connexion visible en haut.
- Les lignes envoyées hors ligne sur papier n'apparaissent pas.

CRITÈRES D'ACCEPTATION
- Si l'écran perd la connexion, il le montre clairement et ne laisse pas croire que la file est à jour.
- Tests : avance de statut, annulation reçue pendant la préparation, nouveau bon avec signal sonore.
```

### I6. Ma caisse et clôture serveur

```
OBJECTIF : écran « Ma caisse » du serveur.

EXIGENCES : CAI-2, CAI-3, CAI-4, CAI-5, PAI-6.

DESCRIPTION
- Résumé : fond de caisse, espèces encaissées, remboursements d'ardoise, pourboires, sorties de caisse validées, espèces attendues.
- Saisie d'une sortie de caisse (montant, motif dans une liste), en attente de validation du gérant.
- Clôture : le serveur saisit le montant compté ; l'écart (manque ou excédent) s'affiche ; s'il est non nul, motif et commentaire sont obligatoires avant de pouvoir clôturer.
- Après clôture : état « en attente du gérant » ; aucune autre vente possible pour ce serveur sur cette journée.

CRITÈRES D'ACCEPTATION
- La formule affichée correspond exactement à CAI-2 (test avec scénario chiffré).
- Impossible de clôturer avec un écart non justifié.
```

### I7. PC caisse : tableau de bord, journée et caisses

```
OBJECTIF : écrans du gérant sur le PC (mise en page bureau : navigation latérale, tableaux denses, raccourcis clavier).

EXIGENCES : CAI-1, CAI-5, CAI-6, ARD-5, STK-3, STK-4, R1, R2, R3.

DESCRIPTION
- Tableau de bord : alertes (stock négatif, entrées à valider, ardoises au-dessus du plafond, écarts de caisse), ventes en cours, état des appareils connectés.
- Journée : ouvrir (fond de caisse par serveur), suivre les caisses, clôturer la journée seulement quand toutes les caisses sont closes.
- Caisses : voir chaque clôture, forcer une clôture avec R1 et motif.
- Le propriétaire voit en plus les valeurs (coûts, marges) ; le gérant voit les mêmes écrans sans ces colonnes, sans espaces vides ni boutons grisés.

CRITÈRES D'ACCEPTATION
- Un gérant ne voit jamais un prix d'achat.
- Tests : clôture de journée refusée tant qu'une caisse est ouverte ; clôture forcée avec R1.
```

### I8. PC caisse : stock, inventaire et ardoises

```
OBJECTIF : écrans de stock et de suivi des ardoises sur le PC.

EXIGENCES : STK-2 à STK-6, ARD-1, ARD-5, PRX-1, D19, O9, O16.

DESCRIPTION
- Stock : liste des produits avec quantité, produits négatifs en tête, historique des mouvements.
- Entrées : file des entrées « à valider » avec valider ou rejeter ; saisie d'une entrée (quantités seulement).
- Inventaire quotidien des boissons : comptage rapide, écarts affichés en quantités, motif obligatoire par écart ; la valorisation n'apparaît que pour le propriétaire.
- Pertes : casses, annulations après préparation, offerts, écarts négatifs, affichés séparément.
- Ardoises : clients avec solde, plafond, dépassements ; fixer un plafond ; enregistrer un remboursement.
- Prix de vente : modification avec refus si le prix est inférieur ou égal au coût, sans afficher le coût (PRX-1).

CRITÈRES D'ACCEPTATION
- Tests : rejet d'une entrée, inventaire avec manque et excédent, tentative de prix sous le seuil par un gérant.
```

---

## 4. Prompt de revue (à utiliser en fin de session)

```
Passe en revue ce que tu viens de produire contre specification-snack-bar.md.

1. Liste chaque exigence concernée par cette session et indique : couverte (avec le fichier et le test), partielle, ou absente.
2. Signale toute règle que tu as ajoutée ou interprétée et qui ne figure pas dans la spécification.
3. Signale tout endroit où le code contredit une règle transversale (R1 à R5).
4. Liste les trois risques les plus sérieux restants (course, hors ligne, fraude).
5. Propose le prompt de la prochaine session.

Format : un tableau (exigence, statut, preuve) puis les points 2 à 5 en listes courtes. N'écris pas de code.
```
