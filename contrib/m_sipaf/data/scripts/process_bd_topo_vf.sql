-- DROP TABLE IF EXISTS bd_topo.voie_ferree_nommee
-- DROP TABLE IF EXISTS bd_topo.troncon_de_voie_ferree


    -- supprimer les doublons
    -- voie ferre
WITH keep_id AS (
    SELECT
        id,
        min(gid) AS gid
    FROM
        BD_TOPO.VOIE_FERREE_NOMMEE d
    GROUP BY
        id
)
DELETE
FROM
    BD_TOPO.VOIE_FERREE_NOMMEE d
        USING keep_id k
WHERE
    d.id = k.id
    AND k.gid != d.gid;

-- voie ferre
WITH keep_id AS (
SELECT
        id,
    min(gid) AS gid
FROM
    bd_topo.TRONCON_DE_VOIE_FERREE d
GROUP BY
    id
)
DELETE
FROM
    bd_topo.TRONCON_DE_VOIE_FERREE d
        USING keep_id k
WHERE
    d.id = k.id
    AND k.gid != d.gid;
--
--

SELECT UpdateGeometrySRID('bd_topo', 'lignes_par_statut', 'geom', 2154);

do $$
BEGIN
    PERFORM  ST_TRANSFORM(ST_SETSRID(geom, 4326), 2154) FROM BD_TOPO.LIGNES_PAR_STATUT;
    UPDATE BD_TOPO.LIGNES_PAR_STATUT SET geom = ST_TRANSFORM(ST_SETSRID(geom, 4326), 2154);    
    RAISE NOTICE 'ok' ;    
    COMMIT;    
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'BD_TOPO.LIGNES_PAR_STATUT déjà en 2154' ;
    
end $$;


--DROP TABLE BD_TOPO.LIGNES_PAR_STATUT
-- ²SELECT geom FROM BD_TOPO.LIGNES_PAR_STATUT;

DROP TABLE IF EXISTS bd_topo.import_linear_group_vf;
CREATE TABLE bd_topo.import_linear_group_vf AS (
SELECT
    lps.CODE_LIGNE AS code,
    CASE
        WHEN 'Ligne à grande vitesse' = ANY(ARRAY_AGG(DISTINCT lpe.catlig))
            THEN CONCAT('LGV_', lps.code_ligne, ' ', lps.lib_ligne )
        ELSE CONCAT('L_', lps.code_ligne, ' ', lps.lib_ligne )
    END AS name,
    ST_UNION(lps.geom) AS geom
FROM bd_topo.lignes_par_statut lps
JOIN bd_topo.lignes_lgv_et_par_ecartement lpe ON lpe.code_ligne = lps.code_ligne
GROUP BY lps.lib_ligne, lps.code_ligne
);


DROP TABLE IF EXISTS bd_topo.IMPORT_LINEAR_vf;
CREATE TABLE bd_topo.IMPORT_LINEAR_vf AS (
    
SELECT
        TDVF.id AS linear_code,
        STRING_AGG(code, ', ') AS groups,
        CONCAT(STRING_AGG(code, ', '), ' ', tdvf.id) AS linear_name,
        TDVF.geom,
        CASE
            WHEN nature = 'LGV' THEN 'VF_LGV'
            WHEN nature IN ('Voie de service', 'Voie ferrée principale') THEN 'VF_P'
            ELSE NULL
        END AS id_type,
        'IGN BDTOPO 3-3' AS SOURCE,
        TRUE AS ENABLED
        --,
        --'{ "largeur": ' || tdvf.largeur || ' }' AS additional_data
    FROM BD_TOPO.TRONCON_DE_VOIE_FERREE TDVF
    JOIN bd_topo.IMPORT_LINEAR_GROUP_vf g ON ST_DWITHIN(TDVF.GEOM, g.geom, 10)
    WHERE TDVF.NATURE IN ('Voie de service', 'Voie ferrée principale', 'LGV')
    GROUP BY tdvf.id, tdvf.geom, nature, tdvf.largeur
    
    )
    
    