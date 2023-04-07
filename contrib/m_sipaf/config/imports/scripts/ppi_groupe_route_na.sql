SELECT
    MIN(id_import) AS id_import,
    'RTE' AS id_type,
    numero AS code,
    cl_admin || ' ' || numero AS name
    FROM :table_data
    GROUP BY cl_admin, numero