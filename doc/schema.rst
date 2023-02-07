===========
Les schemas
===========

- ``meta``
    - contient des informations sur le schela
- ``properties``
    - liste les propriété du schema
        - les colonnnes de la table
        - les relations
        - les ``columns properties`` (ou vues)


- ``required``
    - liste les champs requis

``meta``
========

- ``schema_code`` : nom du schema
- ``slq_processing``: le sql est généré par gn_modulator
- ``sql_schema_dot_table``: table dans la base postgres
- ``label``: Nom utilisé en frontend
- ``labels``: *optionel*, nom utilisé pour le pluriel
    - par défaut on rajoute un ``s`` à la fin de ``label``
- ``genre``: ``M`` (masculin) ou ``F`` féminin
    - pour accordér les arcticles (dans les titres, tooltips, etc...)
- ``geometrie_field_name``: champs utilisé pour afficher la geometrie sur une caractère
- ``label_field_name``: champs utilisé pour référence une ligne dans un titre
- ``unique``: tableau de champs utilisés pour définir l'unicité d'une ligne
    - ce champs n'est pas la clé primaire
    - idéalement ce chamsp n'est pas un uuid

- ``check_cruved``: **TODO à préciser !!**
    - le cruved est appliqué
        - on calcule l'appartenance des données
        - on filtre sur les route de listes
        - TODO check cruved pour creation et update en backend

# - schema_complement
"     - nom du schema qui va lister les tables de complément pour cette table


``properties``
==============