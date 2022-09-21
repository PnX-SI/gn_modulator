-- process schema : m_monitoring.site
--
-- and dependancies : m_monitoring.site_category, m_monitoring.visit, m_monitoring.observation, m_monitoring.site_group, m_monitoring.sc_arbre_loge, m_monitoring.sc_grotte


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.t_sites

CREATE TABLE m_monitoring.t_sites (
    id_site SERIAL NOT NULL,
    site_code VARCHAR NOT NULL,
    site_name VARCHAR NOT NULL,
    site_desc VARCHAR,
    site_uuid UUID,
    site_geom GEOMETRY(GEOMETRY, 4326) NOT NULL,
    id_site_category INTEGER,
    id_digitiser INTEGER,
    id_inventor INTEGER,
    id_nomenclature_type_site INTEGER NOT NULL,
    site_data JSONB
);

COMMENT ON COLUMN m_monitoring.t_sites.id_site_category IS 'Catégorie de site (pour pouvoir associé des champs spécifiques)';
COMMENT ON COLUMN m_monitoring.t_sites.id_digitiser IS 'Personne qui a saisi la donnée';
COMMENT ON COLUMN m_monitoring.t_sites.id_inventor IS 'Descripteur du site';
COMMENT ON COLUMN m_monitoring.t_sites.id_nomenclature_type_site IS 'Nomenclature de type de site';
COMMENT ON COLUMN m_monitoring.t_sites.site_data IS 'Données additionnelles du site';

---- table m_monitoring.bib_sites_category

CREATE TABLE m_monitoring.bib_sites_category (
    id_category SERIAL NOT NULL,
    category_name VARCHAR NOT NULL,
    category_code VARCHAR NOT NULL,
    category_desc VARCHAR NOT NULL
);


---- table m_monitoring.t_visits

CREATE TABLE m_monitoring.t_visits (
    id_visit SERIAL NOT NULL,
    visit_uuid UUID,
    visit_date_min DATE NOT NULL,
    visit_date_max DATE,
    id_site INTEGER,
    id_module INTEGER,
    id_digitiser INTEGER,
    id_dataset INTEGER NOT NULL,
    visit_data JSONB
);

COMMENT ON COLUMN m_monitoring.t_visits.id_visit IS 'Clé primaire de la visite';
COMMENT ON COLUMN m_monitoring.t_visits.visit_date_min IS 'Date (minimale) associée à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.visit_date_max IS 'Date (maximale) associée à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.id_site IS 'Site associé à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.id_module IS 'Module associé à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.id_digitiser IS 'Personne qui a saisi la donnée';
COMMENT ON COLUMN m_monitoring.t_visits.id_dataset IS 'Jeu de données associé à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.visit_data IS 'Données additionnelles du site';

---- table m_monitoring.t_observations

CREATE TABLE m_monitoring.t_observations (
    id_observation SERIAL NOT NULL,
    cd_nom INTEGER,
    id_digitiser INTEGER,
    id_visit INTEGER,
    observation_uuid UUID,
    observation_data JSONB
);

COMMENT ON COLUMN m_monitoring.t_observations.id_observation IS 'Clé primaire de l''observaiton';
COMMENT ON COLUMN m_monitoring.t_observations.cd_nom IS 'Taxon lié à l''observation';
COMMENT ON COLUMN m_monitoring.t_observations.id_digitiser IS 'Personne qui a saisi la donnée';
COMMENT ON COLUMN m_monitoring.t_observations.id_visit IS 'Visite associée à l''observation';
COMMENT ON COLUMN m_monitoring.t_observations.observation_data IS 'Données additionnelles de l''observation';

---- table m_monitoring.t_site_group

CREATE TABLE m_monitoring.t_site_group (
    id_site_group SERIAL NOT NULL,
    site_group_code VARCHAR NOT NULL,
    site_group_name VARCHAR NOT NULL,
    site_group_desc VARCHAR,
    id_digitiser INTEGER,
    site_group_uuid UUID,
    site_group_geom GEOMETRY(GEOMETRY, 4326),
    site_group_data JSONB
);

COMMENT ON COLUMN m_monitoring.t_site_group.id_site_group IS 'Clé primaire du group de site';
COMMENT ON COLUMN m_monitoring.t_site_group.id_digitiser IS 'Personne qui a saisi la donnée';
COMMENT ON COLUMN m_monitoring.t_site_group.site_group_data IS 'Données additionnelles du  groupe de site';

---- table m_monitoring.sc_arbre_loge

CREATE TABLE m_monitoring.sc_arbre_loge (
    id_site SERIAL NOT NULL,
    hauteur FLOAT
);


---- table m_monitoring.sc_grotte

CREATE TABLE m_monitoring.sc_grotte (
    id_site SERIAL NOT NULL,
    profondeur FLOAT
);


---- m_monitoring.t_sites primary key constraint

ALTER TABLE m_monitoring.t_sites
    ADD CONSTRAINT pk_m_monitoring_t_sites_id_site PRIMARY KEY (id_site);


---- m_monitoring.bib_sites_category primary key constraint

ALTER TABLE m_monitoring.bib_sites_category
    ADD CONSTRAINT pk_m_monitoring_bib_sites_category_id_category PRIMARY KEY (id_category);


---- m_monitoring.t_visits primary key constraint

ALTER TABLE m_monitoring.t_visits
    ADD CONSTRAINT pk_m_monitoring_t_visits_id_visit PRIMARY KEY (id_visit);


---- m_monitoring.t_observations primary key constraint

ALTER TABLE m_monitoring.t_observations
    ADD CONSTRAINT pk_m_monitoring_t_observations_id_observation PRIMARY KEY (id_observation);


---- m_monitoring.t_site_group primary key constraint

ALTER TABLE m_monitoring.t_site_group
    ADD CONSTRAINT pk_m_monitoring_t_site_group_id_site_group PRIMARY KEY (id_site_group);


---- m_monitoring.sc_arbre_loge primary key constraint

ALTER TABLE m_monitoring.sc_arbre_loge
    ADD CONSTRAINT pk_m_monitoring_sc_arbre_loge_id_site PRIMARY KEY (id_site);


---- m_monitoring.sc_grotte primary key constraint

ALTER TABLE m_monitoring.sc_grotte
    ADD CONSTRAINT pk_m_monitoring_sc_grotte_id_site PRIMARY KEY (id_site);


---- m_monitoring.t_sites foreign key constraint id_site_category

ALTER TABLE m_monitoring.t_sites
    ADD CONSTRAINT fk_m_monitoring_t_sit_bib_s_id_site_category FOREIGN KEY (id_site_category)
    REFERENCES m_monitoring.bib_sites_category(id_category)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_sites foreign key constraint id_digitiser

ALTER TABLE m_monitoring.t_sites
    ADD CONSTRAINT fk_m_monitoring_t_sit_t_rol_id_digitiser FOREIGN KEY (id_digitiser)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_sites foreign key constraint id_inventor

ALTER TABLE m_monitoring.t_sites
    ADD CONSTRAINT fk_m_monitoring_t_sit_t_rol_id_inventor FOREIGN KEY (id_inventor)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_sites foreign key constraint id_nomenclature_type_site

ALTER TABLE m_monitoring.t_sites
    ADD CONSTRAINT fk_m_monitoring_t_sit_t_nom_id_nomenclature_type_site FOREIGN KEY (id_nomenclature_type_site)
    REFERENCES ref_nomenclatures.t_nomenclatures(id_nomenclature)
    ON UPDATE CASCADE ON DELETE CASCADE;


---- m_monitoring.t_visits foreign key constraint id_site

ALTER TABLE m_monitoring.t_visits
    ADD CONSTRAINT fk_m_monitoring_t_vis_t_sit_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites(id_site)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_visits foreign key constraint id_digitiser

ALTER TABLE m_monitoring.t_visits
    ADD CONSTRAINT fk_m_monitoring_t_vis_t_rol_id_digitiser FOREIGN KEY (id_digitiser)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_visits foreign key constraint id_dataset

ALTER TABLE m_monitoring.t_visits
    ADD CONSTRAINT fk_m_monitoring_t_vis_t_dat_id_dataset FOREIGN KEY (id_dataset)
    REFERENCES gn_meta.t_datasets(id_dataset)
    ON UPDATE CASCADE ON DELETE CASCADE;


---- m_monitoring.t_observations foreign key constraint cd_nom

ALTER TABLE m_monitoring.t_observations
    ADD CONSTRAINT fk_m_monitoring_t_obs_taxre_cd_nom FOREIGN KEY (cd_nom)
    REFERENCES taxonomie.taxref(cd_nom)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_observations foreign key constraint id_digitiser

ALTER TABLE m_monitoring.t_observations
    ADD CONSTRAINT fk_m_monitoring_t_obs_t_rol_id_digitiser FOREIGN KEY (id_digitiser)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

---- m_monitoring.t_observations foreign key constraint id_visit

ALTER TABLE m_monitoring.t_observations
    ADD CONSTRAINT fk_m_monitoring_t_obs_t_vis_id_visit FOREIGN KEY (id_visit)
    REFERENCES m_monitoring.t_visits(id_visit)
    ON UPDATE CASCADE ON DELETE SET NULL;


---- m_monitoring.t_site_group foreign key constraint id_digitiser

ALTER TABLE m_monitoring.t_site_group
    ADD CONSTRAINT fk_m_monitoring_t_sit_t_rol_id_digitiser FOREIGN KEY (id_digitiser)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;


---- m_monitoring.sc_arbre_loge foreign key constraint id_site

ALTER TABLE m_monitoring.sc_arbre_loge
    ADD CONSTRAINT fk_m_monitoring_sc_ar_t_sit_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites(id_site)
    ON UPDATE CASCADE ON DELETE CASCADE;


---- m_monitoring.sc_grotte foreign key constraint id_site

ALTER TABLE m_monitoring.sc_grotte
    ADD CONSTRAINT fk_m_monitoring_sc_gr_t_sit_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites(id_site)
    ON UPDATE CASCADE ON DELETE CASCADE;


---- nomenclature check type constraints

ALTER TABLE m_monitoring.t_sites
        ADD CONSTRAINT check_nom_type_m_monitoring_t_sites_id_ite_typite
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_type_site,'TYPE_SITE'))
        NOT VALID;


-- cor m_monitoring.cor_site_group

CREATE TABLE IF NOT EXISTS m_monitoring.cor_site_group (
    id_site INTEGER NOT NULL NOT NULL,
    id_site_group INTEGER NOT NULL NOT NULL
);


---- m_monitoring.cor_site_group primary keys contraints

ALTER TABLE m_monitoring.cor_site_group
    ADD CONSTRAINT pk_m_monitoring_cor_site_group_id_site_id_site_group PRIMARY KEY (id_site, id_site_group);

---- m_monitoring.cor_site_group foreign keys contraints

ALTER TABLE m_monitoring.cor_site_group
    ADD CONSTRAINT fk_m_monitoring_cor_site_group_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites (id_site)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE m_monitoring.cor_site_group
    ADD CONSTRAINT fk_m_monitoring_cor_site_group_id_site_group FOREIGN KEY (id_site_group)
    REFERENCES m_monitoring.t_site_group (id_site_group)
    ON UPDATE CASCADE ON DELETE CASCADE;
-- cor m_monitoring.cor_site_module

CREATE TABLE IF NOT EXISTS m_monitoring.cor_site_module (
    id_site INTEGER NOT NULL NOT NULL,
    id_module INTEGER NOT NULL NOT NULL
);


---- m_monitoring.cor_site_module primary keys contraints

ALTER TABLE m_monitoring.cor_site_module
    ADD CONSTRAINT pk_m_monitoring_cor_site_module_id_site_id_module PRIMARY KEY (id_site, id_module);

---- m_monitoring.cor_site_module foreign keys contraints

ALTER TABLE m_monitoring.cor_site_module
    ADD CONSTRAINT fk_m_monitoring_cor_site_module_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites (id_site)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE m_monitoring.cor_site_module
    ADD CONSTRAINT fk_m_monitoring_cor_site_module_id_module FOREIGN KEY (id_module)
    REFERENCES gn_modules.t_module_complements (id_module)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- cor m_monitoring.cor_visit_observer

CREATE TABLE IF NOT EXISTS m_monitoring.cor_visit_observer (
    id_visit INTEGER NOT NULL NOT NULL,
    id_role INTEGER NOT NULL NOT NULL
);


---- m_monitoring.cor_visit_observer primary keys contraints

ALTER TABLE m_monitoring.cor_visit_observer
    ADD CONSTRAINT pk_m_monitoring_cor_visit_observer_id_visit_id_role PRIMARY KEY (id_visit, id_role);

---- m_monitoring.cor_visit_observer foreign keys contraints

ALTER TABLE m_monitoring.cor_visit_observer
    ADD CONSTRAINT fk_m_monitoring_cor_visit_observer_id_visit FOREIGN KEY (id_visit)
    REFERENCES m_monitoring.t_visits (id_visit)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE m_monitoring.cor_visit_observer
    ADD CONSTRAINT fk_m_monitoring_cor_visit_observer_id_role FOREIGN KEY (id_role)
    REFERENCES utilisateurs.t_roles (id_role)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- process schema : m_monitoring.observation


-- process schema : m_monitoring.site_group


-- process schema : m_monitoring.site_category


-- process schema : m_monitoring.visit


-- process schema : m_monitoring.sc_arbre_loge


-- process schema : m_monitoring.sc_grotte


