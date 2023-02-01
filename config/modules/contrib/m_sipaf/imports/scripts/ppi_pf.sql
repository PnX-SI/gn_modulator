

--DROP FUNCTION IF EXISTS process_number;
CREATE OR REPLACE FUNCTION process_number(n_in text) RETURNS NUMERIC AS $$
DECLARE x NUMERIC;
DECLARE inter TEXT;
BEGIN
	inter := n_in;
    SELECT INTO inter REPLACE(inter, ',', '.');
    x = inter::NUMERIC;
    RETURN x;
EXCEPTION
	WHEN others THEN
    RETURN CASE
   		WHEN n_in IS NULL OR n_in = '' THEN NULL
   		ELSE NULL
   	END;
END;
$$
STRICT
LANGUAGE plpgsql IMMUTABLE;

--DROP FUNCTION IF EXISTS process_integer;
CREATE OR REPLACE FUNCTION process_integer(n_in text) RETURNS INTEGER AS $$
DECLARE x INTEGER;
DECLARE inter TEXT;
BEGIN
	inter := n_in;
    x = inter::INTEGER;
    RETURN x;
EXCEPTION
	WHEN others THEN
    RETURN CASE
   		WHEN n_in IS NULL OR n_in = '' THEN NULL
   		ELSE NULL
   	END;
END;
$$
STRICT
LANGUAGE plpgsql IMMUTABLE;


--DROP FUNCTION IF EXISTS  check_number(TEXT, TEXT, TEXT) ;
CREATE OR REPLACE FUNCTION check_number(
	col_num_in TEXT,
	col_id_in TEXT,
	table_in TEXT
)
RETURNS TABLE(id text, value text) AS
$$
	BEGIN
		RETURN QUERY EXECUTE  FORMAT('
			SELECT %I::text as id, %I::text as value
			FROM %s
			WHERE process_number(%I) = double precision ''NaN''
		', col_id_in, col_num_in, table_in, col_num_in);
	END;
$$
STRICT
LANGUAGE plpgsql IMMUTABLE;

DROP TABLE IF EXISTS corr_type_ouv CASCADE;
CREATE TABLE corr_type_ouv(
cd_nomenclature TEXT,
mot TEXT,
UNIQUE(cd_nomenclature, mot)
);


INSERT INTO corr_type_ouv
VALUES ('BUS', 'buse'),
('ARC', 'Arc'),
('CAD', 'cadre'),
('DAL', 'dalle'),
('VIA', 'Viaduc'),
('VOU', 'Voute'),
('VOU', 'Vo?t?'),
('PON', 'Pont'),
('CAN', 'Canalisation'),
('DIAB', 'Diabolo'),
('DALO', 'Dalot'),
('TRA', 'Tranch'),
('TUN', 'Tunnel'),
('POR', 'portique')
ON CONFLICT DO NOTHING;

DROP VIEW IF EXISTS :pre_processed_import_view;
CREATE VIEW :pre_processed_import_view AS
WITH
	doublons AS (
		SELECT MIN(id_import) AS id_import, uuid_pf
		FROM :raw_import_table
		WHERE uuid_pf != '' OR uuid_pf IS NOT NULL
		GROUP BY uuid_pf
		ORDER BY uuid_pf
	),
	type_ouv AS (
	SELECT
		uuid_pf,
		string_agg(DISTINCT  cd_nomenclature, ',') AS nomenclatures_ouvrage_type
	FROM :raw_import_table tis
	JOIN corr_type_ouv cto
		ON UNACCENT(tis.lb_typ_ouv) ILIKE '%' || cto.mot || '%'
	WHERE lb_typ_ouv != ''
	GROUP BY uuid_pf
)
SELECT
	-- tis.uuid_pf AS id_passage_faune,
	tis.uuid_pf AS code_passage_faune,
	CASE
		WHEN pi_ou_ps LIKE 'PI%' THEN FALSE
		WHEN pi_ou_ps LIKE 'PS%' THEN TRUE
		WHEN pi_ou_ps = '' THEN NULL
		ELSE NULL
	END AS pi_ou_ps,
	st_asewkt(st_makepoint(process_number(x), process_number(y), 4326)) AS GEOM,
	process_number(pk) AS pk,
	process_integer(pr) AS pr,
	process_integer(pr_abs) AS pr_abs,
	id_op AS code_ouvrage_gestionnaire,
	nom_pf AS nom_usuel_passage_faune,
	CASE
		WHEN process_number(date_creat) != double PRECISION 'NaN'
			THEN TO_DATE(process_number(date_creat)::text, 'yyyy')
		ELSE NULL
	END AS date_creation_ouvrage,
	CASE
		WHEN process_number(date_requal) != double PRECISION 'NaN'
			THEN TO_DATE(process_number(date_requal)::text, 'yyyy')
		ELSE NULL
	END	AS date_requalification_ouvrage,
	CASE
		WHEN process_number(date_requal) != double PRECISION 'NaN'
			THEN date_requal != ''
		ELSE NULL
	END	AS issu_requalification,
	process_number(larg_ouvrag) AS largeur_ouvrage,
	process_number(haut_ouvrag) AS hauteur_ouvrage,
	process_number(long_franch) AS longueur_franchissement,
	process_number(diam) AS diametre,
	process_number(larg_disp) AS largeur_dispo_faune,
	process_number(haut_disp) AS hauteur_dispo_faune,
	CASE
		WHEN specificit ILIKE '%mixte%' THEN 'MIX'
		WHEN
			specificit ILIKE '%sp%cifique%'
			OR specificit IN ('Amphibiens', 'Batraciens', 'Boviduc', 'Crapauduc', 'Faune')
			OR specificit ILIKE '%GF%'
			OR specificit ILIKE '%PPF%'
			OR specificit ILIKE '%PF%'
			OR specificit ILIKE '%BESTIAUX%'
			OR specificit ILIKE '%gibier%'
			OR specificit ILIKE '%pas%'
			OR specificit IN ('PF', 'PGF', 'PPF', 'PB', 'PP', 'S')
			THEN 'SPE'
		WHEN
			specificit ILIKE '%non dedie%'
			OR specificit IN ('H', 'M', 'Non')
			THEN 'ND'
		WHEN specificit IN  ('', '?', 'coudée', 'immergée') THEN NULL
		ELSE '???'
	END AS id_nomenclature_ouvrage_specificite,
	tou.nomenclatures_ouvrage_type,
	CASE
		WHEN UNACCENT(TRIM(lb_materiaux)) ILIKE '%Beton%' THEN 'BET'
		WHEN UNACCENT(TRIM(lb_materiaux))  ILIKE '%Metal%' THEN 'MET'
		ELSE NULL
	END AS nomenclatures_ouvrage_materiaux,
	CASE
		WHEN oh = 'Oui' THEN TRUE
		WHEN oh = 'Non' THEN FALSE
		ELSE NULL
	END AS ouvrage_hydrau
	FROM :raw_import_table tis
	JOIN doublons dbl ON dbl.id_import = tis.id_import
	LEFT JOIN type_ouv tou ON tou.uuid_pf = tis.uuid_pf
	ORDER BY tis.uuid_pf
;