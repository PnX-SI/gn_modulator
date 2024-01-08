# Changelog


## 1.3.1 (unreleased)

## 1.3.0 (2024-01-08)

**🚀 Nouveautés**

- [FRONTEND-MAP] Possibilité de désactiver des couches par défaut dans les contrôles (par exemple pour les PK et PR de SIPAF)
- [FRONTEND-MAP] Possibilité de désactiver des couches additionnelles définies dans la configuration globale de GeoNature (#64)
- [FRONTEND-MAP] Affichage plus fluide lors du chargement des données lors de l'ouverture d'une popup
- [FRONTEND-MAP] Ajout du composant Nominatim sur les cartes, permettant de rechercher un lieu et de se centrer dessus
- [FRONTEND-MAP] Conservation du zoom de la carte de la page de recherche quand on créé un nouvel objet (#63)
- [FRONTEND-MAP] Affichage des petits polygones et lignes sous forme de point à large échelle pour en améliorer la visibilité (#65)
- [SIPAF-EXPORT] ajout des champs acteurs, objectifs et usages
- [SIPAF-EXPORT] possibilité de voir le select de l'export (aide pour faire une vue à destination du module Export)
- [SIPAF] Ajout d'un exemple de vue d'export (https://github.com/PnX-SI/gn_modulator/blob/develop/contrib/m_sipaf/config/exports/m_sipaf.pf.export.sql)
- [SIPAF-MAP] Ajout des pk/pr sur toutes les cartes, en les désactivant par défaut
- [SIPAF] Suppression de la possibilité de mettre une personne en tant qu'acteur des PAF, pour se limiter aux organismes
- [SIPAF] Suppression des "Espèces ciblées" au niveau des objectifs des PAF
- [SIPAF] Champs "Usages" désactivé quand le PAF est de type spécifique (#66)
- [SIPAF] Intégration des voies navigables métropolitaines à partir de la BD TOPO de l'IGN
- [SIPAF] Ajout d'un filtre des PAF possédant un diagnostic
- [SIPAF] Ne pas afficher les observateurs dans la liste des observations autour d'un PAF
- [SIPAF] Application des permissions de la Synthèse (portée et sensibilité) quand on récupère la liste des observations autour d'un PAF
- [SIPAF] Application des portées des permissions sur les diagnostics
- [IMPORT] Gestion des relations multiples pour les acteurs ou les usages des PAF par exemple (#58)
- [IMPORT] Exécution des taches en asynchrone avec Celery
- Améliorations, nettoyage et corrections diverses du code source
- Améliorations et compléments des tests automatisés
- Ajout d'un script permettant de traiter les extractions INPN (https://github.com/PnX-SI/gn_modulator/blob/develop/contrib/m_sipaf/data/scripts/process_inpn.sh)

**🐛 Corrections**

- Correction du filtrage des objets sur la carte qui ne prenaient pas en compte les filtres appliqués
- Correction de la mise à jour des géométries de type Polygone

## 1.2.1 (2023-10-12)

**🐛 Corrections**

- [FRONTEND] Correction du compteur de nombre d'éléments dans les listes déroulantes quand celles-ci sont filtrées par une recherche textuelle
- [FRONTEND] Correction de la gestion des colonnes des tableaux
- [FRONTEND] Correction du fichier `frontend/package-lock.json` qui n'était pas à jour avec le fichier `package.json`

## 1.2.0 (2023-10-09)

Nécessite la version 2.13.1 (ou plus) de GeoNature.

**🚀 Nouveautés**

- [SIPAF] Suppression du champs `code_passage_faune` au profit des UUID (#50)
- [SIPAF] Ajout des objectifs et usages dans la base de données, les formulaires et fiches des PAF (#53)
- [SIPAF] Ajout des observations de biodiversité présentes dans la Synthèse à proximité des PAF, dans leurs fiches de détail (#42)
- [SIPAF] Affichage des diagnostics fonctionnels dans les fiches détails des PAF (#37)
- Filtres géographiques : gestion dynamique des routes et des zonages
- Intégration des routes départementales, des voies ferrées et des points de repères, à partir de la BD TOPO de l'IGN
- Possibilité de filtrer sur une bounding box (par exemple emprise de la carte Leaflet)
- Meilleure gestion des champs au format "jsonb"
- Composant `select` : affichage du nombre de données (total, filtré)

**🐛 Corrections**

- Inversion `lat`, `lon` dans les propriétés des PAF
- Carte-liste : correction de la surbrillance d'une ligne de la liste quand on ligne du tableau qui ne se mettait plus en surbrillance avec un click sur la carte
- Corrections et améliorations diverses (voir #54)

**⚠️ Notes de version**

- Mettez à jour le module Modulator avec la procédure classique
- Pour mettre à jour le sous-module SIPAF :
  - lancez les mises à jour de la BDD
    ```
    geonature db autoupgrade
    geonature db status
    ```
  - mettez à jour les données et nomenclatures
    ```
    geonature modulator features m_sipaf.utils
    ```
  - Mettez à jour le référentiel géographique des routes, voies ferrées et points de repère en suivant la documentation dédiée (`contrib/m_sipaf/doc/maj-bd_topo-sipaf_1.2.0.md`)

## 1.1.1 (2023-06-29)

**🐛 Corrections**

- Correction des exports
- Suppression de l'export de test "Export import"
- Correction des tooltips des boutons
- Amélioration de la liste du filtre des infrastructures
- Correction des permissions de suppression d'un objet, s'appuyant sur l'action D du sous-module
- Retrait du bouton de suppression sur les tooltips des cartes
- Correction de l'affichage des imports en frontend
- Import:
  - fichier csv: passage des valeurs caractère vide ('') à NULL
  - frontend: correction affichage erreur

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
