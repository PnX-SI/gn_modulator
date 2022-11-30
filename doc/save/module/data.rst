============
Data
============

Cette section concerne l'ajout de données nécessaire pour un module.

Il peut s'agir par exemple de nomenclature spécifiques.
L'exemple suivi pour la suite concernera l'ajout de nomenclature de type météo, mais la procédure est la même
pour d'autres type de nomenclature (et à l'avenir pour d'autres types de données).

Fichier de données
------------------

Les fichiers de données au format ``.json`` sont placé dans le dossier ``<gn_modules>/config/data/``

par exemple le fichier ``<gn_modules>/config/data/test.json``

::

    {
        "nomenclature_type": [
            {
                "mnemonique": "TEST_METEO",
                "label": "Météo",
                "definition": "Météo (protocôle de suivi test)"
            }
        ],
        "nomenclatures": [
            {
                "type":"TEST_METEO",
                "cd_nomenclature": "METEO_B",
                "mnemonique": "Beau",
                "label": "Beau temps",
                "definition": "Beau temps (test)"
            },
            {
                "type":"TEST_METEO",
                "cd_nomenclature": "METEO_M",
                "mnemonique": "Mauvais",
                "label": "Mauvais temps",
                "definition": "Mauvais temps (test)"
            }
        ]
    }

Ils seronts validées par le schema présent dans le fichier ``<gn_modules>/config/schema/data/data.json``


Commande process_data
-----------------------------

La commande permet d'insérer (ou de mettre à jour si les éléments existent déjà) les données du fichier json correspondant

::

    geonature modules process_data -d <data_code>

par exemple

::

    geonature modules process_data -d data


va insérer ou mettre à jour les données du fichier ``<gn_modules>/config/data/test.json``.

* si un point est présent dans le paramètre on ira chercher le fichier dans l'arobrescence correspondante.
    * ``<test.exemple>`` correspond au fichier ``<gn_modules>/config/data/test/exemple``

* si le chemin concerné est un répertoire, tous les fichiers de ce répertoire seront pris en compte

