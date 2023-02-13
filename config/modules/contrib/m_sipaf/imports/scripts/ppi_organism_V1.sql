DROP VIEW IF EXISTS :pre_processed_import_view;
CREATE VIEW :pre_processed_import_view AS
SELECT DISTINCT
	concess AS nom_organisme,
	'SIPAF' AS adresse_organisme
	FROM :raw_import_table t
	WHERE concess IS NOT NULL AND concess != ''
	ORDER BY concess
