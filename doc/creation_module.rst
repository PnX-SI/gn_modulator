Création d'un module
====================

Aide au développement
---------------------

En phase de développement, il est pratique d'avoir l'application flask qui redemarre automatiquement en cas de changement des fichiers de configuration (yml)
Pour cela vous pouvez lancer l'application avec les commandes suivantes

::

    source <GEONATURE_DIR>/backend/venv/bin/activate
    export extra_files="$(find -L <GEONATURE_DIR>/external_modules/modules/config -type f -name \*.yml | sed -n '1{h};1!{H};${g;s/\n/:/pg}')"
    export FLASK_APP=geonature.app; export FLASK_DEBUG=1;
    flask run --port 8000 --host 0.0.0.0 --extra-files="$extra_files"

Pour voir les changement de la configuration au niveau du frontend, il faudra recharger la page du navigateur (``CTRL + MAJ + R`` ou ``MAJ + F5``)

Nous prenons comme exemple un projet de suivi de parc éolien

Configuration du module
-----------------------

La strucure du dossier de la configuration du module est la suivante:

::

    /
        # fichier de configuration du module
        module.yml

        # fichiers de définition des objects (tables, modèles) associés à ce module
        definitions/

        # données addionelles
        features/

        # fichiers images, médias, etc..
        assets/

        # fichiers contenant la configuration des pages du modules
        layouts/


``module.yml``
~~~~~~~~~~~~~~

Dictionnaire définissant la configuration du module, avec les clés suivantes:

- **module**:

  - information destinées à la table ``gn_commons.t_modules``

::

    module:
        module_code: m_eole
        module_label: Modules de suivi éolien
        module_desc: POC pour le projet suivi éolien
        module_picto: fa-puzzle-piece
        active_frontend: true

- **objects**
    - permet de les données qui vont être manipulée dans ce module
        - pour chaque clé on va définir
            - **schema_name**: définie la table
            - **cruved**: quelles sont les api qui vont être ouvertes et pour quels type d'action
            - **prefilters**:
                - par exemple pour les gîtes on souhaite avoir seulement les sites de catégorie ``gîtes``
                - ``prefilters: category.code = GIT``
                - l'api créée pour cet object (et ce module) appliquera toujours les pré-filtres definis ic
            - **label**: redéfinition du nom de l'objet
            - **labels**: redéfinition du nom (pluriel de l'objet
            - **genre**: ``'M'|'F'`` redéfinition du genre de l'object (masculin / féminin)
            - **map**:
                - **style**: style css des layers
                    - **color**
                - **bring_to_front**: *boolean*, si l'on souhaite ramener ces éléments au premier plan
            - **exports**: liste des nom d'export (``export_name``) associés à l'object


- **tree**: un dictionnaire qui défini une hiérachie entre les pages, classiquement

::
    site:
        visite:
            observation:

- **pages**: la définition des pages qui composent le module_label

::
    pages:
        parc_list:
            url: ''
            layout_name: m_eole.parc_list

- **exports**:

::
    m_sipaf.pf: # code de l'export ou ``export_name``
        export_label: Test
        object_name: pf
        fields:
            - id_passage_faune
            ...
