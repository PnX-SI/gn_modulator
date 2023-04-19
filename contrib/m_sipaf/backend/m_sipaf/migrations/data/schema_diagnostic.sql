-- schema diagnostic
-- table diagnostic
CREATE TABLE pr_sipaf.t_diagnostics (
    id_diagnostic SERIAL NOT NULL,
    id_passage_faune INTEGER NOT NULL,
    id_role INTEGER,
    id_organisme INTEGER,
    date_diagnostic DATE NOT NULL,
    commentaire_diagnostic VARCHAR,
    commentaire_perturbation_obstacle VARCHAR,
    obstacle_autre VARCHAR,
    perturbation_autre VARCHAR,
    id_nomenclature_diagnostic_ouvrage_hydrau_racc_banq INTEGER,
    amenagement_biodiv_autre VARCHAR
);

ALTER TABLE
    pr_sipaf.t_diagnostics
ADD
    CONSTRAINT pk_sipaf_t_diagnostic_id_diagnostic PRIMARY KEY (id_diagnostic);

ALTER TABLE
    pr_sipaf.t_diagnostics
ADD
    CONSTRAINT fk_sipaf_t_diag_t_pf_id_passage_faune FOREIGN KEY (id_passage_faune) REFERENCES pr_sipaf.t_passages_faune(id_passage_faune) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.t_diagnostics
ADD
    CONSTRAINT fk_sipaf_t_diag_t_rol_id_role FOREIGN KEY (id_role) REFERENCES utilisateurs.t_roles(id_role) ON UPDATE CASCADE ON DELETE
SET
    NULL;

ALTER TABLE
    pr_sipaf.t_diagnostics
ADD
    CONSTRAINT fk_sipaf_t_diag_b_org_id_organisme FOREIGN KEY (id_organisme) REFERENCES utilisateurs.bib_organismes(id_organisme) ON UPDATE CASCADE ON DELETE
SET
    NULL;

-- cor diag nomenclature obstacle
CREATE TABLE IF NOT EXISTS pr_sipaf.cor_diag_nomenclature_obstacle (
    id_diagnostic INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_obstacle
ADD
    CONSTRAINT pk_pr_sipaf_cor_diag_nomenclature_obstacle_id_diagnostic_id_nomenclature PRIMARY KEY (id_diagnostic, id_nomenclature);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_obstacle
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_obstacle_id_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES pr_sipaf.t_diagnostics (id_diagnostic) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_obstacle
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_obstacle_id_nomenclature FOREIGN KEY (id_nomenclature) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

-- cor diag nomenclature perturbation
CREATE TABLE IF NOT EXISTS pr_sipaf.cor_diag_nomenclature_perturbation (
    id_diagnostic INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_perturbation
ADD
    CONSTRAINT pk_pr_sipaf_cor_diag_nomenclature_perturbation_id_diagnostic_id_nomenclature PRIMARY KEY (id_diagnostic, id_nomenclature);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_perturbation
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_perturbation_id_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES pr_sipaf.t_diagnostics (id_diagnostic) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_perturbation
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_perturbation_id_nomenclature FOREIGN KEY (id_nomenclature) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.t_diagnostics
ADD
    CONSTRAINT fk_pr_sipaf_t_d_id_nomenclature_diagnostic_ouvrage_hydrau_racc_banq FOREIGN KEY (
        id_nomenclature_diagnostic_ouvrage_hydrau_racc_banq
    ) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

-- cor diag nomenclature ouvrage_hydrau_etat_berge
CREATE TABLE IF NOT EXISTS pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_etat_berge (
    id_diagnostic INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_etat_berge
ADD
    CONSTRAINT pk_ouvrage_hydray_etat_berge_id_diagnostic_id_nomenclature PRIMARY KEY (id_diagnostic, id_nomenclature);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_etat_berge
ADD
    CONSTRAINT fk_ouvrage_hydray_etat_berge_id_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES pr_sipaf.t_diagnostics (id_diagnostic) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_etat_berge
ADD
    CONSTRAINT fk_ouvrage_hydray_etat_berge_id_nomenclature FOREIGN KEY (id_nomenclature) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

-- cor diag nomenclature ouvrage_hydreau_dimensionnement
CREATE TABLE IF NOT EXISTS pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_dim (
    id_diagnostic INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_dim
ADD
    CONSTRAINT pk_pr_sipaf_cor_diag_nomenclature_ouvrage_hydrau_dim_id_diagnostic_id_nomenclature PRIMARY KEY (id_diagnostic, id_nomenclature);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_dim
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_ouvrage_hydrau_dim_id_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES pr_sipaf.t_diagnostics (id_diagnostic) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_dim
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_ouvrage_hydrau_dim_id_nomenclature FOREIGN KEY (id_nomenclature) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

-- cor diag nomenclature amenagement_biodiv
CREATE TABLE IF NOT EXISTS pr_sipaf.cor_diag_nomenclature_amenagement_biodiv (
    id_diagnostic INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_amenagement_biodiv
ADD
    CONSTRAINT pk_pr_sipaf_cor_diag_nomenclature_amenagement_biodiv_id_diagnostic_id_nomenclature PRIMARY KEY (id_diagnostic, id_nomenclature);

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_amenagement_biodiv
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_amenagement_biodiv_id_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES pr_sipaf.t_diagnostics (id_diagnostic) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_amenagement_biodiv
ADD
    CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_amenagement_biodiv_id_nomenclature FOREIGN KEY (id_nomenclature) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

-- clôture guidage
CREATE TABLE IF NOT EXISTS pr_sipaf.t_diagnostic_clotures (
    id_diagnostic SERIAL NOT NULL NOT NULL,
    id_nomenclature_clotures_guidage_type INTEGER NOT NULL NOT NULL,
    id_nomenclature_clotures_guidage_etat INTEGER NOT NULL NOT NULL,
    clotures_guidage_type_autre VARCHAR,
    clotures_guidage_etat_autre VARCHAR
);

ALTER TABLE
    pr_sipaf.t_diagnostic_clotures
ADD
    CONSTRAINT pk_sipaf_t_diagnostic_clotures PRIMARY KEY (id_diagnostic, id_nomenclature_clotures_guidage_type);

ALTER TABLE
    pr_sipaf.t_diagnostic_clotures
ADD
    CONSTRAINT fk_pr_sipaf_t_diagnostic_clotures_id_diagnostic FOREIGN KEY (id_diagnostic) REFERENCES pr_sipaf.t_diagnostics (id_diagnostic) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.t_diagnostic_clotures
ADD
    CONSTRAINT fk_pr_sipaf_t_d_c_g_id_nomenclature_clotures_guidage_type FOREIGN KEY (id_nomenclature_clotures_guidage_type) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    pr_sipaf.t_diagnostic_clotures
ADD
    CONSTRAINT fk_pr_sipaf_t_d_c_g_id_nomenclature_clotures_guidage_etat FOREIGN KEY (id_nomenclature_clotures_guidage_etat) REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) ON UPDATE CASCADE ON DELETE CASCADE;


-- check constraint nomenclature type
ALTER TABLE
    pr_sipaf.t_diagnostics
ADD
    CONSTRAINT check_nom_type_diag_ouvr_hydrau_racc_banq_id_ure_pf_ype CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(
            id_nomenclature_diagnostic_ouvrage_hydrau_racc_banq,
            'PF_DIAG_OUVRAGE_HYDRAULIQUE_RACCORDEMENT_BANQUETTE'
        )
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_obstacle
ADD
    CONSTRAINT check_nom_type_pr_sipaf_cor_diag_nomenclature_obstacle_id_ure_pf_ype CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature, 'PF_DIAG_OBSTACLE')
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.t_diagnostic_clotures
ADD
    CONSTRAINT check_nom_type_diag_clot_gui_type CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(
            id_nomenclature_clotures_guidage_type,
            'PF_DIAG_CLOTURES_GUIDAGE_TYPE'
        )
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.t_diagnostic_clotures
ADD
    CONSTRAINT check_nom_type_diag_clot_gui_etat CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(
            id_nomenclature_clotures_guidage_etat,
            'PF_DIAG_CLOTURES_GUIDAGE_ETAT'
        )
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_amenagement_biodiv
ADD
    CONSTRAINT check_nom_type_pr_sipaf_cor_diag_nomenclature_amenagement_biodiv_id_ure_pf_ype CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature, 'PF_DIAG_AMENAGEMENT_BIODIV')
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_dim
ADD
    CONSTRAINT check_nom_type_pr_sipaf_cor_diag_nomenclature_ouvrage_hydrau_dim_id_ure_pf_ype CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(
            id_nomenclature,
            'PF_DIAG_OUVRAGE_HYDRAU_DIMENSIONNEMENT'
        )
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_etat_berge
ADD
    CONSTRAINT check_nom_type_ouvrage_hydrau_etat_berge_id_ure_pf_ype CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(
            id_nomenclature,
            'PF_DIAG_OUVRAGE_HYDRAULIQUE_ETAT_BERGE'
        )
    ) NOT VALID;

ALTER TABLE
    pr_sipaf.cor_diag_nomenclature_perturbation
ADD
    CONSTRAINT check_nom_type_pr_sipaf_cor_diag_nomenclature_perturbation_id_ure_pf_ype CHECK (
        ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature, 'PF_DIAG_PERTURBATION')
    ) NOT VALID;