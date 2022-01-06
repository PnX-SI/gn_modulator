-- all pf

UPDATE sipaf.t_passages_faune pf SET id_dataset = d.id_dataset
	FROM gn_meta.t_datasets d
	WHERE dataset_name = 'SIPAF';

-- Occitanie
WITH pf_occ AS (
	SELECT 
		id_dataset,
		id_pf
	FROM sipaf.cor_area_pf cap 
	JOIN gn_meta.t_datasets td ON td.dataset_name = 'SIPAF Occitanie'
	JOIN ref_geo.l_areas la ON cap.id_area = la.id_area 
	JOIN ref_geo.bib_areas_types bat ON bat.id_type = la.id_type
	WHERE bat.type_code = 'DEP'
		AND la.area_code IN ('09', '11', '12', '30', '31', '32', '34', '46', '48', '65', '66', '81', '82')
)
UPDATE sipaf.t_passages_faune pf SET id_dataset = n.id_dataset
	FROM pf_occ n
	WHERE pf.id_pf = n.id_pf 
;

-- RN 106

WITH pf_N106 AS (
	SELECT 
		id_dataset,
		id_pf
	FROM sipaf.l_routes r
	JOIN gn_meta.t_datasets td ON td.dataset_name = 'SIPAF RN_106'
	JOIN sipaf.cor_route_pf crp ON crp.id_route = r.id_route
	WHERE r.route_name = 'N106'
)
UPDATE sipaf.t_passages_faune pf SET id_dataset = n.id_dataset
	FROM pf_N106 n
	WHERE pf.id_pf = n.id_pf 
;