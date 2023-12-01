#
data_sinp_zip=$1
geonature_settings=$2

process_csv()
{
    csv_file=$1
    table_name=$2
    delimiter=";"
    fields=$(head -n 1 $csv_file)
    fields_table=$(echo $fields | sed "s/${delimiter}/ VARCHAR,\n/g")" VARCHAR"
    fields_copy=$(echo $fields | sed "s/${delimiter}/, /g")

    test_exists="SELECT EXISTS (SELECT 1 FROM ${table_name})"

    $psqla -c "$test_exists" &>  /dev/null && return 1

    create_table_sql="
CREATE TABLE ${table_name} (
    ${fields_table}
)
;
"
    sql_copy="
COPY ${table_name}(${fields_copy})
    FROM STDIN
    DELIMITER '${delimiter}'
    CSV HEADER
;
"

    $psqla -c "$create_table_sql" > /dev/null
    cat "${csv_file}" | $psqla -c "$sql_copy" > /dev/null
}

process_shape() 
{
    shape_file=$1
    table_name=$2

    ogr2ogr \
        -f PostgreSQL PG:"dbname='${db_name}' host='${db_host}' port='${db_port}' user='${user_pg}' password='${user_pg_pass}'" \
        -lco GEOMETRY_NAME=geom \
        -lco FID=gid \
        -lco SPATIAL_INDEX=GIST \
        -nlt PROMOTE_TO_MULTI \
        -nln ${table_name} \
        -overwrite \
        $shape_file

}

# settings geonature & bdd
[ ! -f "${geonature_settings}" ] && echo "Le fichier de config de geonature n'a pas été trouvé" && exit 1
set -a; source $geonature_settings; set +a
export PGPASSWORD=$user_pg_pass
psqla="psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1"
$psqla -c "SELECT 1" > /dev/null || (echo "La configuration de base de données n'est pas valide" && exit 1)


script_dir=$(dirname $0)
output_dir=$script_dir/../processed/sinp
mkdir -p "${output_dir}"

data_dir=$(dirname ${data_sinp_zip})
data_filename=$(basename ${data_sinp_zip})

output_csv_file=$output_dir/${data_filename%%.zip}.csv


if [ ! -d "${data_sinp_dir}" ]; then 
    data_sinp_dir=${data_dir}/${data_filename%%.zip}
    mkdir -p ${data_sinp_dir}
    unzip -o -d ${data_sinp_dir} ${data_sinp_zip} > /dev/null
fi
# import des fichier dans des tables


$psqla -c "DROP SCHEMA IF EXISTS import_sinp_sipaf CASCADE" > /dev/null
$psqla -c "CREATE SCHEMA IF NOT EXISTS import_sinp_sipaf" > /dev/null

# - fichiers csv
process_csv ${data_sinp_dir}/St_Principal.csv import_sinp_sipaf.st_principal
process_csv ${data_sinp_dir}/St_Descr.csv import_sinp_sipaf.st_descr
process_csv ${data_sinp_dir}/St_AttrAdd_Suj.csv import_sinp_sipaf.st_attr_add
process_csv ${data_sinp_dir}/St_Regrp.csv import_sinp_sipaf.st_regrp
process_csv ${data_sinp_dir}/St_Communes.csv import_sinp_sipaf.st_communes
process_csv ${data_sinp_dir}/St_Departements.csv import_sinp_sipaf.st_departements
process_csv ${data_sinp_dir}/St_Mailles.csv import_sinp_sipaf.st_mailles

# - fichier shapes
process_shape ${data_sinp_dir}/point.shp import_sinp_sipaf.point
process_shape ${data_sinp_dir}/ligne.shp import_sinp_sipaf.ligne
process_shape ${data_sinp_dir}/polygone.shp import_sinp_sipaf.polygone

# - bilan nombre de données
$psqla -c "
WITH pre AS (
    SELECT 'st_principal' as t, count(*) as c FROM import_sinp_sipaf.st_principal
    UNION SELECT 'st_descr' as t, count(*) as c FROM import_sinp_sipaf.st_descr
    UNION SELECT 'st_attr_add' as t, count(*) as c FROM import_sinp_sipaf.st_attr_add
    UNION SELECT 'st_regrp' as t, count(*) as c FROM import_sinp_sipaf.st_regrp
    UNION SELECT 'st_communes' as t, count(*) as c FROM import_sinp_sipaf.st_communes
    UNION SELECT 'st_departements' as t, count(*) as c FROM import_sinp_sipaf.st_departements
    UNION SELECT 'st_mailles' as t, count(*) as c FROM import_sinp_sipaf.st_mailles
    UNION SELECT 'point' as t, count(*) as c FROM import_sinp_sipaf.point
    UNION SELECT 'ligne' as t, count(*) as c FROM import_sinp_sipaf.ligne
    UNION SELECT 'polygone' as t, count(*) as c FROM import_sinp_sipaf.polygone
)
SELECT
    t, c
FROM pre
ORDER BY c DESC
"

# creation vue pour csv
$psqla -f ${script_dir}/process_sinp.sql > /dev/null
$psqla -c "COPY (SELECT * FROM import_sinp_sipaf.v_sinp) TO STDOUT WITH CSV HEADER DELIMITER ';'" > $output_csv_file
