-- create schema for module gn_modules

CREATE SCHEMA gn_modules;

CREATE TABLE gn_modules.t_module_complements(
  id_module serial NOT NULL,
  module_name VARCHAR,
  CONSTRAINT pk_gn_modules_t_module_complements_id_module PRIMARY KEY (id_module),
  CONSTRAINT fk_gn_modules_t_module_complements_id_module FOREIGN KEY (id_module)
     REFERENCES gn_commons.t_modules(id_module) ON UPDATE CASCADE ON DELETE CASCADE
);

