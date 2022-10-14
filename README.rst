Module de modules
=================

Présentation
============



Installation
============
Se placer dans le répertoire backend de GeoNature et activer le virtualenv

``source venv/bin/activate``

Lancer la commande d'installation

``geonature install_packaged_gn_module <MON_CHEMIN_ABSOLUE_VERS_LE_MODULE /modules``

Installation de sous-modules
----------------------------

La commande suivante permet d'installer des sous-modules

``geonature modules install <module_code>``

Il faut au préalable placer la configuration du sous-module dans le dossier ``<gn_modules>/config/modules``

* idéalement dans le dossier ``<gn_modules>/config/modules/externals`` pour les sous-modules externes
* cela peut être une copie ou un lien symbolique vers le dossier
* le formalisme pour les codes des sous-modules est le suivante
    * en minuscule
    * preffixé par ``m_``
    * par exemple ``m_sipaf``, ``m_monitoring``, ``m_protocol_test``

Des sous-modules sont déjà présents dans le dossier ``<gn_modules>/config/modules/contrib``

* Le module gestionnaire de site
    * ``geonature modules install m_monitoring``
    * Défini les tables suivantes
        * site
        * groupe de sites
        * visite
        * observation
    * les api (liste, get, post, patch, delete) associées
    * Les pages associées au module suivent la hierachie:
        * site -> visite -> observation
    * des données d'exemples peuvent être ajoutées avec la commande ``geonature modules features m_monitoring.exemples``


* Un protocole de test pour le module monitoring
    * Il fauyt avoir installé au préalable le sous-module ``m_monitoring``
    * ``geonature modules install m_protocol_test``
        * module (protocole) -> site -> visite -> observation
    * des données d'exemples peuvent être ajoutées avec la commande ``geonature modules features m_monitoring.exemples``

Développement
=============

Création d'un sous-module
=========================

La démarche pour créer un sous module est exposée `ici <./doc/creation_module.rst>`_
