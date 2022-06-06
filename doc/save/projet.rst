# Projet

## Introduction 

cf https://github.com/PnX-SI/gn_module_monitoring/issues/96

Le but de ce projet est de pouvoir créer des modules de la façon la plus générique possible.

Contrairement au module monitoring, les données seront stockée dans des champs dédiés et non regroupée dans un champs en jsonb.

Une configuration est définie et permet de 
- créer les schémas et tables nécessaires en base
- créer dynamiquement les modèles sqla, ainsi que les api rest
- dans un premier temps frontend succint qui permettra de tester les configuration ainsi que les différentes routes et de s'assurer de la fonctionnalité de la partie SQL et Backend (tableau server side, formulaires, composants autocomplete, création / edition / suppression)

l'accent sera porté sur la partie backend et base de donnés dasn un premier temps. 
Dans un second temps, on pourras imaginer de développer des briques de base pour le frontend (tableaux, cartes, propriétés, ), qui pourront ensuite être utilisée pour des frontend dédiés (programmés ou définis par une config)


## Configuration 

Le standart utilisé pour la configuration pourra être json schema, à voir comment les organiser pour les différents type de besoin : SQL (types, contraintes), modeles (Backend) (type, contraintes?), formulaire (Frontend, Backend) (type, contraintes et dispositions)

## Plan d'action

La validation des étapes 1 et 2 devrait assurer la pérénité du projet.
### Préalable

- documentation sur jsonschema
  - definition
  - validation
  - formulaire frontend
- documentation alembic
- documentation CI

### étape 1 : sous-module avec un seul objet simple : *pas de relation, on se limite au type texte*

- [ ] **configuration**
    - [ ] organisation de la configuration en fichiers .json (module, sous-modules, objets)
- [ ] **SQL** 
  - [ ] commande flask / geonature pour générer / supprimer le schéma du sous module + table de l'objet
  - [ ] cette commande ne fait rien si la table existe 
- [ ] **Backend**
  - [ ] config
  - [ ] fonctionalité pour lire / valider la config
  - [ ] API config
  - [ ] modèle dynamique
  - [ ] API REST generique
    - [ ] validation (POST PATCH) avec jsonschema / marshmallow ??
    - [ ] api GET pour les liste avec filtre tri server side, etc.. 
    - [ ] inspiré des routes generique de l'oeasc ?
    - [ ] module python api rest jsonschema existant ? 
    - [ ] essayer d'introduire les test dès la première étape
- [ ] **Frontend**
  - [ ] angular
  - [ ] simple / efficace / rapide, pour répondre à des besoins de tests
  - [ ] tableau pour tester les api liste tri filtre server side
  - [ ] formulaire jsonschema
    - [ ] disposition
    - [ ] contraintes / validation
    - [ ] test composant liste
    - [ ] statiques (liste en dur)
    - [ ] depuis une api
    - [ ] dynamique (autocomplete)
  - [ ] test CRUD



#### Questions ???
- *Utilisation de sqlalchemy pour créer les table ou génération de script sql ?*
  - les + : on a juste  à gérer le modèle
  - les - : 
    - on ne maîtrise pas le sql
    - peut ne pas être compatible avec alembic ?

- *api / routes generiques faire ou utiliser une librairie ?*  

- *comment gérer les test, idéalement en CI, important de le faire dès la première étape*

### étape 2 : relationships : faire des objets liés par des relation 1-n, n-n  
- **configuration**: 
    - [ ] notions de parent - child autre ??
    - [ ] variable `tree` (cf monitoring)
    - [ ] attributs de type objets, tableau d'objets
- **SQL**:
    - [ ] ajout des contrainte de clé étrangères
    - [ ] gestion des tables de corrélation
- **Backend**:
    - [ ] modèles dynamiques plus complexes
    - [ ] api GET pour les listes peut prendre en compte des relations (pour filtrer trier donner les champs de sortie)
    - [ ] validation par les schema 
- **Frontend**:
    - [ ] relations dans les formulaire (création d'un nouvel objet enfant ou choix dans une liste) 
    - [ ] page avec propriété et tableau d'objets enfants
    - [ ] navigation / breadcrump
  
### étape 3 : utiliser les tables / modèle existants

*par exemple pour pouvoir utiliser les éléments des référentiels (nomenclature, metadonnée, geo, utilisateur, taxon, habitat, etc...)
- **configuration**
    - [ ] besoin de créer une configuration
    - [ ] préciser que l'édition de ces tables est impossible
    - [ ] possibilité d'ajout d'éléments spécifiques au sous module (par exemple listes de nomenclature spécifique dédiées au sous module nomenclature (cf monitoring), listes de taxons, etc..)
- **SQL**
    - [ ] gestion des contraintes de clé étrangères pour les objets
- **Backend**
    - [ ] api generique depuis modele ou api dédiés existants ?

### étape 4 : gestion des version du module / des sous-modules / pour la bdd et l'applicatif
- **configuration**:
  - pouvoir stocker la version du sous module, la version requise du module, de gn (fourchette)
- **SQL**
  - [ ] Utilisation d'alembic, pour créer / mettre à jour (surement plus difficile) les schema de gn_modules / des sous modules
- **backend** :
  - [ ] test compatibilité en versions GN / gn_modules / sous-module

### étape 5 : pouvoir créer un module et gérer la configuration depuis le navigateur (mode admin)
- **configuration** :
    - [ ] config en base ?? vs config en fichiers (préférence)
  - **backend** :
    - [ ] fonctionalité d'analyse de la configuration
    - [ ] API config qui renvoie les erreurs dans les fichiers json
    - [ ] API pour pouvoir créer / modifier / supprimer un module (existe déjà de part les routes génériques)
    - [ ] API pour pouvoir créer / modifier / supprimer les config
   - **frontend** :
     - [ ] message d'erreur qui signale les erreurs de fichier config
     - [ ] page d'administration et d'édition de la config
     - [ ] message d'avertissement / à valider si le changement de config implique des changements importants en base

### étape 6 : affinage (peut être fait avant)
gestion du plus grand nombre possible de type de champs : uuid, nombres, date, heure, textes longs, geom  etcs.     
  - **configuration**
    - voir l'existant avec jsonschema et comment compléter s'il y a des manques
    - voir aussi pour les propriété hybrides et/ou column properties (par exemple nombre d'enfant ou dernière visite d'un site)
    - gestion des geometries
  - **SQL**
    - compléter la génération des scripts
  - **Backend** 
    - gestion des modèles
  - **Frontend** 
    - etendre les composants des formulaire
    - saisie sur carte
    - affichage sur carte (comment gérer le server side ?? afficher un grand nombre de données à faible cou ? WMS, cluster)

#### Question 
*column_properties en backend ou colonne matérialisée en sql ???*

### étape 7 : gestion fine des droit cruved et des données accessibles par l'api générique

rejoint la discussion lancée dans monitoring
comment gérer ces question en partant de la config question ouverte mais essentielle
gestion par object au sens des permission et des objets definis dans la configuation (cf monitoring avec la possibilité de définir des droits pour les SITES, VISITES)

### étape 8 : composants de base frontend

un frontend generique repondant à tout les besoin semble assez difficikle à réaliser, par contre créer une base de brique de base qui serait facilement réutilisable pour créer  

créer une librairie de composants de base pour le frontend pour pouvoir être réutilisés et réagencés peut être par contre une bonne base pour créer facilement le frontend des sous modules

propriete, tableau, cartes, graphiques, breadcrumbs, formulaire, etc...

### étape 9 : import / export

### étapes + : 

#### affiner les test

test backend, front, etc...

#### Les templates

pouvoir des définir template, définissant un certain nombre d'éléments qui peuvent être ensuite repris et complété par d'autre sous-modules qui héritent de ce template, et qui peuvent partager des données en communs
(*ceci permettrai par exemple de pouvoir recréer le fonctionnement du module monitoring, ou les modules partagent le meme cadre (comme les table site, visite, observation), et peuvent compléter ces objets avec un configuration simple*)

#### Application mobile

il peut être bon de refléchir en amont à la possibilité de pouvoir consulter / éditer un sous module depuis une application mobile

besoin de monter en compétence en appli mobile, peut être commencer à regarder ce qui a été fait pour monitoring.

#### lien avec la synthèse

est t'il possbile d'automatiser le processus d'intégration des données des sous-module dans la synthese
en allant plus loin que ce qui est fait dans monitoring, c'est à dire en automatisant la création de vue pour la synthese
- derouler les donnés selon l'arborescence renseignée dans la config
- associer les variable à celle de la table synthèse
  - soit de meme noms
  - soit association definie dans la config   

#### contruire le frontend du sous module en ligne

voir ce qui est fait pour l'oeasc ou les pages sont éditée en ligne en markdown, avec la possibilité d'ajouter des éléments (graphe, fomrulaire, etc...) (ne marche surement en angular mais en vue ok)