# Albion Online Architecture

## Objectif

Cette app Django regroupera les fonctionnalités liées à Albion Online dans la catégorie `game`.

## Structure actuelle

- `albion_online/urls.py`: routes publiques de l'app.
- `albion_online/views/`: contrôleurs Django. Les vues doivent rester fines.
- `albion_online/services/`: logique métier, organisée en classes avec une API publique réduite.
- `albion_online/models/`: modèles Django. Chaque modèle devra être enregistré dans l'admin depuis son module.
- `albion_online/constants/`: enums et constantes métier.
- `albion_online/templates/albion_online/`: templates Bootstrap de l'app.
- `albion_online/tests/`: tests pytest, en priorité sur les services.

## Modèles

### Object

Représente un item Albion Online importé depuis le dump AODP.

- `aodp_id`: identifiant officiel utilisé pour les prix.
- `name`: libellé du dump quand il existe.
- `tier`: tier `1..8`, ou `NULL` pour les objets non tierés comme `UNIQUE_HIDEOUT`.
- `enchantment`: enchantement `0..4`, avec `0` quand l'ID n'a pas de suffixe `@N`.
- `tier_enchantment_notation`: notation persistée `X.Y`, par exemple `5.1`.
- `equipment_category`: catégorie nullable pour les objets équipables (`CHEST`, `OFFHAND`, `SINGLE_HAND`, `TWO_HAND`, `SHOE`).
- `crafting_tree`: arbre de craft nullable, utilisé pour regrouper les objets fabriqués dans une même branche.
- `type`: FK vers une table de référence `ObjectTypeGroup` qui porte le code métier et le `resource_return_rate_city`.

Mapping actuel de `equipment_category`:

- `ARMOR` -> `CHEST`
- `OFF` -> `OFFHAND`
- `MAIN` -> `SINGLE_HAND`
- `2H` -> `TWO_HAND`
- `SHOES` -> `SHOE`

Règles actuelles de `crafting_tree`:

- Armures classiques: combinaison matière + slot, par exemple `cloth_head`, `leather_chest`, `metal_shoe`.
- Armures gatherer: combinaison `gatherer_<resource>_<slot>`, par exemple `gatherer_fiber_head`.
- Armes: famille Albion déduite de l'ID AODP, par exemple `axe`, `bow`, `nature_staff`, `cursed_staff`.
- Offhands: famille déduite de l'ID AODP, par exemple `shield`, `book`, `orb`, `torch`.
- Les objets non reconnus ou non craftables restent `NULL`.

### Price

Représente un prix de marché observé pour un objet.

- `sell_price_min`: prix de vente minimum observé, utilisé comme prix par défaut dans l'app.
- `sell_price_min_date`: date et heure de l'observation du `sell_price_min`.
- `sell_price_max`: prix de vente maximum observé.
- `sell_price_max_date`: date et heure de l'observation du `sell_price_max`.
- `buy_price_min`: prix d'achat minimum observé.
- `buy_price_min_date`: date et heure de l'observation du `buy_price_min`.
- `buy_price_max`: prix d'achat maximum observé, utilisé comme prix d'achat par défaut dans l'app.
- `buy_price_max_date`: date et heure de l'observation du `buy_price_max`.
- `city`: ville Albion parmi les villes principales supportées.
- `object`: objet Albion concerné.
- `quality`: qualité `0..4`.

### ObjectTypeGroup

Représente une famille d'objets référencée par `Object.type`.

- `code`: code métier stable, réutilisé comme identifiant de la FK.
- `name`: libellé lisible dans l'admin.
- `resource_return_rate_city`: ville optionnelle où tous les objets de ce type bénéficient du `resource return rate` élevé.

### RecipeDefinition

Représente une règle de génération de recipes.

- `key`: identifiant stable de la règle.
- `name`: libellé lisible dans l'admin et la page `settings`.
- `config`: configuration JSON de génération, incluant les filtres d'output et les règles d'inputs.
- `is_active`: permet d'activer ou désactiver une définition sans la supprimer.

## Récupération des prix

`AlbionOnlineDataPriceFetcher` utilise uniquement le serveur Europe:

`https://europe.albion-online-data.com`

Endpoint courant:

`/api/v2/stats/prices/{item_ids}.json`

Règles actuelles:

- Les filtres `locations` et `qualities` sont optionnels.
- Les lignes avec ville inconnue, qualité invalide ou date de vente minimum nulle sont ignorées.
- L'API renvoie les qualités `1..5`; elles sont converties en interne en `0..4`.
- Les requêtes sont découpées pour rester sous la limite d'URL de 4096 caractères documentée par Albion Online Data.
- Le front affiche seulement les tiers `4+` par défaut.
- Le front masque par défaut `sell_price_max` et `buy_price_min`; les valeurs de référence affichées sont `sell_price_min` et `buy_price_max`.
- Le front remplace les dates brutes de prix par un indicateur de fiabilité: vert si l'info a moins d'1 heure, orange si elle a plus d'1 heure, rouge si elle a plus d'1 jour.
- La table principale Mercenary Jacket compresse les gros montants avec `k`, `M` et `B`, avec une décimale seulement quand nécessaire.
- La table principale Mercenary Jacket affiche la marge de craft en montant compact et en pourcentage de coût de craft.
- Le calcul de marge applique une fee de trade de 2%: les inputs sont majorés de 2% et le prix de vente net est minoré de 2%.
- Sur la page Mercenary Jacket, si un prix utilisé dans le calcul a plus d'1 jour, la donnée est masquée au lieu d'être affichée.
- Le front affiche les prix par ville séparément et calcule une moyenne par ville sur les qualités `0`, `1` et `2` uniquement.
- Le refresh de prix récupère aussi les objets d'input des recipes des objets suivis pour permettre le calcul du coût de craft.
- Le refresh de prix effectue maintenant une seconde requête dédiée au leather (`T4.0` à `T8.4`) pour alimenter le calcul du coût de craft.
- Le front affiche désormais la marge de craft par ville: `sell_price` moyen moins le coût de craft basé sur les inputs du recipe.
- Le coût de craft applique un `resource return rate` sur les inputs de type ressource avant la fee de trade: `15.3%` par défaut, `36.7%` dans la ville spécialisée.
- Le `resource return rate` est porté par le type d'objet produit via `Object.type.resource_return_rate_city`, ce qui permet de spécialiser une ville sans changer la formule de craft.

### Recipe

Représente une recette instanciée pour un output précis.

- `output`: objet produit par la recette.
- `output_quantity`: quantité produite, par défaut `1`.
- Une contrainte garantit une seule recette par output.
- `definition`: définition de génération à l'origine de la recette, nullable pour conserver la compatibilité avec les recettes historiques.

### RecipeInput

Représente un ingrédient d'une recette.

- `recipe`: recette concernée.
- `object`: objet consommé.
- `quantity`: quantité consommée.
- Une contrainte garantit qu'un même objet input n'apparait qu'une fois par recette.

Exemple: pour une Mercenary Jacket `5.1`, la recette peut contenir un input `16 x T5_LEATHER_LEVEL1@1` et un output `1 x T5_ARMOR_LEATHER_SET1@1`.

### Génération des recipes

`RecipeGenerationService` reconstruit les recipes à partir des `RecipeDefinition`.

- Le service supprime les recipes dont les outputs sont couverts par une definition.
- Il régénère ensuite les `Recipe` et `RecipeInput` à partir de la configuration.
- La page `settings` sert de point d'entrée manuel pour relancer cette génération.
- Une première definition active est seedée pour les mercenary jackets.

## Import des objets

La migration `0002_import_objects_from_aodp_dump` importe le dump officiel:

`https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/formatted/items.txt`

Règles de parsing actuelles:

- Format de ligne: `<index>: <aodp_id> : <name>`.
- Tier: préfixe `T1_` à `T8_`.
- Enchantement: suffixe `@0` à `@4`; absent signifie `0`.
- Type: premier segment de l'ID après retrait du préfixe tier et du suffixe enchantement.

## Routes

- `/albion_online/`: page d'accueil de l'app.
- `/albion_online/settings/`: page de régénération des recipes.

## Conventions d'évolution

- Ajouter les décisions métier et les flux principaux dans ce fichier au moment où ils sont implémentés.
- Ne pas créer de modèle sans admin associé dans le même module.
- Ne pas modifier une migration existante; créer une nouvelle migration via `make migrations`.
- Placer la logique métier dans un service avant de l'appeler depuis une vue.
