DROP FUNCTION IF EXISTS isnumeric(text);

CREATE OR REPLACE FUNCTION isnumeric(text) RETURNS BOOLEAN AS $$
DECLARE x NUMERIC;
BEGIN
    x = $1::NUMERIC;
    RETURN TRUE;
EXCEPTION WHEN others THEN
    RETURN FALSE;
END;
$$
STRICT
LANGUAGE plpgsql IMMUTABLE;

DROP FUNCTION IF EXISTS sipaf.correct_number(VARCHAR);

CREATE OR REPLACE FUNCTION sipaf.correct_number(number_in varchar)
    RETURNS FLOAT AS $$
    DECLARE inter VARCHAR;
    DECLARE n_out FLOAT;

    BEGIN
        SELECT INTO inter REPLACE(number_in, '?', '');
        SELECT INTO inter REPLACE(inter, ',', '.');

        -- nettoyage à faire par les gestionnaire de données
        if NOT isnumeric(inter)
            THEN RETURN NULL;
        end if;


        SELECT INTO n_out NULLIF(inter, '')::float;



        RETURN n_out;
    END;
    $$
    LANGUAGE plpgsql;

TRUNCATE sipaf.t_passages_faune;


INSERT INTO sipaf.t_passages_faune(
    id_pf,
	id_dataset,
    uuid_pf,
    pi_ou_ps,
	geom,
	PK,
	PR,
	PR_abs,
	Y,
	X,
	id_op,
	nom_pf,
	Cd_Com,
	an_ref_com,
	issu_requa,
	date_creat,
	date_requal,
	larg_ouvrag,
	haut_ouvrag,
	long_franch,
	diam,
	haut_disp,
	larg_disp,
	specificit,
	lb_typ_ouv,
	lb_materiaux,
	ep_materiaux,
	OH,
	OH_position,
	OH_caract,
	OH_banqu,
	OH_tirant,
	id_cer,
	id_corr,
	nom_corr,
	id_resv,
	nom_resv,
	id_obst,
	nom_obst,
	comment,
	id_nomenclature_materiaux,
	id_nomenclature_oh_position,
	id_nomenclature_oh_banq_caract,
	id_nomenclature_oh_banq_type
)
WITH non_doublons AS (
	SELECT id_pf
	FROM tmp_import_sipaf tis
	GROUP BY id_pf
	HAVING COUNT(*) = 1
)
SELECT
    i.id_pf::INT,
	d.id_dataset,
    COALESCE(uuid_pf::UUID, uuid_generate_v4()),
    pi_ou_ps,
	CASE
		WHEN (sipaf.correct_number(X) IS NOT NULL) AND (sipaf.correct_number(Y) IS NOT NULL)
			THEN ST_SetSRID(ST_Point(sipaf.correct_number(X), sipaf.correct_number(Y)), 4326)
		ELSE
			NULL
	END as geom,
	sipaf.correct_number(PK),
	sipaf.correct_number(PR),
	sipaf.correct_number(PR_abs),
    sipaf.correct_number(Y),
    sipaf.correct_number(X),
	id_op,
	nom_pf,
	Cd_Com,
	anRefCom,
	issu_requa,
	date_creat,
	date_requal,
	sipaf.correct_number(larg_ouvrag),
	sipaf.correct_number(haut_ouvrag),
	sipaf.correct_number(long_franch),
	sipaf.correct_number(diam),
	sipaf.correct_number(haut_disp),
	sipaf.correct_number(larg_disp),
	specificit,
	lb_typ_ouv,
	lb_materiaux,
	sipaf.correct_number(ep_materiaux),
	OH,
	OH_position,
	OH_caract,
	OH_banqu,
	OH_tirant,
	id_cer,
	id_corr,
	nom_corr,
	id_resv,
	nom_resv,
	id_obst,
	nom_obst,
	comment,
	CASE
		WHEN TRIM(lb_materiaux) = 'Béton' THEN ref_nomenclatures.get_id_nomenclature('PF_MATERIAUX', 'BET')
		WHEN TRIM(lb_materiaux) = 'Métal' THEN ref_nomenclatures.get_id_nomenclature('PF_MATERIAUX', 'MET')
		ELSE NULL
	END,

	NULL,
	NULL,
	NULL
    FROM public.tmp_import_sipaf i
	JOIN non_doublons nd on nd.id_pf = i.id_pf
	JOIN gn_meta.t_datasets d on d.dataset_name = 'test jdd passage faune'
    WHERE i.id_pf IS NOT NULL;