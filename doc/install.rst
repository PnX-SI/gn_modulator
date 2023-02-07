Procédure pour une installation de sipaf

Préalable:
- récupérer les données route et pf et placer les fichiers dans <data_dir_path>

::

    source <GeoNature>/backend/venv/bin/activate

    # Installation du module geonature gn_modulator
    geonature install-gn-module ~/gn_modulator MODULATOR

    # Installation du sous-module
    geonature modulator install m_sipaf

    # Import du ref_geo linéaire routes
    geonature modulator import -i ref_geo.route -d  <data_dir_path>

    # Import des données sipaf (v5 pour l'exemple)
    geonature modulator import -i m_sipaf.pf_exemples -d  <data_dir_path>

    ## Monitoring
    geonature modulator install m_monitoring
    geonature modulator install m_monitoring_test_1
    geonature modulator features m_monitoring.exemples
    geonature modulator features m_monitoring_test_1.exemples