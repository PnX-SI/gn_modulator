-- process schema : m_monitoring.site


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.t_base_sites

CREATE TABLE m_monitoring.t_base_sites (
    id_site SERIAL NOT NULL,
    site_code VARCHAR NOT NULL,
    site_name VARCHAR NOT NULL,
    site_desc VARCHAR,
    site_geom GEOMETRY(GEOMETRY, 4326) NOT NULL
);


---- m_monitoring.t_base_sites primary key constraint

ALTER TABLE m_monitoring.t_base_sites
    ADD CONSTRAINT pk_m_monitoring_t_base_sites_id_site PRIMARY KEY (id_site);


-- process schema : m_monitoring.site_complement


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.bib_sites_complements

CREATE TABLE m_monitoring.bib_sites_complements (
    id_complement SERIAL NOT NULL,
    complement_name VARCHAR NOT NULL,
    complement_code VARCHAR NOT NULL,
    complement_desc VARCHAR NOT NULL,
    schema_name VARCHAR NOT NULL,
    relation_name VARCHAR NOT NULL
);


---- m_monitoring.bib_sites_complements primary key constraint

ALTER TABLE m_monitoring.bib_sites_complements
    ADD CONSTRAINT pk_m_monitoring_bib_sites_complements_id_complement PRIMARY KEY (id_complement);


-- process schema : m_monitoring.sc_arbre_loge


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.sc_arbre_loge

CREATE TABLE m_monitoring.sc_arbre_loge (
    id_site SERIAL NOT NULL,
    hauteur FLOAT
);


---- m_monitoring.sc_arbre_loge primary key constraint

ALTER TABLE m_monitoring.sc_arbre_loge
    ADD CONSTRAINT pk_m_monitoring_sc_arbre_loge_id_site PRIMARY KEY (id_site);


---- m_monitoring.sc_arbre_loge foreign key constraint id_site

ALTER TABLE m_monitoring.sc_arbre_loge
    ADD CONSTRAINT fk_m_monitoring_sc_ar_t_bas_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_base_sites(id_site)
    ON UPDATE CASCADE ON DELETE NO ACTION;


-- process schema : m_monitoring.sc_grotte


---- sql schema m_monitoring

CREATE SCHEMA IF NOT EXISTS m_monitoring;

---- table m_monitoring.sc_grotte

CREATE TABLE m_monitoring.sc_grotte (
    id_site SERIAL NOT NULL,
    profondeur FLOAT
);


---- m_monitoring.sc_grotte primary key constraint

ALTER TABLE m_monitoring.sc_grotte
    ADD CONSTRAINT pk_m_monitoring_sc_grotte_id_site PRIMARY KEY (id_site);


---- m_monitoring.sc_grotte foreign key constraint id_site

ALTER TABLE m_monitoring.sc_grotte
    ADD CONSTRAINT fk_m_monitoring_sc_gr_t_bas_id_site FOREIGN KEY (id_site)
    REFERENCES m_monitoring.t_base_sites(id_site)
    ON UPDATE CASCADE ON DELETE NO ACTION;


