==========
Modules
==========

Definition du module ``module.json``
====================================


Commandes
=========

- ``geonature modules init <module_code>``
  - créer ou met à jour les fichiers
    - sql : ``<module_dir>/migrations/data/schema.sql``
    - alembic : ``<module_dir>/migrations/versions/<uuid>_init_<module_code>.py``

- ``geonature modules install <module_code>``
  - installe le module
    - fait un lien symbolique des fichiers alembic vers le repertoire <gn_modules>/migrations_versions
    - joue la migration alembic upgrade de la branche ``<module_code>``

- ``geonature modules remove <module_code>``
  - supprime le module
    - joue la migration alembic downgrade de la branche ``<module_code>``
    - supprime les liens symbloques liés à ce module dans le répertoire ``<gn_modules>/migrations_versions``

