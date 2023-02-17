# Changelog

## 1.0.3 (unreleased)

**🐛 Corrections**
- composant de filtre: prise en compte des filtre quand la valeur est `false`
- ajout des champs par défaut (dont `ownership`) && correction droits tableaux
- amélioration affichage tableaux dans tabs
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
