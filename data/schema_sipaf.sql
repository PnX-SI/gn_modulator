
-- process schema : schemas.sipaf.pf
--
-- and dependancies : schemas.sipaf.route


---- sql schema sipaf

CREATE SCHEMA IF NOT EXISTS sipaf;

---- table sipaf.t_passages_faune

CREATE TABLE sipaf.t_passages_faune (
    id_pf SERIAL NOT NULL,
    id_op VARCHAR,
    an_ref_com VARCHAR,
    issu_requa VARCHAR,
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
    geom GEOMETRY(POINT, 4326),
    id_dataset INTEGER,
    id_nomenclature_materiaux INTEGER,
    id_nomenclature_oh_position INTEGER,
    id_nomenclature_oh_banq_caract INTEGER,
    id_nomenclature_oh_banq_type INTEGER
);


---- table sipaf.l_routes

CREATE TABLE sipaf.l_routes (
    id_route SERIAL NOT NULL,
    route_name VARCHAR,
    geom GEOMETRY(GEOMETRY, 4326)
);


---- sipaf.t_passages_faune primary key constraint

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT pk_sipaf_t_passages_faune_id_pf PRIMARY KEY (id_pf);


---- sipaf.l_routes primary key constraint

ALTER TABLE sipaf.l_routes
    ADD CONSTRAINT pk_sipaf_l_routes_id_route PRIMARY KEY (id_route);


---- sipaf.t_passages_faune foreign key constraint id_dataset

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_dat_id_dataset FOREIGN KEY (id_dataset)
    REFERENCES gn_meta.t_datasets(id_dataset)
    ON UPDATE CASCADE ON DELETE NO ACTION;

---- sipaf.t_passages_faune foreign key constraint id_nomenclature_materiaux

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_materiaux FOREIGN KEY (id_nomenclature_materiaux)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;

---- sipaf.t_passages_faune foreign key constraint id_nomenclature_oh_position

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_position FOREIGN KEY (id_nomenclature_oh_position)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;

---- sipaf.t_passages_faune foreign key constraint id_nomenclature_oh_banq_caract

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_caract FOREIGN KEY (id_nomenclature_oh_banq_caract)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;

---- sipaf.t_passages_faune foreign key constraint id_nomenclature_oh_banq_type

ALTER TABLE sipaf.t_passages_faune
    ADD CONSTRAINT fk_sipaf_t_pas_t_nom_id_nomenclature_oh_banq_type FOREIGN KEY (id_nomenclature_oh_banq_type)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE NO ACTION;


---- nomenclature check type constraints

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_materiaux
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_materiaux,'PF_MATERIAUX'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_oh_position
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_position,'PF_OH_POSITION'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_oh_banq_caract
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_banq_caract,'PF_OH_BANQ_CARACT'))
        NOT VALID;

ALTER TABLE sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_sipaf_t_passages_faune_pf_oh_banq_type
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_oh_banq_type,'PF_OH_BANQ_TYPE'))
        NOT VALID;


-- cor sipaf.cor_area_pf

CREATE TABLE IF NOT EXISTS sipaf.cor_area_pf (
    id_pf INTEGER NOT NULL,
    id_area INTEGER NOT NULL
);


---- sipaf.cor_area_pf primary keys contraints

ALTER TABLE sipaf.cor_area_pf
    ADD CONSTRAINT pk_sipaf_cor_area_pf_id_pf_id_area PRIMARY KEY (id_pf, id_area);

---- sipaf.cor_area_pf foreign keys contraints

ALTER TABLE sipaf.cor_area_pf
    ADD CONSTRAINT fk_sipaf_cor_area_pf_id_pf FOREIGN KEY (id_pf)
    REFERENCES sipaf.t_passages_faune (id_pf)
    ON UPDATE CASCADE ON DELETE NO ACTION;

ALTER TABLE sipaf.cor_area_pf
    ADD CONSTRAINT fk_sipaf_cor_area_pf_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area)
    ON UPDATE CASCADE ON DELETE NO ACTION;
-- cor sipaf.cor_route_pf

CREATE TABLE IF NOT EXISTS sipaf.cor_route_pf (
    id_pf INTEGER NOT NULL,
    id_route INTEGER NOT NULL
);


---- sipaf.cor_route_pf primary keys contraints

ALTER TABLE sipaf.cor_route_pf
    ADD CONSTRAINT pk_sipaf_cor_route_pf_id_pf_id_route PRIMARY KEY (id_pf, id_route);

---- sipaf.cor_route_pf foreign keys contraints

ALTER TABLE sipaf.cor_route_pf
    ADD CONSTRAINT fk_sipaf_cor_route_pf_id_pf FOREIGN KEY (id_pf)
    REFERENCES sipaf.t_passages_faune (id_pf)
    ON UPDATE CASCADE ON DELETE NO ACTION;

ALTER TABLE sipaf.cor_route_pf
    ADD CONSTRAINT fk_sipaf_cor_route_pf_id_route FOREIGN KEY (id_route)
    REFERENCES sipaf.l_routes (id_route)
    ON UPDATE CASCADE ON DELETE NO ACTION;


-- Triggers


---- Trigger intersection sipaf.t_passages_faune.geom avec le ref_geo

CREATE OR REPLACE FUNCTION sipaf.fct_trig_insert_cor_area_pf_on_each_statement()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                WITH geom_test AS (
                    SELECT ST_TRANSFORM(t.geom, 2154) as geom,
                    t.id_pf
                    FROM NEW as t
                )
                INSERT INTO sipaf.cor_area_pf (
                    id_area,
                    id_pf
                )
                SELECT
                    a.id_area,
                    t.id_pf
                    FROM geom_test t
                    JOIN ref_geo.l_areas a
                        ON public.ST_INTERSECTS(t.geom, a.geom)
                        WHERE
                            a.enable IS TRUE
                            AND (
                                ST_GeometryType(t.geom) = 'ST_Point'
                                OR
                                NOT public.ST_TOUCHES(t.geom,a.geom)
                            );
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE OR REPLACE FUNCTION sipaf.fct_trig_update_cor_area_pf_on_row()
    RETURNS trigger AS
        $BODY$
            BEGIN
                DELETE FROM sipaf.cor_area_pf WHERE id_pf = NEW.id_pf;
                INSERT INTO sipaf.cor_area_pf (
                    id_area,
                    id_pf
                )
                SELECT
                    a.id_area,
                    t.id_pf
                FROM ref_geo.l_areas a
                JOIN sipaf.t_passages_faune t
                    ON public.ST_INTERSECTS(ST_TRANSFORM(t.geom, 2154), a.geom)
                WHERE
                    a.enable IS TRUE
                    AND t.id_pf = NEW.id_pf
                    AND (
                        ST_GeometryType(t.geom) = 'ST_Point'
                        OR NOT public.ST_TOUCHES(ST_TRANSFORM(t.geom, 2154), a.geom)
                    )
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE TRIGGER trg_insert_sipaf_cor_area_pf
    AFTER INSERT ON sipaf.t_passages_faune
    REFERENCING NEW TABLE AS NEW
    FOR EACH STATEMENT
        EXECUTE PROCEDURE sipaf.fct_trig_insert_cor_area_pf_on_each_statement();

CREATE TRIGGER trg_update_sipaf_cor_area_pf
    AFTER UPDATE OF geom ON sipaf.t_passages_faune
    FOR EACH ROW
        EXECUTE PROCEDURE sipaf.fct_trig_update_cor_area_pf_on_row();

---- Trigger sipaf.t_passages_faune.geom avec une distance de 0.001 avec sipaf.l_routes.id_route

CREATE OR REPLACE FUNCTION sipaf.fct_trig_insert_cor_route_pf_on_each_statement()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                INSERT INTO sipaf.cor_route_pf (
                    id_route,
                    id_pf
                )
                SELECT
                    a.id_route,
                    t.id_pf
                    FROM sipaf.t_passages_faune t
                    JOIN sipaf.l_routes a
                        ON ST_DWITHIN(t.geom, a.geom, 0.001)
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE OR REPLACE FUNCTION sipaf.fct_trig_update_cor_route_pf_on_row()
    RETURNS trigger AS
        $BODY$
            BEGIN
                DELETE FROM sipaf.cor_route_pf WHERE id_pf = NEW.id_pf;
                INSERT INTO sipaf.cor_route_pf (
                    a.id_route,
                    t.id_pf
                )
                SELECT
                    a.id_route,
                    t.id_pf
                FROM sipaf.l_routes a
                JOIN sipaf.t_passages_faune t
                    ON ST_DWITHIN(t.geom, a.geom, 0.001)
                WHERE
                    t.id_pf = NEW.id_pf
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE TRIGGER trg_insert_sipaf_cor_route_pf
    AFTER INSERT ON sipaf.t_passages_faune
    REFERENCING NEW TABLE AS NEW
    FOR EACH STATEMENT
        EXECUTE PROCEDURE sipaf.fct_trig_insert_cor_route_pf_on_each_statement();

CREATE TRIGGER trg_update_sipaf_cor_route_pf
    AFTER UPDATE OF geom ON sipaf.t_passages_faune
    FOR EACH ROW
        EXECUTE PROCEDURE sipaf.fct_trig_update_cor_route_pf_on_row();



-- Indexes


CREATE INDEX sipaf_t_passages_faune_geom_idx
    ON sipaf.t_passages_faune
    USING GIST (geom);


-- Indexes


CREATE INDEX sipaf_l_routes_geom_idx
    ON sipaf.l_routes
    USING GIST (geom);



