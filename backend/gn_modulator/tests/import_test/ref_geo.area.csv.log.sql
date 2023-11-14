-- Log Import xxx
-- - schema_code: ref_geo.area

-- Tables et vues utlisées pour l'import
-- - data: gn_modulator_import.t_xxx_data
--    table contenant les données du fichier à importer
--
-- - mapping: gn_modulator_import.t_xxx_data
--    vue permettant de faire la corresondance entre
--             le fichier source et la table destinataire
--
-- - raw: gn_modulator_import.v_xxx_raw_ref_geo_area
--    choix des colonnes, typage
--
-- - process: gn_modulator_import.v_xxx_process_ref_geo_area
--    résolution des clés
--


-- Creation de la table des données

CREATE TABLE IF NOT EXISTS gn_modulator_import.t_xxx_data (
    id_import SERIAL NOT NULL,
    id_type VARCHAR,
    area_name VARCHAR,
     area_code VARCHAR,
    geom VARCHAR,
    CONSTRAINT pk_gn_modulator_import.t_xxx_data_id_import PRIMARY KEY (id_import)
);


-- Insertion des données

INSERT INTO gn_modulator_import.t_xxx_data (id_type, area_name,  area_code, geom)
    VALUES
         ('ZC','Parc National du Triangle','PNTRI','POLYGON((6.48 48.87, 5.22 47.84, 6.87 47.96, 6.48 48.87))'),
        ('ZC','Parc National du Carré','PNCAR','POLYGON((3.29 45.05, 5.49 44.91, 5.42 43.80, 3.12 44.11, 3.29 45.05))')
;

-- Typage (raw)

DROP VIEW IF EXISTS gn_modulator_import.v_xxx_raw_ref_geo_area CASCADE;
CREATE VIEW gn_modulator_import.v_xxx_raw_ref_geo_area AS
SELECT
    t.id_import,
    t.id_type,
    area_name,
    area_code,
    ST_MULTI(ST_SETSRID(ST_FORCE2D(geom::GEOMETRY), 2154)) AS geom,
    CONCAT(t.id_type, '|', t.area_code) AS id_area
FROM gn_modulator_import.t_xxx_data t;


-- Vue d'import

DROP VIEW IF EXISTS gn_modulator_import.v_xxx_process_ref_geo_area CASCADE;
CREATE VIEW gn_modulator_import.v_xxx_process_ref_geo_area AS
SELECT
    min(id_import) AS id_import,
    j_0.id_type AS id_type,
    t.area_name,
    t.area_code,
    t.geom,
    j_pk.id_area
FROM gn_modulator_import.v_xxx_raw_ref_geo_area t
LEFT JOIN ref_geo.bib_areas_types j_0
    ON j_0.type_code = t.id_type
LEFT JOIN ref_geo.l_areas j_pk
    ON j_pk.id_type = j_0.id_type
    AND (j_pk.area_code = SPLIT_PART(t.id_area, '|', 2)
      OR (j_pk.area_code IS NULL AND SPLIT_PART(t.id_area, '|', 2) IS NULL))
GROUP BY j_0.id_type, t.area_name, t.area_code, t.geom, j_pk.id_area
;


-- Comptage insert

WITH d AS (
    SELECT
        DISTINCT id_type, area_code
    FROM gn_modulator_import.v_xxx_process_ref_geo_area
    WHERE id_area IS NULL
)
SELECT
    COUNT(*)
FROM d
;


-- Comptage update

SELECT
    COUNT(*)
FROM ref_geo.l_areas t
JOIN gn_modulator_import.v_xxx_process_ref_geo_area a
    ON a.id_area = t.id_area

WHERE (t.id_type IS DISTINCT FROM a.id_type)
    OR (t.area_name IS DISTINCT FROM a.area_name)
    OR (t.area_code IS DISTINCT FROM a.area_code)
    OR (t.geom IS DISTINCT FROM a.geom)
;


-- Insertion des données

INSERT INTO ref_geo.l_areas (
    id_type,
    area_name,
    area_code,
    geom
)
SELECT
    id_type,
    area_name,
    area_code,
    geom
FROM gn_modulator_import.v_xxx_process_ref_geo_area WHERE id_area IS NULL
;


-- Mise à jour des données

UPDATE ref_geo.l_areas t SET
    id_type=p.id_type,
    area_name=p.area_name,
    area_code=p.area_code,
    geom=p.geom
FROM (
    SELECT
        id_type,
        area_name,
        area_code,
        geom,
        id_area
    FROM gn_modulator_import.v_xxx_process_ref_geo_area
)p
WHERE p.id_area = t.id_area
  AND NOT (
    (t.id_type IS DISTINCT FROM p.id_type)
    AND (t.area_name IS DISTINCT FROM p.area_name)
    AND (t.area_code IS DISTINCT FROM p.area_code)
    AND (t.geom IS DISTINCT FROM p.geom)
    AND (t.id_area IS DISTINCT FROM p.id_area)
)
;


