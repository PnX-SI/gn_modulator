# Changelog

## 1.1.1 (unreleased)

**🐛 Corrections**

- 

## 1.1.0 (2023-06-27)

Nécessite la version 2.13.0 (ou plus) de GeoNature.

**🚀 Nouveautés**

- Ajout de fonctionalités d'import depuis des fichiers CSV (commande + interface frontend) (#25)
- Compatibilité avec GeoNature 2.13.0 et la refonte des permissions, en définissant les permissions disponibles du module (#232)
- Possibilité pour chaque sous-module de déclarer ses permissions disponibles
- [SIPAF] Ajout d'un onglet et du formulaire des diagnostics fonctionnels (#37)

**✨ Améliorations**

- Clarification dans la gestion des routes REST
- Meilleure gestion des `tabs` et des `scrolls` (#32)
- Sécurisation des API (contrôle des `fields` en lecture et écriture) (#29)
  - champs listés à partir de la config
  - écriture : si un champs demandé n'est pas dans la config -> erreur 403
  - lecture : ce champs n'est pas pris en compte (utilisation de `only` dans l'initialisation des champs marshmallow)
- Requêtes SQL (fonction `query_list`)
    - chargement des relations et des champs pour les requêtes
    - pour éviter les chargements n+1 (1 requête supplémentaire par relation)
    - utilisation de `raise_load`
    - on charge le minimum de champs possibles
- Déplacement des configurations dans le dossier `media/modulator/config` de GeoNature
- Changement de nom `ownership` -> `scope`
- Amélioration du composant list_form

**🐛 Corrections**

- Correction des formulaires dans les onglets (#38)

**⚠️ Notes de version**

Si vous mettez à jour le module :

- Mettre à jour le module SIPAF
  ```
  geonature modulator install m_sipaf
  ```
  - Cette commande va effectuer les actions suivantes :
    - créer le dossier `<GN>/backend/media/modulator`
    - déplacer la config du sous-module dans le dossier `<GN>/backend/media/modulator/config`
    - mettre à jour les `features` du module et notamment :
      - ajouter des nomenclatures pour les permissions
      - corriger de nomenclatures pour les passages à faune
      - ajouter des permissions disponibles pour le module

## 1.0.5 (13-03-2023)

**✨ Améliorations**

- Historisation de la table `pr_sipaf.t_passages_faune` et ajout des champs `meta_create_date` et `meta_update_date` (#27)
- Amélioration des noms des fichiers exportés (#26)
- Gestion plus classique des versions Alembic des sous-modules (modules python avec `setup.py` et non plus avec des copies/liens symboliques vers les fichiers de migration)

**⚠️ Notes de version**

Si vous mettez à jour le module :

- Exécutez la commande `geonature modulator update`, pour installer les sous-modules en tant que module python lorsque cela est nécessaire
- Exécutez la commande `geonature db autoupgrade`, pour mettre à jour la BDD.

## 1.0.4 (03-03-2023)

**🐛 Corrections**

- Corrige un bug sur le composant de filtrage

## 1.0.3 (03-03-2023)

**🐛 Corrections**

- Composant de filtre : prise en compte des filtres quand la valeur est `false`
- SIPAF : Correction des filtres par infrastructure
- Ajout des champs par défaut (dont `ownership`) et correction des droits dans les listes

**✨ Améliorations**

- Amélioration de l'affichage des tableaux dans le composant "tabs"
- Import : amélioration des fonctionnalités d'import
- NavBar : affichage du nom du sous-module (à la place de 'MODULATOR')

## 1.0.2 (17-02-2023)

**🐛 Corrections**

- Ajout des méthodes de serialisation `utils_flask_sqla.serializers.serializable` aux modèles autogénérés (pour éviter un bug dans la gestion des permissions)

## 1.0.1 (16-02-2023)

**✨ Améliorations**

- Listes des objets : adaptation automatique du nombre d'objets demandées (`page_size`) en fonction de la hauteur du composant (pour éviter les zones vides)

**🐛 Corrections**

- SIPAF : Correction de l'import du référentiel de linéaires (routes, autoroutes)

## 1.0.0 (16-02-2023)

Première version fonctionnelle du module MODULATOR.
Elle inclut une documentation pour créer ses propres sous-modules, mais aussi 2 sous-modules d'exemple (SIPAF pour l'inventaire national des passages à faune et MONITORING pour le gestionnaire de sites).

Compatible avec la version 2.11 de GeoNature.
