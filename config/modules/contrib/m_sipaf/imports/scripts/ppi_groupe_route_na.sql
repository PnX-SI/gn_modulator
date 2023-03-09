DROP VIEW IF EXISTS :pre_processed_import_view CASCADE;
CREATE VIEW :pre_processed_import_view AS
SELECT DISTINCT ON(id_import)
    'RTE' AS id_type,
    numero AS code,
    cl_admin || ' ' || numero AS name
    FROM :table_data
    ORDER BY id_import