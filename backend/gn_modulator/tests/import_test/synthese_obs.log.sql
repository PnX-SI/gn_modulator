-- Log Import 6559
-- - schema_code: syn.synthese

-- Tables et vues utlisées pour l'import
-- - data: gn_modulator_import.t_xxx_data
--    table contenant les données du fichier à importer
--
-- - mapping: gn_modulator_import.t_xxx_data
--    vue permettant de faire la corresondance entre
--             le fichier source et la table destinataire
--
-- - raw: gn_modulator_import.v_xxx_raw_syn_synthese
--    choix des colonnes, typage
--
-- - process: gn_modulator_import.v_xxx_process_syn_synthese
--    résolution des clés
--
-- - process relation n-n cor_observers: gn_modulator_import.v_xxx_process_syn_synthese_cor_observers


-- Creation de la table des données

CREATE TABLE IF NOT EXISTS gn_modulator_import.t_xxx_data (
    id_import SERIAL NOT NULL,
    cd_nom VARCHAR,
    id_source VARCHAR,
    entity_source_pk_value VARCHAR,
    nom_cite VARCHAR,
    date_min VARCHAR,
    date_max VARCHAR,
    cor_observers VARCHAR,
    CONSTRAINT pk_gn_modulator_import.t_xxx_data_id_import PRIMARY KEY (id_import)
);


-- Insertion des données

INSERT INTO gn_modulator_import.t_xxx_data (cd_nom, id_source, entity_source_pk_value, nom_cite, date_min, date_max, cor_observers)
    VALUES
         ('67111','Occtax','21','Ablette','2017-01-08 20:00:00.000','2017-01-08 23:00:00.000','admin,agent'),
        ('67111','Occtax','22','Ablette','2017-01-08 20:00:00.000','2017-01-08 23:00:00.000','admin,agent')
;

-- Typage (raw)

DROP VIEW IF EXISTS gn_modulator_import.v_xxx_raw_syn_synthese CASCADE;
CREATE VIEW gn_modulator_import.v_xxx_raw_syn_synthese AS
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
FROM gn_modulator_import.t_xxx_data t;


-- Vue d'import

DROP VIEW IF EXISTS gn_modulator_import.v_xxx_process_syn_synthese CASCADE;
CREATE VIEW gn_modulator_import.v_xxx_process_syn_synthese AS
SELECT
    min(id_import) AS id_import,
    j_0.cd_nom AS cd_nom,
    j_1.id_source AS id_source,
    t.entity_source_pk_value,
    t.nom_cite,
    t.date_min,
    t.date_max,
    j_pk.id_synthese
FROM gn_modulator_import.v_xxx_raw_syn_synthese t
LEFT JOIN taxonomie.taxref j_0
    ON j_0.cd_nom = t.cd_nom::INTEGER
LEFT JOIN gn_synthese.t_sources j_1
    ON j_1.name_source = t.id_source
LEFT JOIN gn_synthese.synthese j_pk
    ON j_pk.id_source = j_1.id_source
    AND (j_pk.entity_source_pk_value = SPLIT_PART(t.id_synthese, '|', 2)
      OR (j_pk.entity_source_pk_value IS NULL AND SPLIT_PART(t.id_synthese, '|', 2) IS NULL))
GROUP BY j_0.cd_nom, j_1.id_source, t.entity_source_pk_value, t.nom_cite, t.date_min, t.date_max, j_pk.id_synthese
;


-- Comptage insert

WITH d AS (
    SELECT
        DISTINCT id_source, entity_source_pk_value
    FROM gn_modulator_import.v_xxx_process_syn_synthese
    WHERE id_synthese IS NULL
)
SELECT
    COUNT(*)
FROM d
;


-- Comptage update

    WITH process_cor_observers AS (
        SELECT
            id_synthese,
            ARRAY_AGG(id_role) AS id_role
            FROM gn_modulator_import.v_xxx_process_syn_synthese_cor_observers
            GROUP BY id_synthese
    ), cor_cor_observers AS (
        SELECT
            id_synthese,
            ARRAY_AGG(id_role) AS id_role
            FROM gn_synthese.cor_observer_synthese
            GROUP BY id_synthese
    )
SELECT
    COUNT(*)
FROM gn_synthese.synthese t
JOIN gn_modulator_import.v_xxx_process_syn_synthese a
    ON a.id_synthese = t.id_synthese
    LEFT JOIN process_cor_observers
        ON process_cor_observers.id_synthese = t.id_synthese
    LEFT JOIN cor_cor_observers
        ON cor_cor_observers.id_synthese = t.id_synthese
WHERE (t.cd_nom IS DISTINCT FROM a.cd_nom)
    OR (t.id_source IS DISTINCT FROM a.id_source)
    OR (t.entity_source_pk_value IS DISTINCT FROM a.entity_source_pk_value)
    OR (t.nom_cite IS DISTINCT FROM a.nom_cite)
    OR (t.date_min IS DISTINCT FROM a.date_min)
    OR (t.date_max IS DISTINCT FROM a.date_max)
    OR process_cor_observers.id_role IS DISTINCT FROM cor_cor_observers.id_role
;


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
FROM gn_modulator_import.v_xxx_process_syn_synthese WHERE id_synthese IS NULL
;


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
    FROM gn_modulator_import.v_xxx_process_syn_synthese
)p
WHERE p.id_synthese = t.id_synthese
  AND NOT (
    (t.cd_nom IS DISTINCT FROM p.cd_nom)
    AND (t.id_source IS DISTINCT FROM p.id_source)
    AND (t.entity_source_pk_value IS DISTINCT FROM p.entity_source_pk_value)
    AND (t.nom_cite IS DISTINCT FROM p.nom_cite)
    AND (t.date_min IS DISTINCT FROM p.date_min)
    AND (t.date_max IS DISTINCT FROM p.date_max)
    AND (t.id_synthese IS DISTINCT FROM p.id_synthese)
)
;


-- - Traitement relations n-n

--   - cor_observers
--     - import

DROP VIEW IF EXISTS gn_modulator_import.v_xxx_process_syn_synthese_cor_observers CASCADE;
CREATE VIEW gn_modulator_import.v_xxx_process_syn_synthese_cor_observers AS
WITH unnest_cor_observers AS (
    SELECT
        id_import,
        id_synthese,
        TRIM(UNNEST(STRING_TO_ARRAY(cor_observers, ','))) AS cor_observers
        FROM gn_modulator_import.v_xxx_raw_syn_synthese
), remove_doublons AS (
    SELECT min(id_import) as id_import
    FROM gn_modulator_import.v_xxx_raw_syn_synthese
    GROUP BY id_synthese
)
SELECT
    t.id_import,
    j_0.id_role,
    j_pk.id_synthese
FROM unnest_cor_observers AS t
JOIN remove_doublons r ON r.id_import = t.id_import
LEFT JOIN utilisateurs.t_roles j_0
    ON j_0.identifiant = t.cor_observers
LEFT JOIN gn_synthese.t_sources j_pk_0
    ON j_pk_0.name_source = SPLIT_PART(t.id_synthese, '|', 1)
LEFT JOIN gn_synthese.synthese j_pk
    ON j_pk.id_source = j_pk_0.id_source
    AND (j_pk.entity_source_pk_value = SPLIT_PART(t.id_synthese, '|', 2)
      OR (j_pk.entity_source_pk_value IS NULL AND SPLIT_PART(t.id_synthese, '|', 2) IS NULL));


--     - suppression

DELETE FROM gn_synthese.cor_observer_synthese t
    USING gn_modulator_import.v_xxx_process_syn_synthese_cor_observers j
    WHERE t.id_synthese = j.id_synthese;


--     - insertion

INSERT INTO gn_synthese.cor_observer_synthese (
    id_role,
    id_synthese
)
SELECT
    id_role,
    id_synthese
FROM gn_modulator_import.v_xxx_process_syn_synthese_cor_observers
;


