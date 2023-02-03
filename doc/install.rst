Procédure pour une installation de sipaf

Préalable:
- récupérer les données route et pf

::

    source <GeoNature>/backend/venv/bin/activate

    # Installation du module geonature gn_modules
    geonature install-gn-module ~/gn_modules MODULES

    # Installation du sous-module
    geonature modules install m_sipaf

    # Import du ref_geo linéaire routes
    geonature modules import -i ref_geo.route -d  <data_dir_path>

    # Import des données sipaf (v5 pour l'exemple)
    geonature modules import -i m_sipaf.pf_exemples -d  ~/m_sipaf/import/data/

    ## Monitoring
    geonature modules install m_monitoring
    geonature modules install m_monitoring_test_1
    geonature modules features m_monitoring.exemples
    geonature modules features m_monitoring_test_1.exemples