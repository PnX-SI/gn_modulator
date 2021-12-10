
-- process schema : schemas.sipaf.pf


---- sql schema sipaf

CREATE SCHEMA IF NOT EXISTS sipaf;

---- table sipaf.t_passages_faune

CREATE TABLE IF NOT EXISTS sipaf.t_passages_faune (
    id_pf SERIAL NOT NULL,
    id_dataset INTEGER,
    id_op VARCHAR,
    an_ref_com VARCHAR,
    issu_requa VARCHAR,
    id_nomenclature_materiaux INTEGER,
    id_nomenclature_oh_position INTEGER,
    id_nomenclature_oh_banq_caract INTEGER,
    id_nomenclature_oh_banq_type INTEGER,
    uuid_pf UUID,
    pi_ou_ps VARCHAR,
    pk FLOAT,
    pr FLOAT,
    pr_abs FLOAT,
    x FLOAT,
    y FLOAT,
    nom_pf VARCHAR,
    cd_com VARCHAR,
    date_creat VARCHAR,
    date_requal VARCHAR,
    larg_ouvrag FLOAT,
    haut_ouvrag FLOAT,
    long_franch FLOAT,
    diam FLOAT,
    larg_disp FLOAT,
    haut_disp FLOAT,
    specificit VARCHAR,
    lb_typ_ouv VARCHAR,
    lb_materiaux VARCHAR,
    ep_materiaux FLOAT,
    oh VARCHAR,
    oh_position VARCHAR,
    oh_caract VARCHAR,
    oh_banqu VARCHAR,
    oh_tirant VARCHAR,
    id_cer VARCHAR,
    id_corr VARCHAR,
    nom_corr VARCHAR,
    id_resv VARCHAR,
    nom_resv VARCHAR,
    id_obst VARCHAR,
    nom_obst VARCHAR,
    comment VARCHAR,
    geom GEOMETRY(POINT, 4326)
);

---- sipaf.t_passages_faune primary key constraint
ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS pk_sipaf_t_passages_faune_id_pf;
ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT pk_sipaf_t_passages_faune_id_pf PRIMARY KEY (id_pf);

---- sipaf.t_passages_faune foreign key constraint
ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS fk_sipaf_t_pas_t_dat_id_dataset;
ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_dat_id_dataset FOREIGN KEY (id_dataset)
    REFERENCES gn_meta.t_datasets(id_dataset)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint
ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS fk_sipaf_t_pas_t_nom_id_nomenclature_materiaux;
ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_materiaux FOREIGN KEY (id_nomenclature_materiaux)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint
ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS fk_sipaf_t_pas_t_nom_id_nomenclature_oh_position;
ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_position FOREIGN KEY (id_nomenclature_oh_position)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint
ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_caract;
ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_caract FOREIGN KEY (id_nomenclature_oh_banq_caract)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint
ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_type;
ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_type FOREIGN KEY (id_nomenclature_oh_banq_type)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;


---- nomenclature check type constraints

ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS check_nom_type_sipaf_t_passages_faune_pf_materiaux;
ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_materiaux
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_materiaux,'PF_MATERIAUX'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS check_nom_type_sipaf_t_passages_faune_pf_oh_position;
ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_oh_position
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_position,'PF_OH_POSITION'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS check_nom_type_sipaf_t_passages_faune_pf_oh_banq_caract;
ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_oh_banq_caract
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_banq_caract,'PF_OH_BANQ_CARACT'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune DROP CONSTRAINT IF EXISTS check_nom_type_sipaf_t_passages_faune_pf_oh_banq_type;
ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_oh_banq_type
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_banq_type,'PF_OH_BANQ_TYPE'))
        NOT VALID;



