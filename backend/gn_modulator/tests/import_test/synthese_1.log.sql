-- Log Import {id import}
-- - schema_code: syn.synthese

-- Tables et vues utlisées pour l'import
-- - data: gn_modulator_import.t_1887_data
--    table contenant les données du fichier à importer
--
-- - raw: gn_modulator_import.v_1887_raw_syn_synthese
--    choix des colonnes, typage
--
-- - process: gn_modulator_import.v_1887_process_syn_synthese
--    résolution des clés
--



-- Creation de la table des données

CREATE TABLE IF NOT EXISTS gn_modulator_import.t_1887_data (
    id_import SERIAL NOT NULL,
    cd_nom VARCHAR,
    id_source VARCHAR,
    entity_source_pk_value VARCHAR,
    nom_cite VARCHAR,
    date_min VARCHAR,
    date_max VARCHAR,
    cor_observers VARCHAR,
    CONSTRAINT pk_gn_modulator_import_t_1887_data_id_import PRIMARY KEY (id_import)
);

-- Insertion des données

INSERT INTO gn_modulator_import.t_1887_data (cd_nom, id_source, entity_source_pk_value, nom_cite, date_min, date_max, cor_observers)
    VALUES
         ('67111','Occtax','21','Ablette','2017-01-08 20:00:00.000','2017-01-08 23:00:00.000','admin'),
        ('67111','Occtax','22','Ablette','2017-01-08 20:00:00.000','2017-01-08 23:00:00.000','admin')
;

-- Typage (raw)

DROP VIEW IF EXISTS gn_modulator_import.v_1887_raw_syn_synthese CASCADE;
CREATE VIEW gn_modulator_import.v_1887_raw_syn_synthese AS
SELECT
    t.id_import,
    t.cd_nom,
    t.id_source,
    entity_source_pk_value,
    nom_cite,
    date_min::TIMESTAMP,
    date_max::TIMESTAMP,
    t.cor_observers,
    CONCAT(t.id_source, '|', t.entity_source_pk_value) AS id_synthese
FROM gn_modulator_import.t_1887_data t;


-- Résolution des clés (process)

DROP VIEW IF EXISTS gn_modulator_import.v_1887_process_syn_synthese CASCADE;
CREATE VIEW gn_modulator_import.v_1887_process_syn_synthese AS
SELECT
    id_import,
    j_0.cd_nom AS cd_nom,
    j_1.id_source AS id_source,
    t.entity_source_pk_value,
    t.nom_cite,
    t.date_min,
    t.date_max,
    j_pk.id_synthese
FROM gn_modulator_import.v_1887_raw_syn_synthese t
LEFT JOIN taxonomie.taxref j_0
    ON j_0.cd_nom::TEXT = SPLIT_PART(t.cd_nom, '|', 1)::TEXT
LEFT JOIN gn_synthese.t_sources j_1
    ON j_1.name_source::TEXT = SPLIT_PART(t.id_source, '|', 1)::TEXT
LEFT JOIN gn_synthese.synthese j_pk
    ON j_pk.id_source::TEXT = j_1.id_source::TEXT
    AND (j_pk.entity_source_pk_value::TEXT = SPLIT_PART(t.id_synthese, '|', 2)::TEXT
      OR (j_pk.entity_source_pk_value IS NULL AND SPLIT_PART(t.id_synthese, '|', 2) IS NULL));


-- Insertion des données


INSERT INTO gn_synthese.synthese (
    cd_nom,
    id_source,
    entity_source_pk_value,
    nom_cite,
    date_min,
    date_max
)
SELECT
    cd_nom,
    id_source,
    entity_source_pk_value,
    nom_cite,
    date_min,
    date_max
FROM gn_modulator_import.v_1887_process_syn_synthese WHERE id_synthese IS NULL;


-- Mise à jour des données


UPDATE gn_synthese.synthese t SET
    cd_nom=p.cd_nom,
    id_source=p.id_source,
    entity_source_pk_value=p.entity_source_pk_value,
    nom_cite=p.nom_cite,
    date_min=p.date_min,
    date_max=p.date_max
FROM (
    SELECT
        cd_nom,
        id_source,
        entity_source_pk_value,
        nom_cite,
        date_min,
        date_max,
        id_synthese
    FROM gn_modulator_import.v_1887_process_syn_synthese
)p
WHERE p.id_synthese = t.id_synthese
  AND NOT (
    (t.cd_nom::TEXT IS DISTINCT FROM p.cd_nom::TEXT)
    AND (t.id_source::TEXT IS DISTINCT FROM p.id_source::TEXT)
    AND (t.entity_source_pk_value::TEXT IS DISTINCT FROM p.entity_source_pk_value::TEXT)
    AND (t.nom_cite::TEXT IS DISTINCT FROM p.nom_cite::TEXT)
    AND (t.date_min::TEXT IS DISTINCT FROM p.date_min::TEXT)
    AND (t.date_max::TEXT IS DISTINCT FROM p.date_max::TEXT)
    AND (t.id_synthese::TEXT IS DISTINCT FROM p.id_synthese::TEXT)
)
;
-- - Traitement relation n-n cor_observers