SELECT DISTINCT ON (id_import)
	concess AS nom_organisme,
	'SIPAF' AS adresse_organisme
	WHERE concess IS NOT NULL AND concess != ''
	FROM :table_data
	ORDER BY id_import, concess
