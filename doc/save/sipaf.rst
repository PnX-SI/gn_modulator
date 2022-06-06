================
Passages à Faune
================

Réflexions sur le projet passage à faune (``SIPAF``) et son intégration dans géonature

===========
Les Besoins
===========

La principale demande est de constituer une base de données de référence sur les passages à faune.

Il est demandé aussi de pouvoir mettre en lien des passages à faune et des observations.

Les usages liés à ces observations ne sont pas encore définis.

Données
=======

- modèle de données ``SIPAF``
    - https://cloud.ecrins-parcnational.fr/index.php/s/zNjMa53wkHH4C57?dir=undefined&openfile=93162

- données d'observations

Fonctionalités
==============

- import /export
- saisie / consultation

==============
Questionnement
==============

- rôle de ``gn_monitoring.t_base_sites`` ?

============
Propositions
============

P1) ``gn_monitoring.t_base_sites`` central
==========================================

- Donner un rôle central à ``gn_monitoring.t_base_sites`` et monitoring et construire le ``SIPAF`` autour
- Proposition à développer

P2) Un schéma dédié au ``SIPAF`` et créer des ponts avec le reste
=================================================================

Idée générale
-------------

La demande principale est la constitution d'une base de donnée de référence pour les passages à faune,

Une solution serait de :

- créer un schema ``pr_sipaf`` 
    - avec les données **complètes** concernant les passages à faune
    - en lien avec un module de gestion des données ``SIPAF``

- créer des ponts vers d'autres éléments de geonature
    - la synthese 
        - pouvoir lier des observations avec des passages à faune

    - monitoring
        - pouvoir lier des passages à faune avec les sites du schema ``gn_monitoring``
        - permet de pouvoir lier des protocole de suivi (de type sous-module monitoring) au passages à faune

Détails
-------

- Données passage à faune
    -  dans un schema dédié ``pr_sipaf``
        - ``t_pafs`` : les données des passages à faune
        - ``t_interventions`` etc...

- Observations : 
    - lien avec la synthese
    - le lien se fait par une table de correlation
        - entre ``gn_synthese.synthese`` et ``pr_sipaf.t_paf``
        - nommée ``pr_sipaf.cor_synthese`` ou ``pr_sipaf.cor_synthese_paf``
        - avantages
            - on a les informations de la source provenance
            - on peut selon les cas remonter à la source (``occtax``, ``monitoring``, ...)
            - les données associées à un passage faune peuvent provenir de différentes sources
                - occtax
                - monitoring
                - autres modules spécifiques GN
                - données importée sans module geonature dédiés
        - inconvénients
            - comment associer une donnée à un passage faune en pratique ?
            - comment vérifier / assurer l'intégrité des données

- **Monitoring**
    - Lien avec le module ``monitorings`` et ``gn_monitoring.t_base_sites``
      - t_base_sites reprend les données de ``pr_sipaf.t_paf`` pour les champs
          - ``base_site_name``
          - ``base_site_code``
          - ``geom``
          - autres ...???
      - lien simple ``1-1``
          - entre les sites monitoring et les passages à faune
          - par la table ``gn_monitoring.t_site_complements`` 
          - ou table dédiée ``gn_monitoring.t_site_sipaf`` ou ``pr_sipaf.t_site_monitoring``
          - avec les champs
              - ``id_base_site``
              - ``id_sipaf``
          - et des contraintes d'unicité 
              - ``id_sipaf``
              - (``id_sipaf``, ``id_base_site``)
              
