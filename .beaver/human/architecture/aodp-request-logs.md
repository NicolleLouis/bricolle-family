# AODP Request Logs Architecture

## Objective
Permettre dans `albion_online` l’analyse rapide des appels sortants vers AODP pour déboguer les données, comprendre les réponses reçues et retrouver un cas précis via une recherche textuelle.

Succès attendu:
- chaque appel AODP est persisté avec la requête et la réponse utiles au debug;
- une page front dédiée permet de filtrer et de relire ces échanges proprement;
- les réponses en erreur ressortent visuellement en rouge;
- les données expirent automatiquement après 24 heures pour éviter l’encombrement de la base;
- la purge s’exécute de façon opportuniste au début d’un nouvel appel AODP et ne doit jamais bloquer le fetch si elle échoue.

## Current State
Dans `albion_online`, les appels AODP sont centralisés dans `albion_online/services/price_fetcher.py`.

État actuel constaté:
- `AlbionOnlineDataPriceFetcher._fetch_price_payload()` construit l’URL, logge l’URL via `logging`, effectue un `GET`, puis appelle `raise_for_status()` avant de lire le JSON;
- la réponse AODP n’est pas stockée en base;
- un endpoint de debug temporaire existe déjà dans `albion_online/views/artifact_salvage.py`, mais il sert seulement à inspecter les objets envoyés, pas les échanges HTTP complets;
- l’app `albion_online` a déjà un pattern de page simple avec Bootstrap, navigation commune, et pages publiques/staff-only gérées par les middlewares globaux;
- le projet utilise déjà Celery pour les tâches asynchrones, mais la rétention de ces logs n’a pas besoin d’un job dédié vu le faible volume annoncé.

Contrainte d’accès importante:
- `albion_online` est déjà protégé par les middlewares globaux du projet; cette nouvelle page doit suivre exactement le même niveau d’accès que le reste de l’app, sans ajouter une politique spéciale.

## Target Behavior
Le système doit enregistrer un log à chaque requête AODP effectuée par l’app.

Comportement cible:
1. Lors d’un fetch AODP, le code persiste une entrée de log avec le contexte de la requête.
2. Si AODP répond correctement, la réponse brute est conservée et affichable.
3. Si AODP renvoie une erreur HTTP ou si l’appel échoue, le log garde l’état d’échec et le message d’erreur utile au debug.
4. Une page front dédiée affiche les logs sous une forme lisible:
   - liste des entrées récentes;
   - recherche par string;
   - affichage lisible de la query de requête et du body de réponse;
   - mise en évidence visuelle des entrées en erreur.
5. Les logs expirés sont supprimés automatiquement après 24 heures, au minimum via une purge opportuniste au début des nouveaux appels.

Hypothèse fonctionnelle retenue:
- la recherche textuelle doit couvrir la query de requête et le body de réponse, pas les headers ni d’autres payloads.

## Non-Goals
- Pas de stockage des headers complets.
- Pas d’export CSV ou JSON des logs.
- Pas de full-text search Postgres ni d’indexation avancée au départ.
- Pas de routage API séparé pour ces logs.
- Pas de rétention longue durée, d’archivage, ou de backfill historique.
- Pas de refonte globale du design de l’app.

## Key Decisions
- Les logs seront stockés en base dans une nouvelle table dédiée.
- Chaque log représentera un appel HTTP sortant unique vers AODP.
- Le contenu conservé sera limité à ce qui aide réellement au debug: contexte de la requête, query string, status HTTP, body brut de réponse, et message d’erreur si besoin.
- La recherche côté front utilisera une simple recherche substring insensible à la casse sur la query de requête et le body de réponse.
- Les réponses en erreur seront marquées explicitement en base afin de pouvoir être colorées en rouge dans l’UX sans recalcul complexe.
- La page de consultation sera une page simple de type liste + détails repliables, pas un mini-outil de BI.
- La rétention 24h sera gérée par un service de purge déclenché au début de l’appel AODP, avec un comportement best-effort et idempotent.
- Avec le volume annoncé d’environ 50 requêtes/jour, une solution basée sur `TextField` + `icontains` est suffisante; aucune optimisation de recherche avancée n’est nécessaire pour cette phase.
- La persistance des logs AODP ne doit exister que dans le service de fetch des prix, ou dans des helpers privés appelés uniquement par ce service.

## Open Questions
- Aucune question bloquante. Le volume annoncé et le besoin produit sont assez clairs pour cadrer une solution simple.

## Proposed Architecture
Introduire une brique de log AODP dans `albion_online` autour de trois responsabilités:

- capture des échanges HTTP lors des appels AODP;
- lecture et filtrage des logs pour la page front;
- purge des entrées expirées.

Composants proposés:

- `albion_online/models/aodp_request_log.py`
  - modèle persistant des appels AODP;
  - enregistrement admin dans le même module;
  - champs orientés debug et recherche.
- `albion_online/services/aodp_request_log_service.py`
  - logique métier de lecture, recherche et purge;
  - helpers privés de persistance appelables uniquement depuis `price_fetcher.py`;
  - garde la vue et le fetcher fins;
  - contient la normalisation d’affichage des payloads.
- `albion_online/views/aodp_request_log.py`
  - vue liste avec filtre textuel;
  - pagination légère ou limite de page, suffisante pour 24h de données;
  - rendu des états d’erreur et des détails.
- `albion_online/templates/albion_online/aodp_request_log.html`
  - table ou cartes Bootstrap avec zone de recherche;
  - rendu propre des query strings et bodies via `<pre>`/`<details>`.

Boundaries:

- `price_fetcher.py` reste le seul point de capture HTTP AODP;
- aucune autre partie de l’app ne doit créer ou écrire de log AODP directement;
- la logique de persistance de logs ne doit pas fuir dans les templates;
- la vue front ne doit pas recalculer la classification d’erreur, elle consomme l’état déjà persisté;
- la purge doit rester idempotente et ne jamais bloquer le flux principal.

## Data Model
Créer une nouvelle table `AodpRequestLog`.

Champs recommandés:
- `source`: origine métier de l’appel, par exemple `leather_jacket`, `gathering_gear`, `artifact_salvage`;
- `request_url`: URL complète appelée;
- `request_query_string`: query string brute ou normalisée;
- `response_status_code`: code HTTP reçu, nullable si l’appel échoue avant réponse;
- `response_body_raw`: body brut de réponse, vide si aucun body n’est disponible;
- `error_message`: texte d’erreur lisible pour les cas d’échec;
- `is_error`: booléen dérivé ou stocké pour la mise en forme rapide;
- `created_at`: date de création indexée;
- `duration_ms`: durée de l’appel, utile pour repérer les lenteurs.

Indexation:
- index sur `created_at` pour la purge et l’ordre chronologique;
- index sur `source` pour filtrer par provenance;
- index sur `is_error` si on veut un filtre “erreurs seulement” sans scan inutile.

Contraintes:
- un log doit pouvoir représenter un échec sans body de réponse;
- les bodies peuvent être volumineux, donc `TextField` plutôt que `CharField`;
- aucun chiffrement ou redaction spécifique n’est nécessaire ici, car les payloads AODP sont publics et non sensibles dans ce contexte.

Migration:
- nouvelle migration Django pour la table;
- aucune modification des tables existantes n’est requise.

## Backend Flow
Flux recommandé pour chaque requête AODP:

1. `AlbionOnlineDataPriceFetcher._fetch_price_payload()` construit l’URL.
2. Avant ou autour de l’appel réseau, le code capture:
   - l’URL;
   - la query string;
   - la source métier;
   - le timestamp de début.
3. La requête HTTP est exécutée.
4. Si une réponse existe:
   - le status code est stocké;
   - le body brut est lu et persisté;
   - `raise_for_status()` est exécuté après capture du body pour garder le debug des 4xx/5xx.
5. Si une exception réseau ou HTTP survient:
   - l’entrée de log garde `is_error=True`;
   - `error_message` conserve la raison lisible;
   - la vue front affiche la ligne en rouge.
6. La réponse utile continue ensuite le pipeline normal de refresh des prix.

Purge:

- la purge s’exécute au début de l’appel AODP, avant la requête réseau;
- l’opération reste best-effort: si le `DELETE` échoue, le fetch continue;
- la suppression porte sur `created_at < now - 24h`;
- aucune tâche Celery dédiée n’est nécessaire pour cette rétention, compte tenu du faible volume annoncé.

Service design:

- la persistance du log est encapsulée dans `AlbionOnlineDataPriceFetcher` ou un helper privé appelé exclusivement par ce fetcher;
- aucun autre service, vue, task ou template ne doit créer des entrées AODP directement;
- un service de requête construit la liste filtrée pour la vue;
- un service de purge encapsule la règle de rétention et le calcul de l’horodatage de coupure.

## Frontend Flow
La page front doit rester simple et lisible.

Structure cible:
- une barre de recherche textuelle en haut;
- un filtre optionnel par source si utile;
- une liste paginée ou bornée des logs récents;
- chaque ligne montre le statut, la date, la source, et un extrait de la query;
- un panneau repliable affiche:
  - la query de requête;
  - le body brut de réponse;
  - le message d’erreur;
  - le status HTTP et la durée.

UX d’erreur:
- une ligne en échec reçoit un style rouge ou une badge de danger;
- le body de réponse doit rester lisible via formatage préserve les retours à la ligne;
- si le body est du JSON valide, il peut être beautifié au rendu sans changer la donnée stockée.

Navigation:
- ajouter un lien dans le header Albion, qui doit être le point d’accès principal à la page;
- ajouter un accès depuis la home de l’app pour ne pas dépendre uniquement de l’admin.

## Authorization And Feature Gates
Pas de nouvelle règle d’accès.

Décision:
- la page suit le niveau d’accès existant de `albion_online`;
- aucune permission spéciale, aucun flag produit, aucun rôle additionnel.

Conséquence:
- les logs restent visibles aux mêmes utilisateurs que le reste de l’app;
- si une future restriction est nécessaire, elle devra être ajoutée par un gate explicite et non via ce mécanisme de base.

## Observability And Operations
Points d’observabilité à prévoir:
- log applicatif court à chaque capture d’appel AODP avec source, status, durée et id de log;
- message d’erreur gardé en base pour le debug UI;
- purge opportuniste silencieuse, avec log INFO du nombre de lignes supprimées;
- possibilité d’inspecter aussi le modèle dans l’admin Django si besoin d’investigation rapide.

Opérations:
- la table reste petite à cause de la rétention 24h;
- aucune archive n’est conservée;
- si aucun nouvel appel AODP ne survient pendant un moment, des lignes un peu plus vieilles que 24h peuvent rester jusqu’au prochain fetch, ce qui est acceptable au vu du volume.

## Edge Cases
- réponse HTTP 4xx/5xx avec body utile: le body doit être persisté avant l’exception;
- échec réseau sans réponse: la ligne doit quand même exister avec un message d’erreur;
- body non-JSON ou JSON invalide: afficher brut sans casser le rendu;
- query string vide: la recherche ne doit pas échouer;
- entrée très longue: le rendu doit préserver le scroll horizontal ou le wrapping via Bootstrap;
- purge simultanée et lecture: la liste ne doit pas casser si une ligne disparaît entre deux requêtes;
- volume faible mais bursts ponctuels: la pagination ou la limite de page doit éviter un écran trop long.

## Testing Strategy
Tests attendus:

- modèle:
  - création d’un log;
  - marquage d’erreur;
  - ordre par date;
  - admin search fields si pertinent.
- service:
  - capture d’un succès HTTP;
  - capture d’un échec HTTP;
  - purge des entrées expirées;
  - filtrage par string sur query et body.
- fetcher:
  - appel réussi loggé;
  - réponse HTTP en erreur loggée avant exception;
  - body de réponse conservé.
- view:
  - page rendue;
  - recherche appliquée;
  - styling d’erreur visible;
  - navigation vers la page.

Validation recommandée:
- tests unitaires ciblés sur le service de log;
- tests de fetcher pour vérifier la capture au bon endroit;
- test de vue pour vérifier le rendu Bootstrap et la recherche.

## Rollout And Migration
Ordre de déploiement recommandé:

1. ajouter le modèle, l’admin, et la migration;
2. brancher la capture dans `price_fetcher.py`;
3. ajouter la vue, le template, et la navigation;
4. brancher la purge opportuniste au début du fetch;
5. compléter les tests et vérifier le chemin d’erreur.

Compatibilité:
- le flux actuel de refresh des prix ne doit pas changer fonctionnellement;
- si le log échoue, il ne doit pas casser la récupération de prix;
- la purge ne doit jamais empêcher un refresh AODP de réussir.

Rollback:
- retirer la capture de log dans le fetcher doit suffire à stopper les nouvelles écritures;
- la table peut être purgée ou laissée sans usage sans casser les pages existantes.

## Files Expected To Change
Probables fichiers à créer ou modifier:

- `albion_online/models/aodp_request_log.py` new
- `albion_online/models/__init__.py`
- `albion_online/services/aodp_request_log_service.py` new
- `albion_online/services/price_fetcher.py`
- `albion_online/views/aodp_request_log.py` new
- `albion_online/templates/albion_online/aodp_request_log.html` new
- `albion_online/urls.py`
- `albion_online/templates/albion_online/header.html`
- `albion_online/templates/albion_online/home.html`
- `albion_online/migrations/*` new
- `albion_online/tests/test_aodp_request_log_service.py` new
- `albion_online/tests/test_aodp_request_log_view.py` new
- `albion_online/tests/test_price_fetcher.py`
