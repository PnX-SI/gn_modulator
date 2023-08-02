-- Analyse bd_topo

DROP SCHEMA bd_topo CASCADE

CREATE SCHEMA bd_topo

DROP TABLE bd_topo.ROUTE_NOMMEE 
--
-- couche ROUTE_NUMEROTEE_OU_NOMMEE.shp
--

-- test shp src
SELECT DISTINCT shp_src FROM  bd_topo.ROUTE_NOMMEE 

-- nombre de route
SELECT COUNT(*) FROM BD_TOPO.route_nommee;

-- nombre de route / type 
SELECT count(*), type_route FROM bd_topo.route_nommee GROUP BY type_route ORDER BY count(*) DESC;

-- nombre de route / gestion
SELECT count(*), gestion FROM bd_topo.route_nommee GROUP BY gestion ORDER BY count(*) DESC;

-- analyse departementales
SELECT DISTINCT gestion FROM bd_topo.route_nommee WHERE type_route = 'Départementale'

-- lien gestion et area_code dept
SELECT GESTION, LA.AREA_CODE, COUNT(*)
    FROM BD_TOPO.ROUTE_NOMMEE RN 
    LEFT JOIN REF_GEO.L_AREAS LA ON LA.AREA_NAME = RN.GESTION
    LEFT JOIN REF_GEO.BIB_AREAS_TYPES BAT ON BAT.ID_TYPE = LA.ID_TYPE 
    WHERE 
        BAT.TYPE_CODE = 'DEP'
        AND RN.TYPE_ROUTE = 'Départementale'
        --AND la.ID_AREA IS NULL --CHECK join
    GROUP BY GESTION, LA.AREA_CODE 
    ORDER BY COUNT(*) DESC

-- TRONCON DE ROUTE

-- Nombre de troncon
SELECT count(*) FROM BD_TOPO.TRONCON_DE_ROUTE TDR

-- Nombre de troncon / cl_admin
SELECT cl_admin, count(*) FROM BD_TOPO.TRONCON_DE_ROUTE TDR GROUP BY cl_admin ORDER BY count(*) desc

-- unicité id_rn ~ numero pour les departementales
SELECT id, numero
FROM BD_TOPO.ROUTE_NOMMEE RN 
GROUP BY id, numero
HAVING count(*) > 1


--
-- Départementales
--

-- lien id_rn et couche pour les départementtales
WITH unnest_id_rn AS (
    SELECT 
        UNNEST(STRING_TO_ARRAY(id_rn, '/')) AS id_rn,
        id,
        NUMERO,
        gestion
        FROM  BD_TOPO.TRONCON_DE_ROUTE TDR
        WHERE CL_ADMIN = 'Départementale'
            AND ID_RN LIKE '%/%'
)
SELECT count(*), tdr.id, tdr.numero, id_rn, rn.NUMERO, rn.GESTION, rn.TYPE_ROUTE 
FROM  unnest_id_rn TDR
LEFT JOIN bd_topo.ROUTE_NOMMEE RN ON rn.id =  id_rn
WHERE rn.TYPE_ROUTE = 'Départementale'
GROUP BY tdr.id, tdr.numero, id_rn, rn.NUMERO, rn.GESTION, rn.TYPE_ROUTE 
ORDER BY count(*) DESC, tdr.id

-- association numero / dept

WITH troncon_route_unnest_id_rn AS (
    SELECT 
        UNNEST(STRING_TO_ARRAY(id_rn, '/')) AS id_rn,
        id,
        id_rn as id_rn_raw,
        NUMERO,
        gestion
        FROM  BD_TOPO.TRONCON_DE_ROUTE TDR
        WHERE CL_ADMIN = 'Départementale'
--            AND ID_RN LIKE '%/%'
)
SELECT tdr.id, id_rn_raw, rn.id, tdr.NUMERO, rn.NUMERO , tdr.GESTION, rn.GESTION, CONCAT(rn.NUMERO, ' (', la.area_code, ')')
FROM troncon_route_unnest_id_rn tdr
LEFT JOIN bd_topo.ROUTE_NOMMEE RN ON rn.id =  id_rn
LEFT JOIN REF_GEO.L_AREAS LA ON la.AREA_NAME = rn.GESTION 
WHERE rn.TYPE_ROUTE = 'Départementale' --AND tdr.GESTION != rn.GESTION 
--AND (rn.id IS NULL OR la.ID_AREA IS NULL) -- test pour vérifier les jointures

--    CASE 
--        WHEN TYPE_ROUTE = 'Départementale' THEN
--    END AS linear_type,


SELECT * FROM  BD_TOPO.ROUTE_NOMMEE RN  LIMIT 1

-- pour linear_group
SELECT 
    shp_src,
    rn.id AS linear_group_code,
    CASE 
        WHEN TYPE_ROUTE = 'Départementale' THEN CONCAT(rn.NUMERO, ' (', la.area_code, ')')
        ELSE rn.NUMERO 
    END AS linear_group_name
FROM BD_TOPO.ROUTE_NOMMEE RN 
LEFT JOIN REF_GEO.L_AREAS LA ON LA.AREA_NAME = RN.GESTION 
LEFT JOIN REF_GEO.BIB_AREAS_TYPES BAT ON BAT.ID_TYPE = LA.ID_TYPE AND BAT.TYPE_CODE = 'DEP'
WHERE RN.TYPE_ROUTE IN ('Autoroute', 'Départementale', 'Nationale')
ORDER BY NUMERO 

-- pour linear
WITH unnest_id_rn AS (
    SELECT 
        id,
        UNNEST(STRING_TO_ARRAY(id_rn, '/')) AS id_rn
    FROM  BD_TOPO.TRONCON_DE_ROUTE TDR
)
SELECT 
    tdr.id AS linear_code,
    tdr.id AS linear_name,
    string_agg(rn.id, ',')  AS linear_groups
    FROM bd_topo.TRONCON_DE_ROUTE TDR 
JOIN unnest_id_rn u ON u.id = tdr.id
JOIN BD_TOPO.ROUTE_NOMMEE RN ON RN.id = u.id_rn
WHERE
    tdr.CL_ADMIN IN ('Autoroute', 'Nationale', 'Départementale')
    AND rn.TYPE_ROUTE IN ('Autoroute', 'Nationale', 'Départementale')
GROUP BY tdr.id
HAVING count(*) > 1

SELECT * FROM bd_topo.ROUTE_NOMMEE RN WHERE NUMERO = 'D922'