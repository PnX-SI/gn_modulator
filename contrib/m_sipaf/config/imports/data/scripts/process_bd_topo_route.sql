--
-- 1er traitement enlever les doublons
--
    

-- ROUTE_NUMEROTEE_OU_NOMMEE
WITH keep_id AS ( 
    SELECT
        id, min(gid) AS gid
    FROM BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE d
    GROUP BY id
)
DELETE FROM BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE d
USING keep_id k
WHERE d.id = k.id AND  k.gid != d.gid;

-- troncon_de_route
WITH keep_id AS ( 
    SELECT
        id, min(gid) AS gid
    FROM BD_TOPO.TRONCON_DE_ROUTE  d
    GROUP BY id
)
DELETE FROM BD_TOPO.TRONCON_DE_ROUTE d
USING keep_id k
WHERE d.id = k.id AND  k.gid != d.gid;


-- ajout colonne pour numero + dept pour les départementales
ALTER TABLE BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE ADD COLUMN IF NOT EXISTS numero_dept VARCHAR;

UPDATE BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE rn SET numero_dept = CONCAT(rn.numero,' (', la.area_code,')')
FROM REF_GEO.L_AREAS la
JOIN REF_GEO.BIB_AREAS_TYPES bat ON la.ID_TYPE =BAT.ID_TYPE AND BAT.TYPE_CODE = 'DEP'
WHERE la.AREA_NAME = rn.gestion
AND rn.TYPE_ROUTE = 'Départementale'
;

-- Collectivité européenne d'Alsace et DIR Méditerranée
UPDATE BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE rn SET numero_dept = CONCAT(rn.numero,' (67-68)')
WHERE rn.TYPE_ROUTE = 'Départementale' AND gestion = 'Collectivité européenne d''Alsace'
;

-- DIR Méditerranée
UPDATE BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE rn SET numero_dept = CONCAT(rn.numero,' (30)')
WHERE rn.TYPE_ROUTE = 'Départementale' AND gestion = 'DIR Méditerranée'
;

-- Nationale & Autoroutes
UPDATE BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE rn SET numero_dept = rn.numero
WHERE rn.TYPE_ROUTE in ('Autoroute', 'Nationale')
;


-- import route nommee
DROP TABLE IF EXISTS BD_TOPO.import_linear_group_route;
CREATE TABLE BD_TOPO.import_linear_group_route As
SELECT
    numero_dept AS code,
    CONCAT(type_route, ' ', numero_dept) AS name
FROM BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE RN
GROUP BY numero_dept, type_route
;

-- import troncon / route (numero_dept)
DROP TABLE IF EXISTS BD_TOPO.import_linear_route;
CREATE TABLE BD_TOPO.import_linear_route AS
WITH unnest_rn_id AS (
    SELECT
        UNNEST(STRING_TO_ARRAY(id_rn, '/')) AS id_rn_split,
        *
        FROM BD_TOPO.TRONCON_DE_ROUTE TR
)
SELECT
    CASE
        WHEN CL_ADMIN = 'Départementale' THEN 'RT_DEP'
        WHEN CL_ADMIN = 'Nationale' THEN 'RT_NAT'
        WHEN CL_ADMIN = 'Autoroute' THEN 'RT_AUT'
        ELSE NULL
    END AS id_type,
    tr.id AS linear_code,
    concat(STRING_AGG(rn.NUMERO_DEPT , ', '), ' ',REPLACE(tr.id, 'TRONROUT000000', 'TR ')) AS linear_name,
    STRING_AGG(rn.NUMERO_DEPT, ',') AS groups,
    ST_ASEWKT(tr.geom) AS geom,
    'IGN BDTOPO 3-3' AS SOURCE,
    TRUE AS ENABLED
    FROM unnest_rn_id TR
    JOIN BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE RN ON RN.id = TR.id_rn_split
    GROUP BY tr.id, tr.geom, tr.CL_ADMIN
;