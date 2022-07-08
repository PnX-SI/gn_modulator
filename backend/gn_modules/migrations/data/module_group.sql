-- process schema : modules.group


---- table gn_modules.t_module_groups

CREATE TABLE gn_modules.t_module_groups (
    id_module_group SERIAL NOT NULL,
    module_group_code VARCHAR,
    module_group_name VARCHAR,
    module_group_desc VARCHAR
);


---- gn_modules.t_module_groups primary key constraint

ALTER TABLE gn_modules.t_module_groups
    ADD CONSTRAINT pk_gn_modules_t_module_groups_id_module_group PRIMARY KEY (id_module_group);


-- cor gn_modules.cor_module_groupe

CREATE TABLE IF NOT EXISTS gn_modules.cor_module_groupe (
    id_module_group INTEGER NOT NULL NOT NULL,
    id_module INTEGER NOT NULL NOT NULL
);


---- gn_modules.cor_module_groupe primary keys contraints

ALTER TABLE gn_modules.cor_module_groupe
    ADD CONSTRAINT pk_gn_modules_cor_module_groupe_id_module_group_id_module PRIMARY KEY (id_module_group, id_module);

---- gn_modules.cor_module_groupe foreign keys contraints

ALTER TABLE gn_modules.cor_module_groupe
    ADD CONSTRAINT fk_gn_modules_cor_module_groupe_id_module_group FOREIGN KEY (id_module_group)
    REFERENCES gn_modules.t_module_groups (id_module_group)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE gn_modules.cor_module_groupe
    ADD CONSTRAINT fk_gn_modules_cor_module_groupe_id_module FOREIGN KEY (id_module)
    REFERENCES gn_modules.t_module_complements (id_module)
    ON UPDATE CASCADE ON DELETE CASCADE;


