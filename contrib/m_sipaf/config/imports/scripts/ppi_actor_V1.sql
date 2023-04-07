SELECT
	id_import,
	uuid_pf AS id_passage_faune,
    'CON' AS id_nomenclature_type_actor,
	concess AS id_organism,
    NULL AS id_role
    FROM :table_data
	WHERE concess IS NOT NULL AND concess != ''
;

