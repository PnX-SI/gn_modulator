=====
schema repository
=====

But
===

Créer une classe qui regroupe l'ensemble des méthodes liée à un schéma

-----------
Propriétés:
-----------

- ``_schema``: dictionnaire contenant le schema

--------
Methodes
--------

getter setter
-------------

- ``schema()``
- ``set_schema(schema)``

chargement / sauvegarde du schema
---------------------------------

- depuis un fichier
  - arborescence : ``schema/<module>/<name>``
  - ``load_from_file(file_path)``:
  - ``load_from_module_name(module, name)``:
  - ``save(file_path)``
  - ``save()`` # ``module``, ``name`` depuis ``_schema``

- depuis la base:
  - lecture / ecriture
  - ?? ou stocker les schemas,
    - 'gn_modulator.t_schemas' en jsonb
    - manque de maturité mais intéressant plus tard

validation
----------

- ``is_valid()`` : tester si le schema est valide et si non donner les erreurs
  - nécéssite d'écrire un schéma pour les schémas
- ``validate(data)`` : tester si une données est valide par rapport au schéma

parser le schema
----------------

- ``sql_table_name()``
- ``sql_schema_name()``
- ``model_name()``
- ``method_view_name()``
- ``url()`` ?? rest ou autres cas ???
- éléments de display
  - ``label()``
  - ``labels()``
  - ``def_label()``
  - ``def_labels()``
  - ``undef_label()``
  - ``undef_labels()``
  - ``title()`` ??
- ``properties()``
- ``parse()``: un dictionnaire contenant l'ensemble des éléments ci dessus

sql
---

- ``sql_create_table_txt()``
- ``sql_drop_table_txt()``

- ``table_exists()`` test de présence de la table ???, des tables de relations ???

?? sql depuis modèle sqlalchmey à essayer

model sqlalchemy
----------------

- ``model()`` !! refléchir à une variable globale pour mettre en cache les modèles et ne pas les recharger tout le temps


serializer / deserializer
-------------------------

??? utils_flask_sqla, marshmallow, custom

repository
----------

- methodes pour api rest
  - ``get()``
  - ``get_one()``
  - ``patch()``, ``put()`` ?? quelle différence
  - ``delete()``


routes
------

- api rest
  - ``MethodView()``
- route config
  - display
     - ``label``, etc....
  - ``schema``
  - schema_disposition pour formulaire ?
  - ``url`` api rest ?
  - etc ...

- ``register_api(blueprint)``
