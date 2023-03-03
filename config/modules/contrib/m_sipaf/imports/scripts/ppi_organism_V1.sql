SELECT DISTINCT
	concess AS nom_organisme,
	'SIPAF' AS adresse_organisme
	WHERE concess IS NOT NULL AND concess != ''
	ORDER BY concess
