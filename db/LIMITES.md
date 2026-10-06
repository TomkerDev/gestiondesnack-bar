# M1 · Cas que le schéma seul ne sait pas représenter (règles → M2-M6)

1. Machines à états (commande, journée, caisse, ligne cuisine) : CHECK posent les valeurs, pas les transitions autorisées.
2. Formule CAI-2 et tolérance : calcul applicatif, pas contrainte SQL.
3. Plafond ardoise ARD-2 et déblocage R1 : contrôle applicatif temps réel.
4. Arbitrage de course CUI-3 (premier enregistré gagne) : UPDATE...WHERE atomique en M4.
5. Jeton R1 60s / 1 usage : logique applicative + horloge centrale.
6. Numéros séquentiels sans trou : compteur + transaction, alerte trou en RPT-1.
7. Séparation saisie≠validation (STK-4) : contrôle applicatif.
8. Prix ≤ coût refusé sans révéler coût (PRX-1+R3) : logique + droits.
