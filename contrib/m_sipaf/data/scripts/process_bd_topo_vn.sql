

-- table intermediaire cor_vn_group

DROP TABLE IF EXISTS bd_topo.cor_vn_group;
CREATE TABLE bd_topo.cor_vn_group AS
SELECT 
  UNNEST ( STRING_TO_ARRAY(id_c_eau, '/')) AS id_c_eau,
  th.id AS id_troncon
FROM bd_topo.TRONCON_HYDROGRAPHIQUE TH 
LEFT JOIN bd_topo.COURS_D_EAU CDE ON cde.ID  = th.ID_C_EAU 
WHERE cde.ID IS NOT NULL AND navigabl = 'Oui'
;

-- table group vn

DROP TABLE IF EXISTS bd_topo.import_linear_group_vn;
CREATE TABLE bd_topo.import_linear_group_vn AS 
WITH id_c_eaus AS (
    SELECT id_c_eau 
    FROM bd_topo.cor_vn_group
)
SELECT 
    id AS code,
    COALESCE(toponyme, id) AS name
FROM bd_topo.COURS_D_EAU CDE
JOIN id_c_eaus ids ON ids.id_c_eau = cde.id
GROUP BY  id, toponyme
;

-- table troncon vn
DROP TABLE IF EXISTS bd_topo.import_linear_vn;
CREATE TABLE bd_topo.import_linear_vn AS 
SELECT
    th.id AS linear_code,
    CONCAT(STRING_AGG(DISTINCT cde.toponyme, ' '), ' ', REPLACE(th.id, 'TRON_EAU000000', 'TR ')) AS linear_name, 
    'VN' AS id_type,
    STRING_AGG(DISTINCT cde.id, ',') AS GROUPs,
    ST_ASEWKT(th.geom) AS geom,
    'IGN BDTOPO 3-3' AS SOURCE,
    True AS enabled
FROM BD_TOPO.TRONCON_HYDROGRAPHIQUE TH 
JOIN bd_topo.cor_vn_group g ON g.id_troncon = th.id 
JOIN BD_TOPO.COURS_D_EAU CDE ON g.id_c_eau = cde.id
GROUP BY th.id, th.geom;


SELECT count(DISTINCT code) FROM bd_topo.import_linear_group_vn
