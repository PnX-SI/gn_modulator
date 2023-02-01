DROP VIEW IF EXISTS :pre_processed_import_view CASCADE;
CREATE VIEW :pre_processed_import_view AS
    SELECT
        'RTE' AS id_type,
        id AS linear_code,
        numero || '_' || substring(id, 9)::bigint AS linear_name,
        wkt as geom,
        true as enable,
        'https://geoservices.ign.fr/bdtopo#telechargementshpreg' AS source,
        numero as groups -- n-n ++
    FROM :raw_import_table
;

