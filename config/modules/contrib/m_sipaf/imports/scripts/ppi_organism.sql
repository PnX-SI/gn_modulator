SELECT DISTINCT
	nom_organism AS nom_organisme,
	'SIPAF' AS adresse_organisme
	WHERE nom_organism IS NOT NULL AND nom_organism != ''
	ORDER BY nom_organism
