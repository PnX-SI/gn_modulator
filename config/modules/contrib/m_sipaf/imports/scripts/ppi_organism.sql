DROP VIEW IF EXISTS :pre_processed_import_view;
CREATE VIEW :pre_processed_import_view AS
SELECT DISTINCT
	nom_organism AS nom_organisme,
	'SIPAF' AS adresse_organisme
	FROM :raw_import_table t
	WHERE nom_organism IS NOT NULL AND nom_organism != ''
	ORDER BY nom_organism
