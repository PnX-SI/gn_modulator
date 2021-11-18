=======
Schema
=======

``id``
------

``schema/test/example.json``

``properties``
--------------

Dictionnaire.

Ses éléments sont les éléments sont des dictionnaires qui contiennent les champs suivant:

* ``type`` : *string*, **obligatoire**
    * à choisir parmi
        * ``"string"``
        * ``"numb`er"``
        * ``"object"``
        * ``"array"``

* ``label`` : *string*

* ``primary_key`` : *boolean*

* ``format`` : *string*
    * ``uuid``

* ``nomenclature_type`` :
    * permet de considérer cette variable comme une clé étrangère vers ``ref_nomenclatures.t_nomenclature.id_nomenclature``
    * renseigne le type de nomenclature
    * à choisr parmi les valeurs du champs ``mnemonique`` de la table ``ref_nomenclatures.bib_nomenclatures_types``
    * exemples: ``STADE_VIE``, ``SEXE``, etc...

* ``foreign_key`` : *string*
    * example: ``#/schemas/utils/nomenclature.id_nomenclature``

* ``rel`:
    * permet de définir une relation associée au clé suivantes
* ``foreign_key``: le nom de la colonne de la relation
* ``local_key``: le nom de la colonne du schema courant
* ``cor``