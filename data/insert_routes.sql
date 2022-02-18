-- insert des données routes depuis
--   sipaf.tmp_import_autoroutes
--   sipaf.tmp_import_routes_nationales

WITH raw_routes AS (
	SELECT num_route, geom
		FROM sipaf.tmp_import_autoroutes
	UNION
	SELECT num_route, geom
		FROM sipaf.tmp_import_routes_nationales tirn2
), routes AS (
    SELECT
	    num_route,
	    st_transform(st_multi(ST_UNION(st_force2d(geom))), 2154) AS geom

	    FROM raw_routes
	    GROUP BY num_route
)
INSERT INTO sipaf.l_infrastructures (
	infrastructure_name,
	infrastructure_number,
	geom,
	id_nomenclature_infrastructure_type
)
SELECT
	r.num_route AS area_code,
	NULLIF(regexp_replace(r.num_route , '[^\.\d]','','g'), '')::numeric AS infrastructure_number,
	geom,
	CASE
		WHEN r.num_route LIKE 'N%' THEN ref_nomenclatures.get_id_nomenclature('PF_INFRASTRUCTURE_TYPE', 'RN')
		WHEN r.num_route LIKE 'A%' THEN ref_nomenclatures.get_id_nomenclature('PF_INFRASTRUCTURE_TYPE', 'AU')
		ELSE NULL
	END
FROM routes r

