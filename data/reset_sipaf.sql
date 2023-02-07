-- DROP schema

-- DROP SCHEMA IF EXISTS sipaf CASCADE;

-- DELETE data +

DELETE FROM ref_nomenclatures.t_nomenclatures WHERE SOURCE = 'SIPAF';
DELETE FROM ref_nomenclatures.bib_nomenclatures_types WHERE SOURCE = 'SIPAF';

DELETE FROM gn_meta.cor_dataset_actor cda USING utilisateurs.bib_organismes bo WHERE bo.id_organisme = cda.id_organism AND bo.adresse_organisme = 'SIPAF';
DELETE FROM gn_meta.t_datasets d USING gn_meta.t_acquisition_frameworks a WHERE d.id_acquisition_framework = a.id_acquisition_framework AND a.acquisition_framework_name = 'SIPAF';
DELETE FROM gn_meta.t_acquisition_frameworks a WHERE a.acquisition_framework_name = 'SIPAF';

DELETE FROM utilisateurs.t_roles WHERE remarques = 'SIPAF';
DELETE FROM utilisateurs.bib_organismes WHERE adresse_organisme = 'SIPAF' ;

-- DELETE FROM gn_modulator.t_module_complements mc USING gn_commons.t_modules m WHERE m.module_code = 'SIPAF' AND m.id_module = mc.id_module;
DELETE FROM gn_commons.t_modules m WHERE m.module_code = 'SIPAF';
