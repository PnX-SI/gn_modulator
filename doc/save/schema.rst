=======
Schemas
=======

Réflexion sur l'organisation et l'utilisation des schémas
===============================================================

Structure du schéma pour un objet contenant les champs suivants:
----------------------------------------------------------------

- TODO
  - ajouter les champs classique de jsonschema (``$id``, ``$ref``)
  - choisir un standart jsonschema
  - voir comment gérer les champs additionels (``$meta``)


::

    {
      "$id": "/schemas/test/example",
      "type": "object",
        "$meta": {
          "name": "nom qui référence l'objet",
          "module": "pour référencer le module",
          "sql_schema_name": "optionel",
          "sql_table_name": "optionel",
          "label": "label qui servira pour les titres, les bouttons, les messages, etc...",
          "description": "pour décrire l'objet",
          "labels": "quand le pluriel du label ne se limite pas à rajouter un nom à la fin",
          "genre": "'M' ou 'F' (masculin féminin)",
        },
        "$properties": {
            "key": "# ... ensemble des propriétés qui peuvent être
            - un champs (texte, nombre, date, geom, etc..)
            - une relation
            - key : {
                type: <integer|string>,
                $ref: <reférence vers un autre schéma>,
                ?primary_key: <true|false>}"
        }
    }



de ce schéma, on doit être en mesure de tirer les information suivantes:

- sql
    - ``sql_schema_name`` : nom du schema sql (attention à la confusion schema sql et schema jsonschema)
    - ``sql_table_name`` : nom de la table
      - ````sql_schema_name`` et ``sql_table_name`` peuvent être soit définis dans ``$meta`` soit déduis des valeurs de ``module`` et ``name``
    - ``pk_field_names`` : ensemble des clé primaires
- python
    - ``model_name`` : nom du modèle sqla
    - ``model_vie_name`` : nom du modèle de vues
    - ``base_url`` : url de base pour l'api rest
    - ``schema_path``: chemin pour atteindre la fichier du schema
- affichage
    - ``label`` avec article défini/indéfini au singulier/pluriel

Un exemple
==========

.. code-block:: json

    {
        "$meta": {
            "name": "example",
            "module": "test",
            "description": "Objet Example pour le sous module Test, permet de démontrer la viabilité de gn_modules",
            "label": "exemple",
            "genre" : "M"
        },

        "$properties" : {
            "id_example" : {"type": "integer", "primary_key": true},
            "nom_example" : {"type" : "string"},
            "code_example" : {"type" : "string"}
        }
    }
```

donnera les informations suivantes :

.. code-block:: json

    {
        "sql_schema_name": "m_test",
        "sql_table_name": "t_example",
        "pk_field_names": ["id_example"],

        "model_name": "TTestExample",
        "model_view_name": "MVTestExample",
        "base_url": "/test/examples/",
        "schema_path": "test/example.json",

        "label": "exemple",
        "labels": "exemples",
        "label_def": "l'exemple",
        "label_undef": "un exemple",
    }


et les données seront de la forme suivante :


.. code-block:: json

    {
        "id_example": 1,
        "nom_example": "Exemple 01",
        "code_example": "E_01"
    }
