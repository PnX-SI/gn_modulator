-- process schema : m_sipaf.pf
--
-- and dependencies : m_sipaf.actor


---- sql schema pr_sipaf

CREATE SCHEMA IF NOT EXISTS pr_sipaf;

---- table pr_sipaf.t_passages_faune

CREATE TABLE pr_sipaf.t_passages_faune (
    id_passage_faune SERIAL NOT NULL,
    code_passage_faune VARCHAR NOT NULL,
    uuid_passage_faune UUID NOT NULL DEFAULT public.uuid_generate_v4(),
    id_digitiser INTEGER,
    pi_ou_ps BOOLEAN,
    geom GEOMETRY(GEOMETRY, 4326) NOT NULL,
    geom_local GEOMETRY(GEOMETRY, 2154),
    pk FLOAT,
    pr INTEGER,
    pr_abs INTEGER,
    code_ouvrage_gestionnaire VARCHAR,
    nom_usuel_passage_faune VARCHAR,
    issu_requalification BOOLEAN,
    date_creation_ouvrage DATE,
    date_requalification_ouvrage DATE,
    largeur_ouvrage FLOAT,
    hauteur_ouvrage FLOAT,
    longueur_franchissement FLOAT,
    diametre FLOAT,
    largeur_dispo_faune FLOAT,
    hauteur_dispo_faune FLOAT,
    id_nomenclature_ouvrage_specificite INTEGER,
    ouvrage_type_autre VARCHAR,
    ouvrage_hydrau BOOLEAN,
    id_nomenclature_ouvrage_hydrau_position INTEGER,
    id_nomenclature_ouvrage_hydrau_banq_caract INTEGER,
    id_nomenclature_ouvrage_hydrau_banq_type INTEGER,
    ouvrag_hydrau_tirant_air FLOAT,
    source VARCHAR
);

COMMENT ON COLUMN pr_sipaf.t_passages_faune.code_passage_faune IS 'Code permettant d''identifier le passage à faune de manière unique (texte)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.uuid_passage_faune IS 'Identifiant universel unique au format UUID (uuid_pf)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.id_digitiser IS 'Personne qui a saisi la donnée';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.pi_ou_ps IS 'Positionnement du passage vis-à vis de l’infrastructure (inférieur (False) ou supérieur (True))';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.geom IS 'Géometrie du passage à faune (SRID=4326)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.geom_local IS 'Géométrie locale du passage à faune (SRID=2154)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.pk IS 'Point kilométrique';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.pr IS 'Point repère';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.pr_abs IS 'Distance en abscisse curviligne depuis le dernier PR';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.code_ouvrage_gestionnaire IS 'Code de l’ouvrage (pour le gestionnaire)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.nom_usuel_passage_faune IS 'Nom usuel utilisé pour dénommer l''ouvrage (nom_usuel_pf)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.issu_requalification IS 'L''ouvrage est issu d''une opération de requalification ?';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.date_creation_ouvrage IS 'Date de la réalisation de l''ouvrage';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.date_requalification_ouvrage IS 'Date de la requalification de l''ouvrage';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.largeur_ouvrage IS 'Largeur de l''ouvrage en mètre';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.hauteur_ouvrage IS 'Hauteur de l''ouvrage en mètre';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.longueur_franchissement IS 'Longueur de franchissement de l''ouvrage en mètres (ne prend pas en compte l''épaisseur des matériaux et éventuels obstacles)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.diametre IS 'Diamètre de la buse en mètre';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.largeur_dispo_faune IS 'Largeur de l''ouvrage effectivement disponible pour la faune en mètre';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.hauteur_dispo_faune IS 'Hauteur de l''ouvrage effectivement disponible pour la faune en mètre';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_specificite IS 'Exclusivité pour le passage faune (specificite)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.ouvrage_hydrau IS 'Ouvrage hydraulique ou non';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_hydrau_position IS 'Ouvrage hydraulique Position (ouvrage_hydrau_position)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_hydrau_banq_caract IS 'Caractérisation de la banquette dans le cas d''un ouvrage hydraulique (ouvrage_hydrau_caract_banquette)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_hydrau_banq_type IS 'Type de la banquette dans le cas d''un ouvrage hydraulique (ouvrage_hydrau_type_banquette)';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.ouvrag_hydrau_tirant_air IS ' Tirant d''air existant entre la banquette et le plafond de l''ouvrage, en mètre';
COMMENT ON COLUMN pr_sipaf.t_passages_faune.source IS 'Source de la donnée';

---- table pr_sipaf.cor_actor_pf

CREATE TABLE pr_sipaf.cor_actor_pf (
    id_actor SERIAL NOT NULL,
    id_passage_faune INTEGER NOT NULL,
    id_organism INTEGER,
    id_role INTEGER,
    id_nomenclature_type_actor INTEGER NOT NULL
);



ALTER TABLE pr_sipaf.t_passages_faune ADD CONSTRAINT unique_pr_sipaf_t_passages_faune_code_passage_faune UNIQUE(code_passage_faune);
---- pr_sipaf.t_passages_faune primary key constraint

ALTER TABLE pr_sipaf.t_passages_faune
    ADD CONSTRAINT pk_pr_sipaf_t_passages_faune_id_passage_faune PRIMARY KEY (id_passage_faune);


---- pr_sipaf.cor_actor_pf primary key constraint

ALTER TABLE pr_sipaf.cor_actor_pf
    ADD CONSTRAINT pk_pr_sipaf_cor_actor_pf_id_actor PRIMARY KEY (id_actor);


---- pr_sipaf.t_passages_faune foreign key constraint id_digitiser

ALTER TABLE pr_sipaf.t_passages_faune
    ADD CONSTRAINT fk_pr_sipaf_t_pas_t_rol_id_digitiser FOREIGN KEY (id_digitiser)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- pr_sipaf.t_passages_faune foreign key constraint id_nomenclature_ouvrage_specificite

ALTER TABLE pr_sipaf.t_passages_faune
    ADD CONSTRAINT fk_pr_sipaf_t_pas_t_nom_id_nomenclature_ouvrage_specificite FOREIGN KEY (id_nomenclature_ouvrage_specificite)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- pr_sipaf.t_passages_faune foreign key constraint id_nomenclature_ouvrage_hydrau_position

ALTER TABLE pr_sipaf.t_passages_faune
    ADD CONSTRAINT fk_pr_sipaf_t_pas_t_nom_id_nomenclature_ouvrage_hydrau_position FOREIGN KEY (id_nomenclature_ouvrage_hydrau_position)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- pr_sipaf.t_passages_faune foreign key constraint id_nomenclature_ouvrage_hydrau_banq_caract

ALTER TABLE pr_sipaf.t_passages_faune
    ADD CONSTRAINT fk_pr_sipaf_t_pas_t_nom_id_nomenclature_ouvrage_hydrau_banq_caract FOREIGN KEY (id_nomenclature_ouvrage_hydrau_banq_caract)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- pr_sipaf.t_passages_faune foreign key constraint id_nomenclature_ouvrage_hydrau_banq_type

ALTER TABLE pr_sipaf.t_passages_faune
    ADD CONSTRAINT fk_pr_sipaf_t_pas_t_nom_id_nomenclature_ouvrage_hydrau_banq_type FOREIGN KEY (id_nomenclature_ouvrage_hydrau_banq_type)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE SET NULL;


---- pr_sipaf.cor_actor_pf foreign key constraint id_passage_faune

ALTER TABLE pr_sipaf.cor_actor_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_a_t_pas_id_passage_faune FOREIGN KEY (id_passage_faune)
    REFERENCES pr_sipaf.t_passages_faune(id_passage_faune)
    ON UPDATE CASCADE ON DELETE CASCADE;

---- pr_sipaf.cor_actor_pf foreign key constraint id_organism

ALTER TABLE pr_sipaf.cor_actor_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_a_bib_o_id_organism FOREIGN KEY (id_organism)
    REFERENCES utilisateurs.bib_organismes(id_organisme)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- pr_sipaf.cor_actor_pf foreign key constraint id_role

ALTER TABLE pr_sipaf.cor_actor_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_a_t_rol_id_role FOREIGN KEY (id_role)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- pr_sipaf.cor_actor_pf foreign key constraint id_nomenclature_type_actor

ALTER TABLE pr_sipaf.cor_actor_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_a_t_nom_id_nomenclature_type_actor FOREIGN KEY (id_nomenclature_type_actor)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE CASCADE;


---- nomenclature check type constraints

ALTER TABLE pr_sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_pr_sipaf_t_passages_faune_id_ite_pf_ite
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_ouvrage_specificite,'PF_OUVRAGE_SPECIFICITE'))
        NOT VALID;


ALTER TABLE pr_sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_pr_sipaf_t_passages_faune_id_ion_pf_ion
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_ouvrage_hydrau_position,'PF_OUVRAGE_HYDRAULIQUE_POSITION'))
        NOT VALID;


ALTER TABLE pr_sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_pr_sipaf_t_passages_faune_id_act_pf_act
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_ouvrage_hydrau_banq_caract,'PF_OUVRAGE_HYDRAULIQUE_BANQ_CARACT'))
        NOT VALID;


ALTER TABLE pr_sipaf.t_passages_faune
        ADD CONSTRAINT check_nom_type_pr_sipaf_t_passages_faune_id_ype_pf_ype
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_ouvrage_hydrau_banq_type,'PF_OUVRAGE_HYDRAULIQUE_BANQ_TYPE'))
        NOT VALID;



---- nomenclature check type constraints

ALTER TABLE pr_sipaf.cor_actor_pf
        ADD CONSTRAINT check_nom_type_pr_sipaf_cor_actor_pf_id_tor_pf_tor
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_type_actor,'PF_TYPE_ACTOR'))
        NOT VALID;



-- cor pr_sipaf.cor_pf_nomenclature_ouvrage_type

CREATE TABLE IF NOT EXISTS pr_sipaf.cor_pf_nomenclature_ouvrage_type (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);


---- pr_sipaf.cor_pf_nomenclature_ouvrage_type primary keys contraints

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_type
    ADD CONSTRAINT pk_pr_sipaf_cor_pf_nomenclature_ouvrage_type_id_passage_faune_id_nomenclature PRIMARY KEY (id_passage_faune, id_nomenclature);

---- pr_sipaf.cor_pf_nomenclature_ouvrage_type foreign keys contraints

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_type
    ADD CONSTRAINT fk_pr_sipaf_cor_pf_nomenclature_ouvrage_type_id_passage_faune FOREIGN KEY (id_passage_faune)
    REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_type
    ADD CONSTRAINT fk_pr_sipaf_cor_pf_nomenclature_ouvrage_type_id_nomenclature FOREIGN KEY (id_nomenclature)
    REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_type
        ADD CONSTRAINT check_nom_type_pr_sipaf_cor_pf_nomenclature_ouvrage_type_id_ure_pf_ype
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature,'PF_OUVRAGE_TYPE'))
        NOT VALID;

-- cor pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux

CREATE TABLE IF NOT EXISTS pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    id_nomenclature INTEGER NOT NULL NOT NULL
);


---- pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux primary keys contraints

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux
    ADD CONSTRAINT pk_pr_sipaf_cor_pf_nomenclature_ouvrage_materiaux_id_passage_faune_id_nomenclature PRIMARY KEY (id_passage_faune, id_nomenclature);

---- pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux foreign keys contraints

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux
    ADD CONSTRAINT fk_pr_sipaf_cor_pf_nomenclature_ouvrage_materiaux_id_passage_faune FOREIGN KEY (id_passage_faune)
    REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux
    ADD CONSTRAINT fk_pr_sipaf_cor_pf_nomenclature_ouvrage_materiaux_id_nomenclature FOREIGN KEY (id_nomenclature)
    REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux
        ADD CONSTRAINT check_nom_type_pr_sipaf_cor_pf_nomenclature_ouvrage_materiaux_id_ure_pf_aux
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature,'PF_OUVRAGE_MATERIAUX'))
        NOT VALID;

-- cor pr_sipaf.cor_area_pf

CREATE TABLE IF NOT EXISTS pr_sipaf.cor_area_pf (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    id_area INTEGER NOT NULL NOT NULL
);


---- pr_sipaf.cor_area_pf primary keys contraints

ALTER TABLE pr_sipaf.cor_area_pf
    ADD CONSTRAINT pk_pr_sipaf_cor_area_pf_id_passage_faune_id_area PRIMARY KEY (id_passage_faune, id_area);

---- pr_sipaf.cor_area_pf foreign keys contraints

ALTER TABLE pr_sipaf.cor_area_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_area_pf_id_passage_faune FOREIGN KEY (id_passage_faune)
    REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pr_sipaf.cor_area_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_area_pf_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area)
    ON UPDATE CASCADE ON DELETE CASCADE;
-- cor pr_sipaf.cor_linear_pf

CREATE TABLE IF NOT EXISTS pr_sipaf.cor_linear_pf (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    id_linear INTEGER NOT NULL NOT NULL
);


---- pr_sipaf.cor_linear_pf primary keys contraints

ALTER TABLE pr_sipaf.cor_linear_pf
    ADD CONSTRAINT pk_pr_sipaf_cor_linear_pf_id_passage_faune_id_linear PRIMARY KEY (id_passage_faune, id_linear);

---- pr_sipaf.cor_linear_pf foreign keys contraints

ALTER TABLE pr_sipaf.cor_linear_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_linear_pf_id_passage_faune FOREIGN KEY (id_passage_faune)
    REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pr_sipaf.cor_linear_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_linear_pf_id_linear FOREIGN KEY (id_linear)
    REFERENCES ref_geo.l_linears (id_linear)
    ON UPDATE CASCADE ON DELETE CASCADE;


-- Triggers


CREATE OR REPLACE FUNCTION pr_sipaf.fn_tri_insert_t_passages_faune_copy_geom_to_geom_local()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                NEW.geom_local := ST_TRANSFORM(NEW.geom, 2154);
                RETURN NEW;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE TRIGGER pr_sipaf_tri_insert_t_passages_faune_copy_geom_to_geom_local
    BEFORE INSERT ON pr_sipaf.t_passages_faune
    FOR EACH ROW
        EXECUTE PROCEDURE pr_sipaf.fn_tri_insert_t_passages_faune_copy_geom_to_geom_local();

CREATE TRIGGER pr_sipaf_tri_update_t_passages_faune_copy_geom_to_geom_local
    BEFORE UPDATE OF geom ON pr_sipaf.t_passages_faune
    FOR EACH ROW
        EXECUTE PROCEDURE pr_sipaf.fn_tri_insert_t_passages_faune_copy_geom_to_geom_local();

---- Trigger intersection pr_sipaf.t_passages_faune.geom_local avec le ref_geo


CREATE OR REPLACE FUNCTION pr_sipaf.fct_trig_insert_cor_area_pf_on_each_statement()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                WITH geom_test AS (
                    SELECT ST_TRANSFORM(t.geom_local, 2154) as geom_local,
                    t.id_passage_faune
                    FROM NEW as t
                )
                INSERT INTO pr_sipaf.cor_area_pf (
                    id_area,
                    id_passage_faune
                )
                SELECT
                    a.id_area,
                    t.id_passage_faune
                    FROM geom_test t
                    JOIN ref_geo.l_areas a
                        ON public.ST_INTERSECTS(t.geom_local, a.geom)
                        WHERE
                            a.enable IS TRUE
                            AND (
                                ST_GeometryType(t.geom_local) = 'ST_Point'
                                OR
                                NOT public.ST_TOUCHES(t.geom_local,a.geom)
                            );
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE OR REPLACE FUNCTION pr_sipaf.fct_trig_update_cor_area_pf_on_row()
    RETURNS trigger AS
        $BODY$
            BEGIN
                DELETE FROM pr_sipaf.cor_area_pf WHERE id_passage_faune = NEW.id_passage_faune;
                INSERT INTO pr_sipaf.cor_area_pf (
                    id_area,
                    id_passage_faune
                )
                SELECT
                    a.id_area,
                    t.id_passage_faune
                FROM ref_geo.l_areas a
                JOIN pr_sipaf.t_passages_faune t
                    ON public.ST_INTERSECTS(ST_TRANSFORM(t.geom_local, 2154), a.geom)
                WHERE
                    a.enable IS TRUE
                    AND t.id_passage_faune = NEW.id_passage_faune
                    AND (
                        ST_GeometryType(t.geom_local) = 'ST_Point'
                        OR NOT public.ST_TOUCHES(ST_TRANSFORM(t.geom_local, 2154), a.geom)
                    )
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE OR REPLACE FUNCTION pr_sipaf.process_all_cor_area_pf()
    RETURNS INTEGER AS
        $BODY$
            BEGIN
                DELETE FROM pr_sipaf.cor_area_pf;
                INSERT INTO pr_sipaf.cor_area_pf (
                    id_area,
                    id_passage_faune
                )
                SELECT
                    a.id_area,
                    t.id_passage_faune
                FROM ref_geo.l_areas a
                JOIN pr_sipaf.t_passages_faune t
                    ON public.ST_INTERSECTS(ST_TRANSFORM(t.geom_local, 2154), a.geom)
                WHERE
                    a.enable IS TRUE
                    AND (
                        ST_GeometryType(t.geom_local) = 'ST_Point'
                        OR NOT public.ST_TOUCHES(ST_TRANSFORM(t.geom_local, 2154), a.geom)
                    )
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE TRIGGER trg_insert_pr_sipaf_cor_area_pf
    AFTER INSERT ON pr_sipaf.t_passages_faune
    REFERENCING NEW TABLE AS NEW
    FOR EACH STATEMENT
        EXECUTE PROCEDURE pr_sipaf.fct_trig_insert_cor_area_pf_on_each_statement();

CREATE TRIGGER trg_update_pr_sipaf_cor_area_pf
    AFTER UPDATE OF geom ON pr_sipaf.t_passages_faune
    FOR EACH ROW
        EXECUTE PROCEDURE pr_sipaf.fct_trig_update_cor_area_pf_on_row();

---- Trigger pr_sipaf.t_passages_faune.geom_local avec une distance de 100 avec ref_geo.l_linears.id_linear


CREATE OR REPLACE FUNCTION pr_sipaf.fct_trig_insert_cor_linear_pf_on_each_statement()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                INSERT INTO pr_sipaf.cor_linear_pf (
                    id_linear,
                    id_passage_faune
                )
                WITH t_match AS (
                    SELECT
                        l.id_linear,
                        t.id_passage_faune,
                        ROW_NUMBER() OVER (PARTITION BY t.id_passage_faune, id_type) As rank
                        FROM NEW AS t
                        JOIN ref_geo.l_linears l
                            ON ST_DWITHIN(t.geom_local, l.geom, 100)
                        WHERE l.enable = TRUE
                        ORDER BY t.geom_local <-> l.geom
                )
                SELECT
                    id_linear,
                    id_passage_faune
                    FROM t_match
                    WHERE rank = 1
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE OR REPLACE FUNCTION pr_sipaf.fct_trig_update_cor_linear_pf_on_row()
    RETURNS trigger AS
        $BODY$
            BEGIN
                DELETE FROM pr_sipaf.cor_linear_pf WHERE id_passage_faune = NEW.id_passage_faune;
                INSERT INTO pr_sipaf.cor_linear_pf (
                    id_linear,
                    id_passage_faune
                )
                WITH t_match AS (
                    SELECT
                        l.id_linear,
                        t.id_passage_faune,
                        ROW_NUMBER() OVER (PARTITION BY t.id_passage_faune, id_type) As rank
                        FROM pr_sipaf.t_passages_faune AS t
                        JOIN ref_geo.l_linears l
                            ON ST_DWITHIN(t.geom_local, l.geom, 100)
                        WHERE
                            t.id_passage_faune = NEW.id_passage_faune
                            AND l.enable = TRUE
                        ORDER BY t.geom_local <-> l.geom
                )
                SELECT
                    id_linear,
                    id_passage_faune
                    FROM t_match
                    WHERE rank = 1
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE OR REPLACE FUNCTION pr_sipaf.process_all_cor_linear_pf()
    RETURNS INTEGER AS
        $BODY$
            BEGIN
                DELETE FROM pr_sipaf.cor_linear_pf;
                INSERT INTO pr_sipaf.cor_linear_pf (
                    id_linear,
                    id_passage_faune
                )
                WITH t_match AS (
                    SELECT
                        l.id_linear,
                        t.id_passage_faune,
                        ROW_NUMBER() OVER (PARTITION BY t.id_passage_faune, id_type) As rank
                        FROM pr_sipaf.t_passages_faune AS t
                        JOIN ref_geo.l_linears l
                            ON ST_DWITHIN(t.geom_local, l.geom, 100)
                        WHERE l.enable = TRUE
                        ORDER BY t.geom_local <-> l.geom
                )
                SELECT
                    id_linear,
                    id_passage_faune
                    FROM t_match
                    WHERE rank = 1
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

CREATE TRIGGER trg_insert_pr_sipaf_cor_linear_pf
    AFTER INSERT ON pr_sipaf.t_passages_faune
    REFERENCING NEW TABLE AS NEW
    FOR EACH STATEMENT
        EXECUTE PROCEDURE pr_sipaf.fct_trig_insert_cor_linear_pf_on_each_statement();

CREATE TRIGGER trg_update_pr_sipaf_cor_linear_pf
    AFTER UPDATE OF geom ON pr_sipaf.t_passages_faune
    FOR EACH ROW
        EXECUTE PROCEDURE pr_sipaf.fct_trig_update_cor_linear_pf_on_row();



-- Indexes


CREATE INDEX pr_sipaf_t_passages_faune_geom_idx
    ON pr_sipaf.t_passages_faune
    USING GIST (geom);
CREATE INDEX pr_sipaf_t_passages_faune_geom_local_idx
    ON pr_sipaf.t_passages_faune
    USING GIST (geom_local);

