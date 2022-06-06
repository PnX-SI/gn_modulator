========
FRONTEND
========

Briques de bases et routes test/
===============================
 
- Détail des propriétés
  - ``/test/properties/<module>/<name>/<id>`` 
- Tableau de données
  - ``/test/table/<module>/<name>``
- Formulaire
  - ``/test/form/<module>/<name>``
  - ``/test/form/<module>/<name>/<id>``
- les trois dans la même page (id pris depuis le click sur le tableau par exemple 
  - ``/test/form/<module>/<name>``
Pour chacun
- Initialisation:
  - récupération de la configuration (schema, display) 
    - par un service (ModulesConfigService)
    - à partir de ``<module>``, ``<name>``

Properties
----------

Titre :  ``Détail ${config.du_label}`` ( Détail du truc, Détail de l'exemple)

Tableau des propriétés en lignes

Table
-----

Titre : ``Tableau des ${config.labels}``

Tableau server side + filtres + sort
inputs du composant en lien avec les paramètres de route
- params
  - filtres
  - page
  - size
  - sort


Formulaire
----------

Titre : ``Création / Edition d'un(e) ${label}`` selon si <id> est défini ou non

inputs du composant en lien avec les paramètres de route

- params
  - value
  - 