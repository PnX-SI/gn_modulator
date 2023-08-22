#
# Script de traitement des données la bd_topo
# ( téléchargées au préalable par le script fetch_bd_topo.sh)

# set -x
set -e

geonature_settings=$1

if [ -z "$geonature_settings" ]; then
    echo "Veuillez renseigner le chemin de ficher settings.ini de geonature"
    exit 1
fi

if [ ! -f $geonature_settings ]; then
    echo "Le fichier de settings $geonature_settings n'existe pas"
    exit 1
fi


current_script=$(readlink -f "$0")
current_dir=$(dirname "${current_script}")
script_dir=${current_dir}
source_dir=${current_dir}/../sources/bd_topo/
processed_dir=${current_dir}/../processed/bd_topo/

mkdir -p $processed_dir

source ${current_dir}/.data

set -a; source $geonature_settings; set +a

# Insertion dans la base de données
for data_type in $(echo $DATA_TYPES); do
    $script_dir/insert_shape_in_db.sh $source_dir/shapes/${data_type}.shp bd_topo ${data_type}
done

# scnf
for data_type in $(echo $DATA_SNCF_TYPES); do
    $script_dir/insert_shape_in_db.sh $source_dir/shapes/$data_type.shp bd_topo ${data_type//-/_}
done

# Process bd topo route
csv_linear_group_route=$processed_dir/linear_group_route.csv
csv_linear_route=$processed_dir/linear_route.csv

if [ ! -f $csv_linear_route ]; then
    export PGPASSWORD=$user_pg_pass;
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -f $script_dir/process_bd_topo_route.sql
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -c "COPY (SELECT * FROM BD_TOPO.IMPORT_LINEAR_GROUP_ROUTE) TO STDOUT WITH CSV HEADER DELIMITER ';'" > $csv_linear_group_route
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -c "COPY (SELECT * FROM BD_TOPO.IMPORT_LINEAR_ROUTE) TO STDOUT WITH CSV HEADER DELIMITER ';'" > $csv_linear_route
fi

# Process bd_topo voie ferre
csv_linear_group_vf=$processed_dir/linear_group_vf.csv
csv_linear_vf=$processed_dir/linear_vf.csv
if [ ! -f $csv_linear_vf ]; then
    export PGPASSWORD=$user_pg_pass;
      psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -f $script_dir/process_bd_topo_vf.sql
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -c "COPY (SELECT * FROM BD_TOPO.IMPORT_LINEAR_GROUP_vf) TO STDOUT WITH CSV HEADER DELIMITER ';'" > $csv_linear_group_vf
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -c "COPY (SELECT * FROM BD_TOPO.IMPORT_LINEAR_vf) TO STDOUT WITH CSV HEADER DELIMITER ';'" > $csv_linear_vf
fi

# Process bd_topo pkpr
csv_point_pkpr=$processed_dir/point_pkpr.csv
if [ ! -f $csv_point_pkpr ]; then
    export PGPASSWORD=$user_pg_pass;
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -f $script_dir/process_bd_topo_pkpr.sql
    psql -h $db_host -U $user_pg -d $db_name -v ON_ERROR_STOP=1 -c "COPY (SELECT * FROM BD_TOPO.IMPORT_point_pkpr) TO STDOUT WITH CSV HEADER DELIMITER ';'" > $csv_point_pkpr
fi
