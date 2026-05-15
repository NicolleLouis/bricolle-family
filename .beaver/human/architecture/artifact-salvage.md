# Artifact Salvage Architecture

## Objective
Créer une nouvelle page Albion Online dédiée au salvage d'artifacts, avec un sélecteur de ville en haut, un bouton `Refresh Price` identique aux pages `gathering_gear` et `leather_jacket`, et une table de lecture rapide pour estimer le seuil d'achat rentable.

Objectif produit:
- afficher, par ville, le prix courant des artefacts suivis;
- regrouper les artefacts en 4 familles: `rune`, `soul`, `relic`, `avalonian`;
- afficher pour chaque famille une table `T6`, `T7`, `T8`;
- comparer chaque prix courant à un seuil `buy_order_price` calculé à partir du prix des shards et des taxes de marché;
- colorer les lignes ou cellules en vert/rouge selon la position du prix courant par rapport au seuil.

Succès attendu:
- la page est lisible en une seule vue;
- le refresh prix suit exactement le même mécanisme asynchrone que les pages existantes;
- l'ajout de nouvelles listes d'artefacts se fait dans le code, sans introduire de nouveau modèle.

## Current State
L'app `albion_online` possède déjà deux pages de marché robustes:

- `gathering_gear` et `leather_jacket` partagent le même pattern de vue:
  - filtre `city` en haut;
  - bouton `Refresh Price`;
  - bannière de suivi du job via `PriceRefreshJob`;
  - cache mémoire invalidé par une clé de version;
  - refresh asynchrone via `refresh_price_job`.

Les pièces importantes déjà en place:

- `albion_online/views/gathering_gear.py` et `albion_online/views/leather_jacket.py` construisent les données, gèrent le cache, les filtres, et lancent le job de refresh.
- `albion_online/tasks.py` exécute le refresh selon `PriceRefreshJob.kind` puis invalide le cache associé.
- `albion_online/models/price_refresh_job.py` porte déjà les kinds `LEATHER_JACKET` et `GATHERING_GEAR`.
- `albion_online/services/price_fetcher.py` récupère les prix courants depuis AODP.
- `albion_online/services/market_summary_core.py` contient déjà les briques de calcul utiles pour la lecture marché.

Contrainte importante vérifiée côté API:

- l'endpoint AODP courant expose `sell_price_min`, `sell_price_max`, `buy_price_min`, `buy_price_max` et leurs dates;
- il n'expose pas de moyenne native dans la réponse courante;
- la page devra donc s'appuyer sur `sell_price_min` comme prix affiché principal.

## Target Behavior
La page `artifact salvage` doit fonctionner comme suit:

1. L'utilisateur choisit une ville dans un sélecteur en haut de page.
2. L'utilisateur peut déclencher `Refresh Price`.
3. La page affiche 4 sections: `rune`, `soul`, `relic`, `avalonian`.
4. Chaque section contient une table avec 3 colonnes: `T6`, `T7`, `T8`.
5. La première ligne de chaque table affiche la valeur de base du shard correspondant, multipliée par `10`.
6. Les lignes suivantes listent les artefacts associés à la famille.
7. Pour chaque artefact, la page affiche le prix courant issu de `sell_price_min`.
8. La cellule est:
   - verte si le prix courant est strictement inférieur à `120%` du `buy_order_price`;
   - rouge sinon.

Règles de calcul retenues:

- `buy_order_price` représente le prix maximal d'achat d'un artefact permettant de garantir `10%` de gain net sur le capital initial.
- la formule prend en compte:
  - une taxe d'achat de `2.5%`;
  - des frais de mise en vente de `2.5%`;
  - une taxe de vente de `4%` sur le prix de vente;
  - un rendement de transformation de `1 artefact -> 10 shards`;
  - un objectif de marge nette de `10%`.
- la formule doit rester pure et testée dans un service métier.

Forme attendue du seuil:

- `buy_order_price = (10 * shard_price * 0.935) / ((1 + buy_tax) * (1 + target_margin))`
- avec `buy_tax = 0.025`, `target_margin = 0.10`
- `0.935 = 1 - 0.025 - 0.04` en modélisation additive sur le prix de vente.
- le calcul final doit être arrondi de façon stable et documentée, idéalement vers l'entier inférieur ou via `round` selon la convention du projet, mais sans créer de divergence entre service et template.

## Non-Goals
- Pas de page secondaire type `profitability`.
- Pas de modèle éditable en admin pour les listes d'artefacts.
- Pas de migration de données pour stocker ces listes.
- Pas de calcul d'average price natif via AODP, puisque l'endpoint courant ne l'expose pas.
- Pas de support `city=all` sur cette page.
- Pas de refonte du design global de l'app.

## Key Decisions
- La page sera une seule route principale, sans onglet secondaire.
- Le sélecteur de ville se comportera comme sur `leather_jacket`: une ville active à la fois.
- Les listes d'artefacts seront codées en dur dans une constante Python.
- Les 4 familles seront structurées de manière homogène pour permettre l'ajout de nouvelles listes sans casser le moteur de rendu.
- Les libellés canoniques AODP servent de référence, pas les variantes ou fautes de frappe fournies initialement.
- Le prix affiché pour comparaison sera `sell_price_min`.
- AODP ne fournit pas de moyenne native sur l'endpoint courant, donc aucune moyenne serveur ne sera consommée pour cette page.
- Le bouton `Refresh Price` utilisera le même pipeline asynchrone, le même banner de statut et la même logique d'invalidation de cache que les autres pages.
- Le calcul du seuil `buy_order_price` vivra dans un service métier testable, pas dans le template.
- Le `120%` servira de seuil de bascule: en dessous, la cellule est verte; à partir de ce seuil, elle est rouge.

## Open Questions
- La convention d'arrondi du `buy_order_price` est `round` vers l'entier le plus proche, comme implémenté par le service et couvert par les tests.

## Proposed Architecture
Créer un ensemble de constantes métier pour décrire les 4 familles d'artefacts, puis construire une vue dédiée qui transforme ces constantes en tables par ville.

Composants proposés:

- `albion_online/constants/artifact_salvage.py`
  - définit les familles `rune`, `soul`, `relic`, `avalonian`;
  - décrit pour chaque artefact son libellé et son identifiant de matching stable.
- `albion_online/services/artifact_salvage_price_refresh.py`
  - récupère les objets concernés et déclenche un refresh prix sur l'ensemble du catalogue suivi;
  - réutilise `GroupedPriceRefreshCore`.
- `albion_online/services/artifact_salvage_market_summary.py`
  - construit les lignes d'affichage pour chaque ville;
  - calcule le prix courant, la valeur de base shard `x10`, le seuil `buy_order_price`, et l'état de couleur.
- `albion_online/views/artifact_salvage.py`
  - gère le filtre `city`;
  - gère le `POST` de refresh;
  - injecte le contexte de rendu et la bannière de job.
- `albion_online/templates/albion_online/artifact_salvage.html`
  - présente les 4 sections en une seule page;
  - réutilise le composant de refresh banner existant.

Boundaries:

- la vue reste fine;
- le service porte le calcul de rentabilité et la sélection des objets;
- le template ne fait que du rendu conditionnel simple;
- aucun code métier ne doit être caché dans le JavaScript de la page.

## Data Model
Aucune nouvelle table métier n'est nécessaire.

Évolutions attendues:

- ajout d'une nouvelle valeur à `PriceRefreshJob.Kind`, par exemple `ARTIFACT_SALVAGE`;
- génération d'une nouvelle migration Django pour refléter cette évolution de l'état du modèle;
- aucune modification du schéma de `Price`, `Object`, ou `Recipe` n'est requise pour cette page.

Source de vérité des prix:

- `Price.sell_price_min` reste la donnée affichée;
- `Price.sell_price_min_date` reste la date de fraîcheur utilisée pour juger la récence;
- aucune moyenne AODP n'est stockée.

Source de vérité des artefacts:

- une constante Python versionnée dans le repo;
- chaque entrée doit avoir un label lisible et un identifiant de matching fiable;
- si un identifiant n'existe pas encore, il faudra le normaliser avant la mise en production.

Correspondance AODP normalisée pour l'implémentation. Le code doit utiliser le fragment
`aodp_id` hors tier, pas le libellé brut saisi ici.

```text
rune | Bloodforged Blade -> ARTEFACT_MAIN_SCIMITAR_MORGANA
rune | Ancient Halberd Head -> ARTEFACT_2H_HALBERD_MORGANA
rune | Runed Rock -> ARTEFACT_MAIN_ROCKMACE_KEEPER
rune | Ancient Hammer Head -> ARTEFACT_2H_HAMMER_UNDEAD
rune | Ursine Guardian Remains -> ARTEFACT_2H_KNUCKLES_KEEPER
rune | Lost Crossbow Mechanism -> ARTEFACT_2H_REPEATINGCROSSBOW_UNDEAD
rune | Ancient Shield Core -> ARTEFACT_OFF_TOWERSHIELD_UNDEAD
rune | Ancient Padding -> ARTEFACT_HEAD_PLATE_UNDEAD
rune | Ancient Chain Rings -> ARTEFACT_ARMOR_PLATE_UNDEAD
rune | Ancient Bindings -> ARTEFACT_SHOES_PLATE_UNDEAD
rune | Ghastly Arrows -> ARTEFACT_2H_LONGBOW_UNDEAD
rune | Keeper Spearhead -> ARTEFACT_MAIN_SPEAR_KEEPER
rune | Druidic Inscriptions -> ARTEFACT_MAIN_NATURESTAFF_KEEPER
rune | Hardened Debole -> ARTEFACT_MAIN_RAPIER_MORGANA
rune | Reinforced Morgana Pole -> ARTEFACT_2H_COMBATSTAFF_MORGANA
rune | Werewolf Remnant -> ARTEFACT_2H_SHAPESHIFTER_MORGANA
rune | Runed Horn -> ARTEFACT_OFF_HORN_KEEPER
rune | Imbued Visor -> ARTEFACT_HEAD_LEATHER_MORGANA
rune | Imbued Leather Folds -> ARTEFACT_ARMOR_LEATHER_MORGANA
rune | Imbued Soles -> ARTEFACT_SHOES_LEATHER_MORGANA
rune | Wildfire Orb -> ARTEFACT_MAIN_FIRESTAFF_KEEPER
rune | Possessed Scroll -> ARTEFACT_MAIN_HOLYSTAFF_MORGANA
rune | Lost Arcane Crystal -> ARTEFACT_MAIN_ARCANESTAFF_UNDEAD
rune | Hoarfrost Orb -> ARTEFACT_MAIN_FROSTSTAFF_KEEPER
rune | Lost Cursed Crystal -> ARTEFACT_MAIN_CURSEDSTAFF_UNDEAD
rune | Alluring Crystal -> ARTEFACT_OFF_ORB_MORGANA
rune | Druidic Preserved Beak -> ARTEFACT_HEAD_CLOTH_KEEPER
rune | Druidic Feathers -> ARTEFACT_ARMOR_CLOTH_KEEPER
rune | Druidic Bindings -> ARTEFACT_SHOES_CLOTH_KEEPER
soul | Burning Orb -> ARTEFACT_2H_FIRESTAFF_HELL
soul | Infernal Scroll -> ARTEFACT_2H_HOLYSTAFF_HELL
soul | Occult Orb -> ARTEFACT_2H_ARCANESTAFF_HELL
soul | Icicle Orb -> ARTEFACT_2H_ICEGAUNTLETS_HELL
soul | Cursed Jawbone -> ARTEFACT_2H_SKULLORB_HELL
soul | Demonic Jawbone -> ARTEFACT_OFF_DEMONSKULL_HELL
soul | Infernal Cloth Visor -> ARTEFACT_HEAD_CLOTH_HELL
soul | Infernal Cloth Folds -> ARTEFACT_ARMOR_CLOTH_HELL
soul | Infernal Cloth Bindings -> ARTEFACT_SHOES_CLOTH_HELL
soul | Demonic Arrowheads -> ARTEFACT_2H_BOW_HELL
soul | Infernal Harpoon Tip -> ARTEFACT_2H_HARPOON_HELL
soul | Symbol of Blight -> ARTEFACT_2H_NATURESTAFF_HELL
soul | Broken Demonic Fang -> ARTEFACT_MAIN_DAGGER_HELL
soul | Hellfire Imp Remnant -> ARTEFACT_2H_SHAPESHIFTER_HELL
soul | Hellish Handle -> ARTEFACT_OFF_JESTERCANE_HELL
soul | Demonhide Padding -> ARTEFACT_HEAD_LEATHER_HELL
soul | Demonhide Leather -> ARTEFACT_ARMOR_LEATHER_HELL
soul | Demonhide Bindings -> ARTEFACT_SHOES_LEATHER_HELL
soul | Demonic Blade -> ARTEFACT_2H_CLEAVER_HELL
soul | Hellish Sicklehead -> ARTEFACT_2H_SCYTHE_HELL
soul | Infernal Mace Head -> ARTEFACT_2H_MACE_MORGANA
soul | Hellish Hammer Heads -> ARTEFACT_2H_DUALHAMMER_HELL
soul | Severed Demonic Horns -> ARTEFACT_2H_KNUCKLES_HELL
soul | Hellish Bolts -> ARTEFACT_2H_DUALCROSSBOW_HELL
soul | Infernal Shield Core -> ARTEFACT_OFF_SHIELD_HELL
soul | Demonic Scraps -> ARTEFACT_HEAD_PLATE_HELL
soul | Demonic Plates -> ARTEFACT_ARMOR_PLATE_HELL
soul | Demonic Filling -> ARTEFACT_SHOES_PLATE_HELL
soul | Hellish Sicklehead Pair -> ARTEFACT_2H_TWINSCYTHE_HELL
relic | Unholy Scroll -> ARTEFACT_2H_INFERNOSTAFF_MORGANA
relic | Ghastly Scroll -> ARTEFACT_2H_HOLYSTAFF_UNDEAD
relic | Possessed Catalyst -> ARTEFACT_2H_ENIGMATICORB_MORGANA
relic | Cursed Frozen Crystal -> ARTEFACT_2H_ICECRYSTAL_UNDEAD
relic | Bloodforged Catalyst -> ARTEFACT_2H_CURSEDSTAFF_MORGANA
relic | Inscribed Stone -> ARTEFACT_OFF_TOTEM_KEEPER
relic | Alluring Padding -> ARTEFACT_HEAD_CLOTH_MORGANA
relic | Alluring Amulet -> ARTEFACT_ARMOR_CLOTH_MORGANA
relic | Alluring Bindings -> ARTEFACT_SHOES_CLOTH_MORGANA
relic | Carved Bone -> ARTEFACT_2H_BOW_KEEPER
relic | Cursed Barbs -> ARTEFACT_2H_TRIDENT_UNDEAD
relic | Preserved Log -> ARTEFACT_2H_NATURESTAFF_KEEPER
relic | Ghastly Blades -> ARTEFACT_2H_DUALSICKLE_UNDEAD
relic | Preserved Rocks -> ARTEFACT_2H_ROCKSTAFF_KEEPER
relic | Runestone Golem Remnant -> ARTEFACT_2H_SHAPESHIFTER_KEEPER
relic | Ghastly Candle -> ARTEFACT_OFF_LAMP_UNDEAD
relic | Ghastly Visor -> ARTEFACT_HEAD_LEATHER_UNDEAD
relic | Ghastly Leather -> ARTEFACT_ARMOR_LEATHER_UNDEAD
relic | Ghastly Bindings -> ARTEFACT_SHOES_LEATHER_UNDEAD
relic | Cursed Blades -> ARTEFACT_2H_DUALSCIMITAR_UNDEAD
relic | Keeper Axeheads -> ARTEFACT_2H_DUALAXE_KEEPER
relic | Imbued Mace Head -> ARTEFACT_2H_MACE_MORGANA
relic | Engraved Log -> ARTEFACT_2H_RAM_KEEPER
relic | Warped Raven Plate -> ARTEFACT_2H_KNUCKLES_MORGANA
relic | Alluring Bolts -> ARTEFACT_2H_CROSSBOWLARGE_MORGANA
relic | Bloodforged Spikes -> ARTEFACT_OFF_SPIKEDSHIELD_MORGANA
relic | Carved Skull Padding -> ARTEFACT_HEAD_PLATE_KEEPER
relic | Preserved Animal Fur -> ARTEFACT_ARMOR_PLATE_KEEPER
relic | Inscribed Bindings -> ARTEFACT_SHOES_PLATE_KEEPER
avalonian | Glowing Harmonic Ring -> ARTEFACT_2H_FIRE_RINGPAIR_AVALON
avalonian | Hypnotic Harmonic Ring -> ARTEFACT_2H_ARCANE_RINGPAIR_AVALON
avalonian | Messianic Curio -> ARTEFACT_MAIN_HOLYSTAFF_AVALON
avalonian | Chilled Crystalline Shard -> ARTEFACT_MAIN_FROSTSTAFF_AVALON
avalonian | Fractured Opaque Orb -> ARTEFACT_MAIN_CURSEDSTAFF_AVALON
avalonian | Severed Celestial Keepsake -> ARTEFACT_OFF_CENSER_AVALON
avalonian | Sanctified Mask -> ARTEFACT_HEAD_CLOTH_AVALON
avalonian | Sanctified Belt -> ARTEFACT_ARMOR_CLOTH_AVALON
avalonian | Sanctified Bindings -> ARTEFACT_SHOES_CLOTH_AVALON
avalonian | Immaculately Crafted Riser -> ARTEFACT_2H_BOW_AVALON
avalonian | Ruined Ancestral Vamplate -> ARTEFACT_MAIN_SPEAR_LANCE_AVALON
avalonian | Uprooted Perennial Sapling -> ARTEFACT_MAIN_NATURESTAFF_AVALON
avalonian | Bloodstained Antiquities -> ARTEFACT_2H_DAGGER_KATAR_AVALON
avalonian | Timeworn Walking Staff -> ARTEFACT_2H_QUARTERSTAFF_AVALON
avalonian | Dawnbird Remnant -> ARTEFACT_2H_SHAPESHIFTER_AVALON
avalonian | Shattered Avalonian Memento -> ARTEFACT_OFF_TALISMAN_AVALON
avalonian | Augured Padding -> ARTEFACT_HEAD_LEATHER_AVALON
avalonian | Augured Sash -> ARTEFACT_ARMOR_LEATHER_AVALON
avalonian | Augured Fasteners -> ARTEFACT_SHOES_LEATHER_AVALON
avalonian | Remnants of the Old King -> ARTEFACT_2H_CLAYMORE_AVALON
avalonian | Avalonian Battle Memoir -> ARTEFACT_2H_AXE_AVALON
avalonian | Broken Oaths -> ARTEFACT_2H_DUALMACE_AVALON
avalonian | Massive Metallic Hand -> ARTEFACT_2H_HAMMER_AVALON
avalonian | Damaged Avalonian Gauntlet -> ARTEFACT_2H_KNUCKLES_AVALON
avalonian | Humming Avalonian Whirligig -> ARTEFACT_2H_CROSSBOW_CANNON_AVALON
avalonian | Crushed Avalonian Heirloom -> ARTEFACT_OFF_SHIELD_AVALON
avalonian | Exalted Visor -> ARTEFACT_HEAD_PLATE_AVALON
avalonian | Exalted Plating -> ARTEFACT_ARMOR_PLATE_AVALON
avalonian | Exalted Greave -> ARTEFACT_SHOES_PLATE_AVALON
```

Catalogue figé à ce stade:

- `rune`:
  - Bloodforged Blade
  - Halberd Head
  - Runed Rock
  - Hammer Head
  - Ursine Guardian Remains
  - Lost crossbow mechanism
  - ancient shield core
  - ancient padding
  - ancient chain rings
  - ancient bindings
  - ghastly arrows
  - keeper spearhead
  - druidic inscriptions
  - hardened debole
  - reinforced morgana pole
  - werewolf remnant
  - runed horn
  - imbued visor
  - imbued leather fold
  - imbued soles
  - wildfire orb
  - possessed scroll
  - lost arcane crystal
  - hoarfrost orb
  - lost cursed crystal
  - alluring crystal
  - druidic preserved beak
  - druidic feathers
  - druidic bindings
- `soul`:
  - burning orb
  - infernal scroll
  - occult orb
  - icicle orb
  - cursed jawbone
  - demonic jawbone
  - infernal cloth visor
  - infernal cloth folds
  - infernal cloth bindings
  - demonic arrowheads
  - infernal harpoon tip
  - symbol of blight
  - broken demonic fang
  - hellish sicklehead spear
  - hellfire imp remnants
  - hellish handle
  - demonhide padding
  - demonhide leather
  - demonhide bindings
  - demonic blade
  - hellish sicklehead
  - infernal mace head
  - hellish hammer head
  - severed demonic horns
  - hellish bolts
  - infernal shield core
  - demonic scraps
  - demonic plates
  - demonic filling
- `relic`:
  - unholy scroll
  - ghastly scroll
  - possessed catalyst
  - cursed frozen crystal
  - bloodforged catalyst
  - inscribed stone
  - alluring padding
  - alluring amulet
  - alluring bindings
  - carved bone
  - carved barbs
  - preserved log
  - ghastly blades
  - preserved rocks
  - runestone golemn remnant
  - ghastly candle
  - ghastly visor
  - ghastly leather
  - ghastly binding
  - cursed blades
  - keeper axehead
  - imbued mace head
  - engraved log
  - warped raven plate
  - alluring bolts
  - bloodforged spikes
  - carved skull padding
  - preserved animal fur
  - inscribed binding
- `avalonian`:
  - glowing harmonic ring
  - messianic curio
  - hypnotic harmonic ring
  - chilled crystalline shard
  - fractured opaque orb
  - severed celestial keepsake
  - sanctified mask
  - sanctified belt
  - sanctified bindings
  - immaculately crafted riser
  - ruined ancestral vamplate
  - uprooted perennial sapling
  - bloodstained antiquities
  - timeworn walking staff
  - dawnbird remnant
  - shattered avalonian memento
  - augured padding
  - augured sash
  - augured fasteners
  - remnant of the old king
  - avalonian battle memoir
  - broken oaths
  - massive mettalic hand
  - damaged avalonian gauntlet
  - humming avalonian whirligig
  - crushed avalonian heirloom
  - exalted visor
  - exalted plating
  - exalted greave

## Backend Flow
### Refresh
Le refresh doit suivre le pipeline déjà utilisé ailleurs:

1. `POST` sur la page.
2. Création d'un `PriceRefreshJob`.
3. `refresh_price_job` passe le job à `running`.
4. Le service de refresh collecte les objets cibles.
5. `AlbionOnlineDataPriceFetcher` interroge AODP.
6. Les prix sont enregistrés en base.
7. Le cache est invalidé.
8. Le job passe à `success` ou `failed`.

Points d'implémentation:

- le refresh doit rester asynchrone;
- le job doit être observable comme les autres pages;
- le refresh ne dépend pas de la ville sélectionnée dans la page, sauf si un futur besoin justifie un filtrage différent.

### Rendering
Le service métier doit produire une structure du type:

- `section_key`
- `section_label`
- `shard_base_price`
- `buy_order_price`
- `rows_by_tier`
- `artifact_rows`
- `current_price`
- `price_state`

Chaque ligne de table doit:

- mapper un artefact à son tier `T6`, `T7`, ou `T8`;
- afficher le prix courant;
- afficher l'état de couleur par rapport au seuil.

### Calculation
Le calcul doit être strictement déterministe:

- récupérer le `sell_price_min` courant;
- déterminer le prix de base du shard correspondant;
- multiplier par `10` pour la ligne de base;
- calculer le seuil `buy_order_price` à partir des taxes et de l'objectif de marge;
- comparer le prix courant au seuil et appliquer la classe visuelle.

## Frontend Flow
Le template `artifact_salvage.html` doit rester proche des pages existantes sur les points suivants:

- header sticky;
- sélecteur de ville en haut;
- bouton `Refresh Price`;
- bannière de suivi du job;
- rendu Bootstrap simple et lisible.

Différences voulues:

- pas de nav secondaire `profitable crafts`;
- pas d'offcanvas de détail;
- 4 tables distinctes au lieu d'une matrice unique;
- chaque table affiche une logique de seuil, pas une marge de craft.

UX de couleur:

- vert pour un prix sous `120%` du `buy_order_price`;
- rouge sinon.

## Authorization And Feature Gates
- Reprendre les mêmes règles d'accès que les autres pages `albion_online`.
- Pas de permission spéciale supplémentaire à introduire.
- Si un feature flag existe plus tard, il doit s'appliquer au routage de la page et au refresh job de manière cohérente.

## Observability And Operations
Le comportement opérationnel doit suivre le standard des pages existantes:

- logs de requête AODP conservés dans le fetcher;
- status du `PriceRefreshJob` visible dans l'UI;
- échec de refresh affiché dans la bannière;
- cache invalidé explicitement après succès.

Points à surveiller:

- volume d'artefacts suivi, pour ne pas dépasser la limite d'URL AODP;
- augmentation du nombre d'objets si les trois familles restantes ajoutent beaucoup d'entrées;
- risque de cache trop granulaire si la page est cachée par ville et par version.

## Edge Cases
- Liste vide pour une famille donnée.
- Artefact sans prix récent dans la ville sélectionnée.
- Artefact présent dans le code mais absent du dump `Object`.
- `sell_price_min` nul ou manquant.
- Tiers incomplets: absence d'un `T6`, `T7` ou `T8`.
- Prix courant exactement égal au seuil.
- Prix courant entre le seuil et `120%` du seuil.
- Job de refresh déjà en cours quand un second clic arrive.
- Artefacts non encore fournis pour `soul`, `relic`, `avalonian`.

## Testing Strategy
### Service tests
- calcul du `buy_order_price`;
- classification couleur;
- extraction des objets suivis depuis les constantes;
- construction des lignes par famille et par tier;
- comportement sur valeurs manquantes.

### View tests
- rendu de la page avec une ville valide;
- invalidation du filtre ville;
- POST de refresh;
- bannière de job;
- redirection et conservation du query string si nécessaire.

### Task tests
- nouveau `PriceRefreshJob.kind`;
- exécution du refresh;
- invalidation du cache après succès;
- propagation des erreurs en cas d'échec.

### Template / integration tests
- présence des 4 sections;
- présence du sélecteur de ville;
- présence du bouton `Refresh Price`;
- rendu des classes de couleur.

## Rollout And Migration
Ordre de livraison recommandé:

1. Ajouter les constantes d'artefacts et les tests de résolution.
2. Ajouter le service de calcul et les tests de seuil.
3. Ajouter le kind `PriceRefreshJob.ARTIFACT_SALVAGE` et la tâche de refresh.
4. Ajouter la vue, la route et le template.
5. Brancher le lien depuis l'accueil et le header si souhaité.
6. Générer la migration de state liée au nouveau kind si Django la produit.

Compatibilité:

- la nouvelle page ne doit pas casser les routes existantes;
- les caches des autres pages doivent rester isolés;
- le rollback fonctionnel doit consister à retirer la route et le kind sans migration de données complexe.

## Files Expected To Change
- `/home/louis/Custom_projects/bricolle-family/albion_online/urls.py`
- `/home/louis/Custom_projects/bricolle-family/albion_online/models/price_refresh_job.py`
- `/home/louis/Custom_projects/bricolle-family/albion_online/tasks.py`
- `/home/louis/Custom_projects/bricolle-family/albion_online/views/artifact_salvage.py` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/services/artifact_salvage_price_refresh.py` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/services/artifact_salvage_market_summary.py` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/constants/artifact_salvage.py` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/templates/albion_online/artifact_salvage.html` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/templates/albion_online/header.html`
- `/home/louis/Custom_projects/bricolle-family/albion_online/templates/albion_online/home.html`
- `/home/louis/Custom_projects/bricolle-family/albion_online/tests/test_artifact_salvage_view.py` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/tests/test_artifact_salvage_service.py` new
- `/home/louis/Custom_projects/bricolle-family/albion_online/tests/test_price_refresh_task.py`
- `/home/louis/Custom_projects/bricolle-family/albion_online/migrations/00xx_*` tentative for the `PriceRefreshJob` choice update
