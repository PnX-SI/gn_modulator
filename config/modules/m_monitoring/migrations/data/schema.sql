-- process schema : m_monitoring.site
--
-- and dependancies : m_monitoring.site_category, m_monitoring.sc_arbre_loge, m_monitoring.sc_grotte


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.t_sites

CREATE TABLE m_monitoring.t_sites (
    id_site SERIAL NOT NULL,
    site_code VARCHAR NOT NULL,
    site_name VARCHAR NOT NULL,
    site_desc VARCHAR,
    site_geom GEOMETRY(GEOMETRY, 4326) NOT NULL,
    id_site_category INTEGER,
    site_data JSONB
);

COMMENT ON COLUMN m_monitoring.t_sites.id_site_category IS 'Catégorie de site (pour pouvoir associé des champs spécifiques)';
COMMENT ON COLUMN m_monitoring.t_sites.site_data IS 'Données additionnelles du site';

---- table m_monitoring.bib_sites_category

CREATE TABLE m_monitoring.bib_sites_category (
    id_category SERIAL NOT NULL,
    category_name VARCHAR NOT NULL,
    category_code VARCHAR NOT NULL,
    category_desc VARCHAR NOT NULL
);


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
    ON UPDATE CASCADE ON DELETE NO ACTION;


---- m_monitoring.sc_arbre_loge foreign key constraint id_site

ALTER TABLE m_monitoring.sc_arbre_loge
    ADD CONSTRAINT fk_m_monitoring_sc_ar_t_sit_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites(id_site)
    ON UPDATE CASCADE ON DELETE NO ACTION;


---- m_monitoring.sc_grotte foreign key constraint id_site

ALTER TABLE m_monitoring.sc_grotte
    ADD CONSTRAINT fk_m_monitoring_sc_gr_t_sit_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites(id_site)
    ON UPDATE CASCADE ON DELETE NO ACTION;


-- process schema : m_monitoring.visit


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.t_visits

CREATE TABLE m_monitoring.t_visits (
    id_visit SERIAL NOT NULL,
    id_site INTEGER,
    visit_date_min DATE NOT NULL,
    visit_data JSONB
);

COMMENT ON COLUMN m_monitoring.t_visits.id_visit IS 'Clé primaire de la visite';
COMMENT ON COLUMN m_monitoring.t_visits.id_site IS 'Site associé à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.visit_date_min IS 'Date (minimale) associée à la visite';
COMMENT ON COLUMN m_monitoring.t_visits.visit_data IS 'Données additionnelles du site';

---- m_monitoring.t_visits primary key constraint

ALTER TABLE m_monitoring.t_visits
    ADD CONSTRAINT pk_m_monitoring_t_visits_id_visit PRIMARY KEY (id_visit);


---- m_monitoring.t_visits foreign key constraint id_site

ALTER TABLE m_monitoring.t_visits
    ADD CONSTRAINT fk_m_monitoring_t_vis_t_sit_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_sites(id_site)
    ON UPDATE CASCADE ON DELETE NO ACTION;


