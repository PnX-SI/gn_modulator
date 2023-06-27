SELECT
	MIN(id_import) AS id_import,
	concess AS nom_organisme,
	'SIPAF' AS adresse_organisme
	FROM :table_data
	WHERE concess IS NOT NULL AND concess != ''
	GROUP BY concess
	ORDER BY concess
