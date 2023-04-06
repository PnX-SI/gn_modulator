# Import


## Introduction et principes

Dans le cadre de ce module, nous avons implémenter des fonctionalité d'import à destination (théoriquement) de n'importe quelle table de la base.

Les étapes de la procédure d'import sont illustrés par des exemple, où l'on détaille le code sql produit pour chaque étape.

- [Exemle simple (ref_geo.l_areas)](/gn_modulator/backend/gn_modulator/tests/import_test/ref_geo.area.csv.log.sql)
- [Exemle avancé (gn_synthese.synthese)](/gn_modulator/backend/gn_modulator/tests/import_test/synthese_obs.csv.log.sql)

### L'unicité

Une condition essentielle au bon déroulement de l'import est de pouvoir définir, pour toutes les tables concernées par l'import, un ou plusieurs champs qui cont permettre d'assurer la continuité d'une ligne. Cela peut être
- un code
- un uuid, lorsque celui ci est fourni dans les données et non généré par l'application
- une combinaison de type et de code (pour le ref_geo ou la nomenclature)

Cela permet

- de résoudre la clé primaire lorsque les champs d'unicité sont présent dans les données

- de résoudre les clés étrangère, qui sont renseigner sous forme de code (ou de combinaison de valeurs s'il y a plusieurs champs d'unicité pour la tablé associée à la clé étrangère)

Pour une ligne du fichier à importer on peux être dans deux cas

- la clé primaire ne peux pas être résolue, il n'y a pas de ligne correspondante dans la table. Il s'agit d'une nouvelle données et on va faire un `INSERT` pour ces lignes

- la clé primaire peut être résolue, il existe déjà une ligne correspondant à cette données. On a la possibilité de faire un `UPDATE` pour ces lignes
## Les étapes

### 1) Chargement, pré-traitement et verification des données
#### 1.1) Chargement des données

Chargement du fichier de données dans une table `gn_modulator_import.t_<id_import_data>`
  - Toutes les colonnes sont de type `VARCHAR`
  - On passe tous les champs de valeur `''` à `NULL`
  - La première ligne donne le nom des colonnes
  - seulement pour les fichiers csv, à voir si l'on prévoit d'autres formats

On rajoute un champs `id_import` (clé primaire, `SERIAL`) afin de pouvoir numéroter les lignes du fichier d'import et pouvoir associer les erreurs aux lignes.
#### 1.2) Mapping (optionnel)

Creation du vue de mapping pour réorganiser les colonnes de la table de données à partir d'une instruction select `SELECT`


#### 1.3) Vérification 

##### Typage des données

On verifie pour chaque colonnes (sauf clé étrangères) que les données des colonnes  vont bien pouvoir être convertie dans le type de la colonne destinataire.

##### Présence des champs pour l'unicité

Les champs d'unicité permette de résoudre la clé primaire et de voir si la ligne est présente en base.
On vérifie que ces clé sont bien présente dans les données à ce stade (pour la vue de mapping si elle existe ou table de données sinon).


#### 1.4) Vue brute (`raw`)

La table de départ est la de mapping si elle existe, ou de la table de donnée

Cette étape permet de
- ne selectionner que les colonnes concernées par la table destinataire
- donner le bon typage aux colonnes (sauf pour les clé étrangères)
- assossier les champs d'unicite dans la colonne associée à la clé primaire


#### 1.5) Vue process

En partant de la vue brute, on cherche à résoudre les clé étrangère
La vue process est prête à être intégrée telle quelle dans la table destinataire elle possède les bonnes id

#### 1.6) Vérification des données

##### Champs Obligatoires

Dans la table `raw`, on fait remonter les lignes qui possède des valeurs nulles pour des colones obligatoires.

##### Résolution des clé étrangères
Dans la table `process` il y a une clé étrangère à `NULL` aors qu'elle est non nulles dans la table `raw`.

### 2) Insertion et mise à jour des données


#### 2.1) Insertion

On insère dans la table destinataire les lignes de la table process pour lequelles la colonne corespondant à la clé primaire est nulle.


### 2.2) Mise à jour des données (optionnel)

On met à jour les ligne sde la table destinataire qui correspondent aux lignes de la table process
- pour lequelles la colonne corespondant à la clé primaire est nulle.
- et où une au moins des colonnes est différente de celle de la ligne destinataire

### 2.3) Traitement des relations n-n

- Effacement de toutes les lignes concernées
- Insert des lignes selon les données

### 3) Log des commandes d'importd

Le modèle d'import contient deux objects pour stocker les commandes sql

- `tables`: pour retrouver les différente tables et vues créées pour l'import.
- `sql`: pour les requêtes utilisée pour l'import

### 3.1) tables

- `data`: table contenant les données

### 3.2)  requêtes sql

- `data_table`: creation de la table contenant les données