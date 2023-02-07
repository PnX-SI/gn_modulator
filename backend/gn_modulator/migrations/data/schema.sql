-- process schema : modules.group


---- sql schema gn_modulator

CREATE SCHEMA IF NOT EXISTS gn_modulator;

---- table gn_modulator.t_module_groups

CREATE TABLE gn_modulator.t_module_groups (
    id_module_group SERIAL NOT NULL,
    code VARCHAR,
    name VARCHAR,
    description VARCHAR
);


---- gn_modulator.t_module_groups primary key constraint

ALTER TABLE gn_modulator.t_module_groups
    ADD CONSTRAINT pk_gn_modulator_t_module_groups_id_module_group PRIMARY KEY (id_module_group);


-- cor gn_modulator.cor_module_groupe

CREATE TABLE IF NOT EXISTS gn_modulator.cor_module_groupe (
    id_module_group INTEGER NOT NULL NOT NULL,
    id_module INTEGER NOT NULL NOT NULL
);


---- gn_modulator.cor_module_groupe primary keys contraints

ALTER TABLE gn_modulator.cor_module_groupe
    ADD CONSTRAINT pk_gn_modulator_cor_module_groupe_id_module_group_id_module PRIMARY KEY (id_module_group, id_module);

---- gn_modulator.cor_module_groupe foreign keys contraints

ALTER TABLE gn_modulator.cor_module_groupe
    ADD CONSTRAINT fk_gn_modulator_cor_module_groupe_id_module_group FOREIGN KEY (id_module_group)
    REFERENCES gn_modulator.t_module_groups (id_module_group)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE gn_modulator.cor_module_groupe
    ADD CONSTRAINT fk_gn_modulator_cor_module_groupe_id_module FOREIGN KEY (id_module)
    REFERENCES gn_commons.t_modules (id_module)
    ON UPDATE CASCADE ON DELETE CASCADE;


-- process schema : modules.tag


---- sql schema gn_modulator

CREATE SCHEMA IF NOT EXISTS gn_modulator;

---- table gn_modulator.t_module_tags

CREATE TABLE gn_modulator.t_module_tags (
    id_module_tag SERIAL NOT NULL,
    code VARCHAR,
    name VARCHAR,
    description VARCHAR
);


---- gn_modulator.t_module_tags primary key constraint

ALTER TABLE gn_modulator.t_module_tags
    ADD CONSTRAINT pk_gn_modulator_t_module_tags_id_module_tag PRIMARY KEY (id_module_tag);


-- cor gn_modulator.cor_module_tag

CREATE TABLE IF NOT EXISTS gn_modulator.cor_module_tag (
    id_module_tag INTEGER NOT NULL NOT NULL,
    id_module INTEGER NOT NULL NOT NULL
);


---- gn_modulator.cor_module_tag primary keys contraints

ALTER TABLE gn_modulator.cor_module_tag
    ADD CONSTRAINT pk_gn_modulator_cor_module_tag_id_module_tag_id_module PRIMARY KEY (id_module_tag, id_module);

---- gn_modulator.cor_module_tag foreign keys contraints

ALTER TABLE gn_modulator.cor_module_tag
    ADD CONSTRAINT fk_gn_modulator_cor_module_tag_id_module_tag FOREIGN KEY (id_module_tag)
    REFERENCES gn_modulator.t_module_tags (id_module_tag)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE gn_modulator.cor_module_tag
    ADD CONSTRAINT fk_gn_modulator_cor_module_tag_id_module FOREIGN KEY (id_module)
    REFERENCES gn_commons.t_modules (id_module)
    ON UPDATE CASCADE ON DELETE CASCADE;
