SELECT
    id_import,
    'RTE' AS id_type,
    id AS linear_code,
    numero || '_' || substring(id, 9) :: bigint AS linear_name,
    wkt as geom,
    true as enable,
    'https://geoservices.ign.fr/bdtopo#telechargementshpreg' AS source,
    numero as groups -- n-n ++