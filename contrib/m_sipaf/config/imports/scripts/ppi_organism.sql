SELECT DISTINCT ON (id_import)
	id_import,
	nom_organism AS nom_organisme,
	'SIPAF' AS adresse_organisme
	WHERE nom_organism IS NOT NULL AND nom_organism != ''
	FROM :table_data
	ORDER BY id_import, nom_organism
