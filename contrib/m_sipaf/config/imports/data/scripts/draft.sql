
WITH close_troncons AS (
    SELECT 
        ID_PASSAGE_FAUNE,
        id_linear, 
        ST_distance(TPF.GEOM_LOCAL, ll.geom) AS d
    FROM PR_SIPAF.T_PASSAGES_FAUNE TPF
    JOIN REF_GEO.L_LINEARS LL ON ST_DWithin(TPF.GEOM_LOCAL, ll.geom, 50)
),
closest AS (
    SELECT id_passage_faune, 
    id_linear,
    ROW_NUMBER() OVER (PARTITION BY ID_PASSAGE_FAUNE  ORDER BY d) rn,
    d
    FROM close_troncons
) 
--INSERT INTO PR_SIPAF.COR_LINEAR_PF(ID_PASSAGE_FAUNE, id_linear) 
SELECT c.ID_PASSAGE_FAUNE, c.id_linear
FROM closest c
JOIN PR_SIPAF.T_PASSAGES_FAUNE TPF2 ON TPF2.ID_PASSAGE_FAUNE = c.id_passage_faune
JOIN REF_GEO.L_LINEARS LL2 ON LL2.ID_LINEAR = c.id_linear
WHERE c.rn = 1
--ON CONFLICT DO NOTHING

DELETE FROM PR_SIPAF.COR_LINEAR_PF 

SELECT count(*) FROM PR_SIPAF.COR_LINEAR_PF CLP 

SELECT count(*) FROM PR_SIPAF.T_PASSAGES_FAUNE TPF 

SELECT *
FROM PR_SIPAF.T_PASSAGES_FAUNE TPF 
JOIN PR_SIPAF.cor

SELECT DISTINCT
  (SELECT string_agg(ref_geo.l_linears.linear_name, ', ') AS string_agg_1
   FROM ref_geo.l_linears,
        pr_sipaf.cor_linear_pf,
        ref_geo.bib_linears_types
   WHERE pr_sipaf.cor_linear_pf.id_passage_faune = pr_sipaf.t_passages_faune.id_passage_faune
     AND pr_sipaf.cor_linear_pf.id_linear = ref_geo.l_linears.id_linear
     AND ref_geo.bib_linears_types.id_type = ref_geo.l_linears.id_type
     AND ref_geo.bib_linears_types.type_code = 'RTE') AS anon_1,
                pr_sipaf.t_passages_faune.id_passage_faune
FROM pr_sipaf.t_passages_faune



SELECT count(*) FROM REF_GEO.COR_LINEAR_GROUP CLG 

SELECT count(*) FROM REF_GEO.L_LINEARS LL 


SELECT * FROM PR_SIPAF.T_PASSAGES_FAUNE TPF WHERE ID_PASSAGE_FAUNE = 358

SELECT
    ID_PASSAGE_FAUNE,
    tpf.geom
--        ID_PASSAGE_FAUNE,
  --      id_linear, 
    --    ST_distance(TPF.GEOM_LOCAL, ll.geom) AS d
    FROM PR_SIPAF.T_PASSAGES_FAUNE TPF
    LEFT JOIN REF_GEO.L_LINEARS LL ON ST_DWithin(TPF.GEOM_LOCAL, ll.geom, 50)
    WHERE id_linear IS nULL
    

SELECT ID_PASSAGE_FAUNE, ll.LINEAR_NAME, ST_distance(TPF.GEOM_LOCAL, ll.geom), ll.geom, tpf.GEOM_LOCAL 
FROM PR_SIPAF.T_PASSAGES_FAUNE TPF
JOIN REF_GEO.L_LINEARS LL ON TRUE
WHERE  ST_DWithin(TPF.GEOM_LOCAL, ll.geom, 1000)
AND ID_PASSAGE_FAUNE = 685
ORDER BY ST_distance(TPF.GEOM_LOCAL, ll.geom)

SELECT geom, LINEAR_CODE  FROM REF_GEO.L_LINEARS LL WHERE LINEAR_NAME LIKE '%N141%'
AND geom && 
          ST_TRANSFORM(ST_SETSRID(
            ST_MakeBox2D(
                ST_MakePoint(-0.35, 45),
                ST_MakePoint(-0.3499, 46)),
          4326), 2154)


SELECT * FROM BD_TOPO.TRONCON_DE_ROUTE TR WHERE id='TRONROUT0000002327226040'

SELECT geom::GEOMETRY FROM BD_TOPO.IMPORT_LINEAR_ROUTE ILR WHERE LINEAR_CODE = 'TRONROUT0000002327226040'

ALTER TABLE BD_TOPO.import_linear_route RENAME linear_group groups

SELECT linear_name, linear_group FROM BD_TOPO.import_linear_route i
LEFT JOIN REF_GEO.T_LINEAR_GROUPS TLG ON i.linear_code LIKE CONC'%' ||tlg.CODE || '%' 
WHERE TLG.ID_GROUP IS NULL 


SELECT * FROM BD_TOPO.ROUTE_NUMEROTEE_OU_NOMMEE RNON WHERE id IN ('ROUTNOMM0000000041519301', 'ROUTNOMM0000000106099019', 'ROUTNOMM0000000041519302')

SELECT * FROM BD_TOPO.IMPORT_LINEAR_GROUP_ROUTE ILGR  WHERE code = 'N41'

SELECT * FROM REF_GEO.T_LINEAR_GROUPS TLG WHERE code='D9B (92)'



SELECT * FROM REF_GEO.L_LINEARS LL WHERE linear_code = 'TRONROUT0000002327226040'

SELECT * FROM BD_TOPO.IMPORT_LINEAR_ROUTE ILR WHERE LINEAR_CODE  = 'TRONROUT0000002327226040'

WITH unnest_ AS (
SELECT UNNEST(STRING_TO_ARRAY(groups, ',')) code
FROM BD_TOPO.import_linear_route i
)
SELECT *
FROM UNNEST_ u
LEFT JOIN REF_GEO.T_LINEAR_GROUPS TLG ON tlg.CODE = u.code
WHERE TLG.ID_GROUP IS NULL



SELECT
  (SELECT string_agg(ref_geo.t_linear_groups.name, ', ') AS string_agg_1
   FROM ref_geo.t_linear_groups
        JOIN ref_geo.cor_linear_group ON ref_geo.cor_linear_group.id_group = ref_geo.t_linear_groups.id_group
        JOIN ref_geo.l_linears ON ref_geo.cor_linear_group.id_group = ref_geo.t_linear_groups.id_group
        JOIN pr_sipaf.cor_linear_pf ON pr_sipaf.cor_linear_pf.id_linear = ref_geo.l_linears.id_linear
   WHERE pr_sipaf.cor_linear_pf.id_passage_faune = pr_sipaf.t_passages_faune.id_passage_faune) AS anon_1,
                pr_sipaf.t_passages_faune.id_passage_faune
FROM pr_sipaf.t_passages_faune