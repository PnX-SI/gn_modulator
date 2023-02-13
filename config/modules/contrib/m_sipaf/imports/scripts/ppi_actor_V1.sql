DROP VIEW IF EXISTS :pre_processed_import_view;
CREATE VIEW :pre_processed_import_view AS
SELECT
	uuid_pf AS id_passage_faune,
    'CON' AS id_nomenclature_type_actor,
	concess AS id_organism,
    NULL AS id_role
	FROM :raw_import_table t
	WHERE concess IS NOT NULL AND concess != ''
;

