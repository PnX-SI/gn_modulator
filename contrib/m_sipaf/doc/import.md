# Import de passages faune

## Définition des champs

[Définition des champs](./import_passage_faune_description_champs.md)

Le champs `uuid_passage_faune` permet d'identifier de maniere unique un passage à faune.  
La colonne `uuid_passage_faune` doit être présente dans le fichier d'import même si les valeurs ne sont pas renseignées.

Si la valeur est nulle, une valeur sera générée par défaut. Cependant il sera plus difficile de faire le lien avec la base de donnée source, ou de faire des mises à jour de ces données (en utilisant la fonctionalité de mise à jour lors d'un import).

Il est donc conseillé de fournir une valeur pour ce champs.

Pour les champs avec des relations multiples (un PAF peut avoir plusieurs acteurs, un PAF peut avoir plusieurs usages), il est possible d'importer ces informations. Pour cela, il faut dupliquer les lignes des PAF concernés en modifiant uniquement ce champs. Par exemple, si un PAF a 2 acteurs, alors ce PAF sera présent 2 fois dans le fichier importé avec un acteur différent à chacune des 2 lignes.

## Exemples de fichiers

- [Exemple simple](/backend/gn_modulator/tests/import_test/pf_simple.csv)
- [Exemple complet](/backend/gn_modulator/tests/import_test/pf_complet.csv)

## Procédure d'import depuis l'interface web

### Accès à l'outil d'import

Si l'utilisateur possède des permissions de création pour ce module, alors le bouton d'import est visible.

![Bouton d'import](img/boutton_import.png)

L'outil d'import apparait dans une fenêtre modale.

![Menu d'import](img/menu_import.png)

### Chargement du fichier

- Appuyer sur le bouton `Charger un fichier`.
- Selectionner un fichier CSV
- Appuyer sur `Valider` pour charger le fichier.

### Vérification

![Validation de l'import](img/validation_import.png)

- Une fois le fichier chargé, des informations sont affichées pour voir :

  - le nombre de données (lignes) du fichier
  - le nombre de lignes à ajouter
  - le nombre de ligne existantes (et éventuellement à modifier)

### Insertion des données

- Appuyer sur `Valider` pour insérer les données
- Un message de confirmation est affiché pour préciser le nombre de lignes ajoutées / modifiées

![Validation de l'import](img/fin_import.png)

- Appuyer sur le bouton `Nouvel import` pour procéder à un nouvel import
- Apputer sur `Annuler` ou cliquer en dehors de la fenêtre modale pour sortir de l'import et reprendre la navigation.

### Erreurs

En cas d'erreur(s), un message est affiché et il faut aller dans l'onglet `Erreurs` pour voir les détails.

Il faudra revoir et corriger les données pour pouvoir reprocéder à l'import.

![Validation de l'import](img/erreur_import.png)

### Options additionnelles

- `Verifier avant insertion`
  - décocher pour passer à l'étape de vérification des données et ne plus avoir à valider une fois le fichier chargé
- `Autoriser les mises à jour`
  - par défaut les mises à jour ne sont pas autorisées
  - appuyer sur cette case pour pouvoir mettre à jour des données à partir de leur UUID
- `SRID`
  - par défaut le SRID (système de projection des coordonnées) est `4326`
    - vous pouvez préciser un SRID différent pour le fichier
