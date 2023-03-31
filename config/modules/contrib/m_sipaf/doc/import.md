# Impot de passage faune

## Définition des champs

[Définition des champs](./import_description_champs.md)

## Exemples de fichiers

- [Exemple simple](/backend/gn_modulator/tests/import_test/pf_simple.csv)
- [Exemple complet](/backend/gn_modulator/tests/import_test/pf_complet.csv)
## Procédure d'import sur l'interface web

### Accès au menu d'import

Si l'utilisateur possède des droits de création pour ce module, alors le bouttons d'import est visible.

![Boutton d'import](img/boutton_import.png)

Le menu d'import apparait dans une fenêtre modale

![Menu d'import](img/menu_import.png)

### Chargement du fichier

- Appuyer le boutton `Charger un fichier`.
- Selectionner un fichier csv
- Appuyer sur valider pour charger le fichier.

### Vérification

![Validation de l'import](img/validation_import.png)

- Une fois le fichier chargé, des information sont affichées pour voir

  - le nombre de données (lignes) du fichier
  - le nombre de lignes à ajouter
  - le nombre de ligne existantes (et éventuellement à modifier)

### Insertion des données

- Appuyer sur valider pour insérer les données
- Un message de confirmation est affiché pour préciser le nombre de lignes ajoutées / modifiées

![Validation de l'import](img/fin_import.png)

- Appuyer sur le boutton `nouvel import` pour procéder à un nouvel import
- Apputer sur `Annuler` ou cliquer en dehors de la fenêtre modale pour sortir reprendre la navigation.
### Erreurs

En cas d'erreur(s), un message est affiché et il faut aller dans l'onglet `Erreurs` pour voir les détails.

Il faudra revoir et corriger les données pour pouvoir reprocéder à l'import.

![Validation de l'import](img/erreur_import.png)

### Options additionelles

- Appuyer sur la case `Afficher les options avancées`
- `Verifier avant insertion`
  - décocher pour passer l'étape de vérification des données et ne plus avoir à valider une fois le fichier chargé
- `Autoriser les mises à jour`
  - par défaut les mise à jour ne sont pas autorisé
  - appuyer sur cette case pour pouvoir mettre à jour des données
- `SRID`
  - par défaut le srid est `4326`
    - vous pouvez préciser un srid différent pour le fichier