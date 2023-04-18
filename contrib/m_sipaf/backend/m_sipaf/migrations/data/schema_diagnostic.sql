-- schema diagnostic

    -- table diagnostic

    CREATE TABLE pr_sipaf.t_diagnostics (
        id_diagnostic SERIAL NOT NULL,
        id_passage_faune INTEGER NOT NULL,
        id_role INTEGER,
        id_organisme INTEGER,
        date_diagnostic DATE NOT NULL,
        comment VARCHAR,
        obstacle_autre VARCHAR
    );

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT pk_sipaf_t_diagnostic_id_diagnostic PRIMARY KEY (id_diagnostic);

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT fk_sipaf_t_diag_t_pf_id_passage_faune FOREIGN KEY (id_passage_faune)
        REFERENCES pr_sipaf.t_passages_faune(id_passage_faune)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT fk_sipaf_t_diag_t_rol_id_role FOREIGN KEY (id_role)
        REFERENCES utilisateurs.t_roles(id_role)
        ON UPDATE CASCADE ON DELETE SET NULL;

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT fk_sipaf_t_diag_b_org_id_organisme FOREIGN KEY (id_organisme)
        REFERENCES utilisateurs.bib_organismes(id_organisme)
        ON UPDATE CASCADE ON DELETE SET NULL;


    -- cor diag nomenclature obstacle
    CREATE TABLE IF NOT EXISTS pr_sipaf.cor_diag_nomenclature_obstacle (
        id_diagnostic INTEGER NOT NULL NOT NULL,
        id_nomenclature INTEGER NOT NULL NOT NULL
    );

    ALTER TABLE pr_sipaf.cor_diag_nomenclature_obstacle
        ADD CONSTRAINT pk_pr_sipaf_cor_diag_nomenclature_obstacle_id_diagnostic_id_nomenclature PRIMARY KEY (id_diagnostic, id_nomenclature);

    ALTER TABLE pr_sipaf.cor_diag_nomenclature_obstacle
        ADD CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_obstacle_id_diagnostic FOREIGN KEY (id_diagnostic)
        REFERENCES pr_sipaf.t_diagnostics (id_diagnostic)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.cor_diag_nomenclature_obstacle
        ADD CONSTRAINT fk_pr_sipaf_cor_diag_nomenclature_obstacle_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.cor_diag_nomenclature_obstacle
            ADD CONSTRAINT check_nom_type_pr_sipaf_cor_diag_nomenclature_obstacle_id_ure_pf_ype
            CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature,'PF_DIAG_OBSTACLE'))
            NOT VALID;
