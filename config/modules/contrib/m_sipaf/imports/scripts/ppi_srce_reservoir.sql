SELECT
    'RESV_SRCE' AS id_type,
    id_resv AS area_code,
    CASE
        WHEN nom_resv IS NOT NULL THEN nom_resv
        ELSE id_resv
    END AS area_name,
    wkt AS geom,
    TRUE AS enable,
    'https://inpn.mnhn.fr/docs/TVB/N_SRCE_RESERVOIR_S_000.zip' AS source