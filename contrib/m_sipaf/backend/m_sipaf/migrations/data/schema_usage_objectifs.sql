    -- table usage
    CREATE TABLE pr_sipaf.t_usages (
        id_usage SERIAL NOT NULL,
        id_passage_faune INTEGER NOT NULL,
        id_nomenclature_usage_type INTEGER NOT NULL,
        detail_usage VARCHAR,
        commentaire VARCHAR
    );

    ALTER TABLE pr_sipaf.t_usages
        ADD CONSTRAINT pk_pr_sipaf_t_usage_id_usage PRIMARY KEY (id_usage)
    ;

    ALTER TABLE pr_sipaf.t_usages
        ADD CONSTRAINT fk_pr_sipaf_usage_pf_id_passage_faune FOREIGN KEY (id_passage_faune)
        REFERENCES pr_sipaf.t_passages_faune(id_passage_faune)
        ON UPDATE CASCADE ON DELETE CASCADE
    ;

    ALTER TABLE pr_sipaf.t_usages
        ADD CONSTRAINT fk_pr_sipaf_usage_nom_id_nomenclature_usage_type FOREIGN KEY (id_nomenclature_usage_type)
        REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
        ON UPDATE CASCADE ON DELETE CASCADE
    ;

    ALTER TABLE pr_sipaf.t_usages
            ADD CONSTRAINT check_nom_type_pr_sipaf_usage_nomenclature_ouvrage_categorie_id_ure_pf_ype
                CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_usage_type,'PF_USAGE_CATEGORIE'))
            NOT VALID;


    -- nomenclatures_categorie_ouvrage

    CREATE TABLE IF NOT EXISTS pr_sipaf.cor_pf_nomenclature_ouvrage_categorie (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);

    ---- pr_sipaf.cor_pf_nomenclature_ouvrage_categorie primary keys contraints

    ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_categorie
        ADD CONSTRAINT pk_pr_sipaf_cor_pf_nomenclature_ouvrage_categorie_id_pf_id_nom PRIMARY KEY (id_passage_faune, id_nomenclature);

    ---- pr_sipaf.cor_pf_nomenclature_ouvrage_categorie foreign keys contraints

    ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_categorie
        ADD CONSTRAINT fk_pr_sipaf_cor_pf_nomenclature_ouvrage_categorie_id_passage_faune FOREIGN KEY (id_passage_faune)
        REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_categorie
        ADD CONSTRAINT fk_pr_sipaf_cor_pf_nomenclature_ouvrage_categorie_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_categorie
            ADD CONSTRAINT check_nom_type_pr_sipaf_cor_pf_nomenclature_ouvrage_categorie_id_ure_pf_ype
            CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature,'PF_OUVRAGE_CATEGORIE'))
            NOT VALID;


    -- passage faune taxref


    CREATE TABLE IF NOT EXISTS pr_sipaf.cor_pf_taxref (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    cd_nom INTEGER NOT NULL NOT NULL
);

    ---- pr_sipaf.cor_pf_taxref primary keys contraints

    ALTER TABLE pr_sipaf.cor_pf_taxref
        ADD CONSTRAINT pk_pr_sipaf_cor_pf_taxref_id_pf_id_nom PRIMARY KEY (id_passage_faune, cd_nom);

    ---- pr_sipaf.cor_pf_taxref foreign keys contraints

    ALTER TABLE pr_sipaf.cor_pf_taxref
        ADD CONSTRAINT fk_pr_sipaf_cor_pf_taxref_id_passage_faune FOREIGN KEY (id_passage_faune)
        REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.cor_pf_taxref
        ADD CONSTRAINT fk_pr_sipaf_cor_pf_taxref_cd_nom FOREIGN KEY (cd_nom)
        REFERENCES taxonomie.taxref (cd_nom)
        ON UPDATE CASCADE ON DELETE CASCADE;

