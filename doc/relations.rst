===================
Module et Relations
===================

Test 1
======

- Créer un module avec deux schema
  - test/_parent
   _ - id_parent
     - parent_name
  - test/child
    - id_child
    - child_name

- fonctionalité pour charger un module
  - tester les dépendances
  - créer les table dans l'ordre
    - avec les contraintes de clé étrangères
  - créer les modèles dans l'ordre
    - avec les relations
      - parent => tableau de child
      - child => parent
        - ?? avec les backref

- tester les api
  - par tableau, propriétés, form

