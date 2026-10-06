# Spécification fonctionnelle : application de gestion de snack-bar

Version 1.2 · 6 octobre 2026 · Statut : M7 tranché (Q1-A, Q2-A, Q3-A, Q4-A, Q5-A), prêt pour M1

Les références entre crochets (D1, O5, R1...) renvoient aux décisions prises pendant la phase de cadrage.

## 1. Objet et périmètre

Application de caisse, de stock et de suivi de cuisine pour un snack-bar : boissons alcoolisées ou non (le whisky se vend à la bouteille) et cuisine associée. Elle est utilisée par plusieurs serveurs sur leurs propres appareils, autour d'un PC caisse central.

**Inclus en v1** : commandes (table et comptoir), cuisine (écran et impression), paiements en espèces et mobile money, ardoise avec plafond, stock des boissons, inventaire quotidien, caisse et clôture par serveur, journée d'exploitation, rapports (dont marges des plats sur coût estimé), pourboires, mode hors ligne.

**Exclu de la v1** : carte bancaire, recettes détaillées et stock des ingrédients (prévus en v2, O10), factures et gestion des fournisseurs, vente à la dose, comptabilité légale ou fiscale.

## 2. Glossaire

- **Journée d'exploitation** : période ouverte puis clôturée explicitement par le gérant (R2).
- **Commande** : appartient à un serveur ; mode *table* ou *comptoir* ; statuts ouverte, payée, annulée.
- **Ligne** : produit, quantité, prix unitaire figé, coût unitaire figé, remise, statut cuisine.
- **Caisse serveur** : espèces encaissées par un serveur pendant une journée.
- **Ardoise** : dette plafonnée d'un client identifié.
- **Autorisation gérant** : voir R1. **Correction** : voir R4.

## 3. Rôles et droits

Le propriétaire cumule tous les droits du gérant.

| Action | Serveur | Gérant | Propriétaire |
|---|---|---|---|
| Ses commandes, encaissement, ardoise dans le plafond | ✓ | ✓ | ✓ |
| Annuler un plat avant préparation ; retirer une boisson d'une commande non payée | ✓ | ✓ | ✓ |
| Annuler après préparation, remises, offerts, déblocage de plafond, corrections (R1) | ✗ | ✓ | ✓ |
| Fixer prix de vente et plafonds d'ardoise | ✗ | ✓ | ✓ |
| Saisir une entrée de stock | si désigné | ✓ | ✓ |
| Valider une entrée de stock | ✗ | ✓ | ✓ |
| Inventaire, fond de caisse, forcer une clôture de caisse, clôturer la journée | ✗ | ✓ | ✓ |
| Prix d'achat et coûts estimés, marges, valeur des écarts, paramètres, utilisateurs, tolérance d'écart | ✗ | ✗ | ✓ |

## 4. Règles transversales

- **R1. Autorisation gérant.** Le gérant (ou le propriétaire) saisit son code personnel sur l'appareil du serveur, dans une fenêtre hors-session. Le système enregistre qui autorise, quel acte, quelle commande, quel motif, à quelle heure. Une autorisation vaut pour un acte précis (jeton à usage unique lié à acte, commande, montant, heure et demandeur, expire après 60 secondes, re-saisie du PIN à chaque acte), jamais pour une période. Elle est indisponible hors ligne. Blocage du PIN après 5 échecs : 5 minutes puis 15 minutes, tracé. [M7-Q5-A]
- **R2. Journée d'exploitation.** Commandes, paiements, mouvements de stock et rapports se rattachent à la journée d'exploitation, pas à la date du calendrier. Un service qui dépasse minuit reste dans la même journée.
- **R3. Coûts réservés au propriétaire.** Prix d'achat, coûts estimés des plats, marges et valorisation des écarts ne sont visibles et modifiables que par le propriétaire. Le gérant voit les écarts en quantités. Toute modification est tracée.
- **R4. Commande payée immuable.** Une commande payée ne se modifie plus. Toute correction est un enregistrement distinct qui référence l'original, autorisé par R1, tracé, et précisant le sort du produit (retour en stock ou perte).
- **R5. Journées closes définitives.** Une journée clôturée n'est jamais rouverte. Une correction portant sur une journée passée est comptabilisée dans la journée en cours, avec référence à la commande d'origine.

## 5. Exigences fonctionnelles

### 5.1 Commandes et service

- **CMD-1** Une commande est en mode *table* (addition ouverte, modifiable jusqu'au paiement) ou *comptoir* (créée et payée en un seul flux, jamais laissée ouverte). [D1]
- **CMD-2** Une table peut avoir plusieurs commandes ouvertes. Chaque commande a un seul payeur et ne se scinde pas. Le transfert de lignes entre commandes d'une même table est permis avant paiement, et tracé. [D6, O4]
- **CMD-3** Une commande comptoir peut devenir une commande de table, par le serveur qui l'a créée. L'inverse est impossible. [O1]
- **CMD-4** Une commande appartient à un serveur. Pour la transférer, le serveur receveur accepte avec son code ; le gérant peut aussi la transférer. [D11, O7]
- **CMD-5** Un serveur peut retirer une boisson tant que la commande n'est pas payée, avec motif et restitution au stock. Si la boisson a été servie, le gérant arbitre et la comptabilise en perte. [O2]
- **CMD-6** Les identifiants de commande sont générés sur l'appareil et uniques sans coordination avec le PC. [D16]
- **CMD-7** L'addition s'imprime avant paiement. Chaque impression est tracée, une réimpression porte la mention DUPLICATA, et toute modification après impression déclenche une nouvelle addition et un événement tracé. Il n'y a pas de reçu après paiement. Hors ligne, le paiement sans addition est autorisé à titre exceptionnel : la commande prend le statut `payée_sans_addition`, l'addition doit être réimprimée à la resynchronisation avant la clôture de la journée. [D23, M7-Q2-A]

### 5.2 Cuisine

- **CUI-1** Un envoi en cuisine produit un bon au numéro unique, affiché à l'écran et imprimé. [D3]
- **CUI-2** Une réimpression porte la mention DUPLICATA. Aucun plat ne dépend d'un seul canal : si l'écran ou l'imprimante tombe, l'autre continue.
- **CUI-3** Statuts d'un plat : envoyé, en préparation, prêt, servi. Le passage à « en préparation » est horodaté par le système central ; si le serveur et la cuisine agissent en même temps, le premier enregistré l'emporte. [D4]
- **CUI-4** Annulation d'un plat : par le serveur tant qu'il est « envoyé » ; ensuite par le gérant (R1). Toute annulation est tracée (qui, quand, motif) et notifiée à la cuisine (écran et bon d'annulation). Un plat annulé après préparation est une perte. [D4]
- **CUI-5** Hors ligne, le bon est écrit à la main. Le serveur marque les lignes « envoyé sur papier » ; elles n'apparaissent pas à l'écran cuisine et n'ont pas de statuts. L'annulation d'un plat est impossible hors ligne ; le gérant la corrige ensuite (R1). [D17, O14]

### 5.3 Paiement

- **PAI-1** Modes acceptés : espèces et mobile money. La liste est un paramètre, pas du code figé. [D8]
- **PAI-2** Une commande est payée quand la somme de ses règlements égale son total net. Espèces et mobile money peuvent se combiner. L'ardoise est exclusive et couvre la totalité de la commande. [D7]
- **PAI-3** En espèces, on enregistre le montant reçu et la monnaie rendue.
- **PAI-4** En mobile money, la référence de transaction et l'opérateur sont obligatoires, saisis par le serveur, et rapprochés du relevé à la clôture. Les paiements ne doivent arriver que sur des numéros de l'établissement. [O5, D11]
- **PAI-5** Remises et offerts : gérant ou propriétaire seulement (R1), par ligne, en pourcentage ou en montant, avec un motif choisi dans une liste. Un offert est une remise de 100 % : la ligne est conservée et le stock décrémenté. [D9, O6]
- **PAI-6** Un pourboire est saisi comme un montant distinct du paiement : il n'entre ni dans le total de la commande ni dans le chiffre d'affaires. Un pourboire en espèces compte dans les espèces attendues. Il est reversé au serveur par une sortie de caisse (motif « reversement de pourboire »), y compris quand il a été payé en mobile money.

### 5.4 Ardoise

- **ARD-1** Un client a un nom, un téléphone, un plafond et un solde dû. Le plafond est fixé par le gérant ou le propriétaire. [D2, O3]
- **ARD-2** Une vente sur ardoise exige un client identifié et un solde dû plus montant de la vente inférieur ou égal au plafond. Sinon la vente est refusée. [D2]
- **ARD-3** Le gérant peut débloquer une vente (R1). Le déblocage est ponctuel, ne modifie pas le plafond, et est tracé. [D5]
- **ARD-4** Un remboursement d'ardoise est un encaissement distinct, attribué au serveur qui l'encaisse. Une vente sur ardoise compte dans le chiffre d'affaires mais pas dans les espèces attendues. [D2]
- **ARD-5** Le gérant dispose à tout moment d'un écran des ardoises en cours, avec alerte sur les clients au-dessus de leur plafond. [D22]
- **ARD-6** Hors ligne, le plafond est vérifié avec la dernière copie synchronisée et aucun déblocage n'est possible. Si le plafond a été dépassé entre-temps, le gérant est alerté à la synchronisation. [D16, O13]

### 5.5 Stock

- **STK-1** Le stock est compté en pièces (bouteilles, canettes). Les plats n'ont pas de suivi de stock en v1.
- **STK-2** Toute variation de stock est un mouvement tracé (vente, achat, casse, correction). Aucune modification directe de la quantité.
- **STK-3** La vente est autorisée quand le stock est nul ou négatif. Le gérant est alerté et dispose d'une liste des produits à stock négatif. [D10]
- **STK-4** Une entrée de stock ne contient que des quantités. Elle ne compte pas dans le stock disponible tant qu'elle reste « à valider » (stock disponible vs stock en attente affichés séparément) ; la validation du gérant la fait entrer dans le disponible. Un rejet crée un mouvement inverse. Seuls les utilisateurs portant l'indicateur « peut saisir les entrées » (activé ou retiré par le gérant ou le propriétaire, tracé ; deux ou trois personnes au maximum conseillées) peuvent saisir. La même personne ne peut pas saisir puis valider la même entrée. [D19, O15, M7-Q1-A]
- **STK-5** Inventaire quotidien des boissons, par le gérant, après la clôture des caisses et avant la clôture de la journée (ordre : caisses closes, puis inventaire, puis clôture journée). L'inventaire est rattaché à la journée qui se clôt. Chaque écart devient un mouvement de correction avec motif. [D12, O9, M7-Q3-A]
- **STK-6** Les pertes regroupent les casses déclarées, les annulations après préparation, les offerts et les écarts d'inventaire négatifs. Elles sont affichées séparément et valorisées au coût (propriétaire). [O16]

### 5.6 Caisse et clôture

- **CAI-1** Le gérant ouvre la journée et fixe le fond de caisse de chaque serveur. Il la clôture quand toutes les caisses sont clôturées. [R2, O8]
- **CAI-2** Espèces attendues d'un serveur = fond de caisse + espèces encaissées (monnaie rendue déduite, pourboires en espèces inclus) + remboursements d'ardoise en espèces − sorties de caisse validées. Les remboursements en mobile money et les ventes mobile sont rapprochés comme ventes mobile, hors espèces attendues. Les pourboires mobile reversés en espèces sont des sorties de caisse normales, tracées à part. [M7-Q4-A]
- **CAI-3** Une sortie de caisse (achat urgent, reversement de pourboire, par exemple) est saisie par le serveur avec un motif et validée par le gérant. [O11]
- **CAI-4** À la clôture, le serveur compte son tiroir. Si l'écart absolu est inférieur ou égal à la tolérance, la clôture est possible sans motif (écart enregistré). Si l'écart dépasse la tolérance, un motif et un commentaire sont obligatoires avant clôture. Tolérance zéro par défaut, réglable par le propriétaire, affichée sur l'écran. [D14, O8, M7-Q4-A]
- **CAI-5** Le gérant peut forcer la clôture d'une caisse (R1), avec un motif consigné.
- **CAI-6** Les montants mobile money sont rapprochés du relevé de l'opérateur à la clôture. [D8]

### 5.7 Prix et coûts

- **PRX-1** Un prix de vente modifié ne s'applique qu'aux nouvelles lignes. Si le nouveau prix est inférieur ou égal au coût, le système refuse en affichant « prix sous le seuil de rentabilité » sans révéler le coût. Chaque changement est tracé (qui, ancien et nouveau prix, quand). [D20]
- **PRX-2** Un seul prix d'achat par produit. Pour un plat, le propriétaire saisit un coût estimé (sans recette ni stock d'ingrédients), ce qui donne une marge approximative. Seul le propriétaire les modifie. [D13, O10, R3]
- **PRX-3** Chaque ligne fige le prix de vente et le coût au moment de son ajout. [D13]

### 5.8 Mode hors ligne

- **OFF-1** Si le PC caisse est injoignable, les appareils continuent : prise et modification de commandes, encaissement (espèces, mobile money) et vente sur ardoise. [D15, D16]
- **OFF-2** Indisponibles hors ligne : remises, offerts, autorisations R1, déblocages, annulations après envoi en cuisine, corrections, impression de l'addition.
- **OFF-3** À la resynchronisation, les mouvements de stock s'additionnent sans conflit (grâce à STK-3) et les commandes d'un même serveur ne se heurtent pas (CMD-2, CMD-4). Les alertes (plafond dépassé, stock négatif) sont émises à ce moment.
- **OFF-4** Hors ligne, les prix utilisés sont ceux de la dernière synchronisation.

### 5.9 Identification et traçabilité

- **SEC-1** Chaque personne s'identifie avec un code personnel d'au moins 4 chiffres, sur n'importe quel appareil. Blocage temporaire après 5 échecs ; verrouillage automatique après 2 minutes d'inactivité. [D24, O17]
- **SEC-2** Hors ligne, les appareils ne conservent que des empreintes salées des codes, jamais les codes eux-mêmes.
- **SEC-3** Un journal d'audit non modifiable enregistre qui, quoi, quand, motif et commande pour toute action sensible : annulation, remise, déblocage, correction, changement de prix ou de plafond, entrée de stock, forçage de clôture.

### 5.10 Rapports

- **RPT-1** Le rapport de clôture contient : ventes par produit et par serveur ; écarts de caisse et de stock (en quantités pour le gérant) ; marges (plats inclus, sur coût estimé) et valeur des pertes (propriétaire seulement). [D22, O10]

## 6. Exigences non fonctionnelles et valeurs par défaut

Ces points n'ont pas été discutés en détail ; ce sont des valeurs raisonnables à confirmer à la relecture.

- **Architecture** : le PC caisse (application Tauri, base SQLite en mode WAL) est la référence des données. Il héberge un serveur local HTTP et WebSocket. Les appareils des serveurs utilisent une page web installable qui fonctionne hors ligne. Le réseau est un Wi-Fi local, sans internet requis.
- **Sauvegarde** : copie automatique de la base à chaque clôture de journée vers un support externe, export manuel possible, test de restauration périodique.
- **Devise et langue** : une seule devise, configurable ; montants entiers dans la plus petite unité, sans décimales ; interface en français.
- **Conservation** : aucun enregistrement n'est supprimé. La durée légale de conservation est à vérifier avec ton comptable.
- **Matériel** : deux imprimantes thermiques 80 mm compatibles ESC/POS, du même modèle, avec coupeur automatique. Cuisine : connexion réseau (câble Ethernet) avec adresse IP fixe. Addition : USB, près du PC caisse. Le papier thermique craint la chaleur et la graisse. Un onduleur est recommandé pour le PC caisse et le routeur.
- **Réactivité** : une action courante doit répondre en moins d'une seconde sur le Wi-Fi local.

## 7. Annexe : listes de paramétrage par défaut

Ces listes sont des paramètres modifiables par le propriétaire. Le motif « Autre » exige toujours un commentaire. Retirer un motif ne supprime jamais l'historique.

- **Remises et offerts** : offert maison, client fidèle, erreur de service, geste commercial, promotion, consommation du personnel.
- **Casses** : bouteille ou verre cassé, produit périmé ou avarié, boisson renversée, plat raté ou renvoyé.
- **Sorties de caisse** : achat urgent, avance à un livreur ou fournisseur, avance au personnel, reversement de pourboire.
- **Justification d'écart de caisse** : erreur de monnaie rendue, vente non enregistrée, confusion de mode de paiement, sortie de caisse non saisie, remboursement d'ardoise non saisi, erreur de comptage.
- **Écart d'inventaire** : casse non déclarée, offert non saisi, livraison non saisie, vente non saisie, erreur de comptage, vol suspecté.

## 8. Restant avant le développement

- Choisir les références exactes des imprimantes, selon la disponibilité locale du matériel et du papier thermique 80 mm.
- Désigner les personnes autorisées à saisir les entrées de stock (réglage au déploiement, pas une exigence).
- Recettes détaillées et stock des ingrédients : v2, à lancer si le besoin se confirme.
