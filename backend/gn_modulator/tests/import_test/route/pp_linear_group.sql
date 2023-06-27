SELECT
    DISTINCT ON (id_import)
    id_import,
    'RTE' AS id_type,
    numero AS code,
    cl_admin || ' ' || numero AS name
    FROM :table_data
    ORDER BY id_import
