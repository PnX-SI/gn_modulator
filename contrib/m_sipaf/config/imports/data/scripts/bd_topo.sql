--
-- 1er traitement enlever les doublons
--

-- route_nommee
WITH keep_id AS ( 
    SELECT
        id, min(gid) AS gid
    FROM BD_TOPO.ROUTE_NOMMEE d
    GROUP BY id
)
DELETE FROM BD_TOPO.ROUTE_NOMMEE d
USING keep_id k
WHERE d.id = k.id AND  k.gid != d.gid

-- troncon_de_route
WITH keep_id AS ( 
    SELECT
        id, min(gid) AS gid
    FROM BD_TOPO.TRONCON_ROUTE  d
    GROUP BY id
)
DELETE FROM BD_TOPO.TRONCON_ROUTE d
USING keep_id k
WHERE d.id = k.id AND  k.gid != d.gid


-- ajout colonne pour numero + dept pour les départementales
ALTER TABLE BD_TOPO.ROUTE_NOMMEE ADD COLUMN numero_dept VARCHAR;

UPDATE BD_TOPO.ROUTE_NOMMEE rn SET numero_dept = CONCAT(rn.numero,' (', la.area_code,')')
FROM REF_GEO.L_AREAS la
JOIN REF_GEO.BIB_AREAS_TYPES bat ON la.ID_TYPE =BAT.ID_TYPE AND BAT.TYPE_CODE = 'DEP'
WHERE la.AREA_NAME = rn.gestion
AND rn.TYPE_ROUTE = 'Départementale'

-- Collectivité européenne d'Alsace et DIR Méditerranée
UPDATE BD_TOPO.ROUTE_NOMMEE rn SET numero_dept = CONCAT(rn.numero,' (67,68)')
WHERE rn.TYPE_ROUTE = 'Départementale' AND gestion = 'Collectivité européenne d''Alsace'

-- DIR Méditerranée
UPDATE BD_TOPO.ROUTE_NOMMEE rn SET numero_dept = CONCAT(rn.numero,' (30)')
WHERE rn.TYPE_ROUTE = 'Départementale' AND gestion = 'DIR Méditerranée'

-- Nationale & Autoroutes
UPDATE BD_TOPO.ROUTE_NOMMEE rn SET numero_dept = rn.numero
WHERE rn.TYPE_ROUTE in ('Autoroute', 'Nationale')

-- test depatementales (doit être 0)
SELECT count(*)
    FROM BD_TOPO.ROUTE_NOMMEE RN 
    WHERE rn.TYPE_ROUTE = 'Départementale' AND NUMERO_DEPT IS null

-- test departementale 1 seul morceau
SELECT count(*), NUMERO_DEPT, ARRAY_AGG(id) 
FROM bd_topo.ROUTE_NOMMEE RN
GROUP BY NUMERO_DEPT
ORDER BY count(*) DESC  

-- lien troncon / route (numero_dept)

SELECT * FROM BD_TOPO.TRONCON_ROUTE TR

WITH unnest_rn_id AS (
    SELECT 
        UNNEST(STRING_TO_ARRAY(id_rn, '/')) AS id_rn_split,
        *
        FROM BD_TOPO.TRONCON_ROUTE TR 
)
SELECT
    CASE 
        WHEN CL_ADMIN = 'Départementale' THEN 'RT_DEP'
        WHEN CL_ADMIN = 'Nationale' THEN 'RT_AUT'
        WHEN CL_ADMIN = 'Autoroute' THEN 'RT_AUT'
        
    END AS id_type
    END
    
    FROM unnest_rn_id TR
    JOIN BD_TOPO.ROUTE_NOMMEE RN ON RN.id = TR.id_rn_split
    WHERE rn.NUMERO != tr.NUMERO      

    SELECT * FROM REF_GEO.BIB_LINEARS_TYPES BLT 