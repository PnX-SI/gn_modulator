shapefile=$1
schema_name=$2
table_name=$3

export PGPASSWORD=$user_pg_pass;

sql_test_table_exists="SELECT
    table_schema, table_name
    FROM information_schema.tables
    WHERE
        LOWER(table_schema) = LOWER('$schema_name')
        AND LOWER(table_name)   = LOWER('$table_name')
    "

test_table_exists=$(psql -h $db_host -U $user_pg -d $db_name -t -c "$sql_test_table_exists")
if [ -z "$test_table_exists" ]; then
    echo insert_shape_in_db ${schema_name}.${table_name}
    psql -h $db_host -U $user_pg -d $db_name -c "CREATE SCHEMA IF NOT EXISTS ${schema_name}"
    ogr2ogr -f PostgreSQL PG:"dbname='${db_name}' host='${db_host}' port='${db_port}' user='${user_pg}' password='${user_pg_pass}'" -lco SCHEMA=${schema_name} -lco GEOMETRY_NAME=geom -lco FID=gid -lco SPATIAL_INDEX=GIST -nlt PROMOTE_TO_MULTI -nln ${table_name} -overwrite ${shapefile}
else
    a=1
    # echo insert shape into db: table ${schema_name}.${table_name} already exists
fi
