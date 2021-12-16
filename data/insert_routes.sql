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
	    st_multi(ST_UNION(st_force2d(ST_TRANSFORM(geom, 4326)))) AS geom
	    FROM raw_routes
	    GROUP BY num_route
)
INSERT INTO sipaf.l_routes (
	route_name,
	geom
)
SELECT
	r.num_route AS area_code,
	geom
FROM routes r

