DROP VIEW IF EXISTS :pre_processed_import_view CASCADE;
CREATE VIEW :pre_processed_import_view AS
SELECT DISTINCT
    'RTE' AS id_type,
    numero AS code,
    cl_admin || ' ' || numero AS name
