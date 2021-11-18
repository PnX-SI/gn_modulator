
-- process schema : schemas.sipaf.pf


---- sql schema sipaf

CREATE SCHEMA sipaf;

---- table sipaf.t_passages_faune

CREATE TABLE  sipaf.t_passages_faune (
    id_pf SERIAL NOT NULL,
    id_op VARCHAR,
    an_ref_com VARCHAR,
    issu_requa VARCHAR,
    id_nomenclature_materiaux INTEGER,
    id_nomenclature_oh_position INTEGER,
    id_nomenclature_oh_banq_caract INTEGER,
    id_nomenclature_oh_banq_type INTEGER,
    uuid_pf VARCHAR,
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

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT pk_sipaf_t_passages_faune_id_pf PRIMARY KEY (id_pf);

---- sipaf.t_passages_faune foreign key constraint

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_materiaux FOREIGN KEY (id_nomenclature_materiaux)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_position FOREIGN KEY (id_nomenclature_oh_position)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_caract FOREIGN KEY (id_nomenclature_oh_banq_caract)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;
---- sipaf.t_passages_faune foreign key constraint

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_type FOREIGN KEY (id_nomenclature_oh_banq_type)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;


---- nomenclature check type constraints

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_sipaf_t_passages_faune_pf_materiaux
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_materiaux,'PF_MATERIAUX'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_sipaf_t_passages_faune_pf_oh_position
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_position,'PF_OH_POSITION'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_sipaf_t_passages_faune_pf_oh_banq_caract
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_banq_caract,'PF_OH_BANQ_CARACT'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_sipaf_t_passages_faune_pf_oh_banq_type
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_banq_type,'PF_OH_BANQ_TYPE'))
        NOT VALID;



