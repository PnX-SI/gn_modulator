-- 
--DROP TABLE IF EXISTS bd_topo.POINT_DE_REPERE


    -- supprimer les doublons
    -- pk pr
WITH keep_id AS (
    SELECT
        id,
        min(gid) AS gid
    FROM
        BD_TOPO.POINT_DE_REPERE d
    GROUP BY
        id
)
DELETE
FROM
    BD_TOPO.POINT_DE_REPERE d
        USING keep_id k
WHERE
    d.id = k.id
    AND k.gid != d.gid;

-- points abhérents ? 
DELETE FROM BD_TOPO.POINT_DE_REPERE
WHERE id IN  ('POIN_REP0000002010252761');

-- nom_dept
ALTER TABLE BD_TOPO.POINT_DE_REPERE ADD COLUMN IF NOT EXISTS route_dept VARCHAR;

-- Tout
UPDATE BD_TOPO.POINT_DE_REPERE pdr SET route_dept = pdr.route
;


UPDATE BD_TOPO.POINT_DE_REPERE pdr SET route_dept = CONCAT(pdr.route,' (', la.area_code,')')
FROM REF_GEO.L_AREAS la
JOIN REF_GEO.BIB_AREAS_TYPES bat ON la.ID_TYPE =BAT.ID_TYPE AND BAT.TYPE_CODE = 'DEP'
WHERE la.AREA_NAME = pdr.gestion
;

--SELECT DISTINCT route FROM BD_TOPO.POINT_DE_REPERE 
--WHERE gestion = 'DIR Méditerranée';

-- Collectivité européenne d'Alsace et DIR Méditerranée
UPDATE BD_TOPO.POINT_DE_REPERE pdr SET route_dept = CONCAT(pdr.route,' (67-68)')
WHERE gestion = 'Collectivité européenne d''Alsace'
AND route LIKE 'D%'
;


--
DROP TABLE IF EXISTS BD_TOPO.import_point_pkpr;
CREATE TABLE BD_TOPO.import_point_pkpr AS
SELECT
    'PK_PR' AS id_TYPE,
    id AS POINT_CODE,
    TRIM(CONCAT(route_dept, ' ', numero, ' ',cote)) AS POINT_NAME,
    'IGN BDTOPO 3-3' AS SOURCE,
    TRUE AS enabled,
    '{' ||
    '"id_section": "' || COALESCE(id_SECTION, '')
    || '", ' || '"numero": "' || numero
    || '", ' || '"route_dept": "' || route_dept
    || '", ' || '"cote": "' || cote
    || '", ' || '"abscisse": "' || abscisse
    || '", ' || '"ordre": "' || ordre
    || '", ' || '"gestion": "' || COALESCE(gestion, '')
    || '"}' AS additional_data,
    ST_ASEWKT((ST_DUMP(geom)).geom) AS geom
FROM BD_TOPO.POINT_DE_REPERE pdr
WHERE TYPE_DE_PR IN ('PR0', 'PRF', 'PR');
