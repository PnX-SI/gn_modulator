#
# Script d'insert des données SIPAF provenant du fichier passage_faune_v3.ods
#
#
# options
#   -x : debug
#   -v : verbose
#   -g : geonature_dir
#
# stop on error
set -eo pipefail


# 0) Initialisation


# - set variables

current_script=$(readlink -f "$0")
data_dir=$(dirname "${current_script}")

utils_file=${data_dir}/utils.sh


source_ods=${data_dir}/sources/passage_faune_v3.ods
source_csv=${source_ods%%.ods}.csv
source_sql=${source_ods%%.ods}.sql

# log

log_file=${data_dir}/sources/insert_data_sipaf.log
echo "Insert data sipaf" > $log_file
date >> $log_file

# - chargement des fonctions utiles

. ${utils_file}


# - options de script et tests

parseScriptOptions "${@}"

if [ ! -d "${geonature_dir}" ]; then
    log_process "Erreur : le dossier de geonature ${geonature_dir} n'est pas correctement défini"
    exit 1;
fi


. ${geonature_dir}/config/settings.ini
export PGPASSWORD=${user_pg_pass};

# 1) ods -> csv

if [ ! -f "${source_csv}" ]; then
# --infilter pour gérer les accents
# https://unix.stackexchange.com/questions/259361/specify-encoding-with-libreoffice-convert-to-csv
# libreoffice --convert-to csv:"59" --infilter=CSV:44,34,76,1 --outdir ${data_dir}/sources ${source_ods}
unoconv -f csv -e FilterOptions="59,34,0,0" ${source_ods}
fi

# 2) csv -> sql

echo "DROP TABLE IF EXISTS sipaf.tmp_import_sipaf;" > ${source_sql}
csvsql ${source_csv} --no-constraints --tables sipaf.tmp_import_sipaf | sed \
    -e 's/DECIMAL/VARCHAR/g' \
    -e 's/BOOLEAN/VARCHAR/g' \
    -e 's/, /,/g' \
    -e 's/"//g' >> ${source_sql}


cp ${source_csv} /tmp/source.csv

# 3) sql

psqla -c "DROP SCHEMA IF EXISTS sipaf CASCADE;"
psqla -c "DROP SCHEMA IF EXISTS gn_modulator CASCADE;"

psqla -f ${data_dir}/reset_sipaf.sql
gn_venv

# patch pourris maj modules en attendant alembic
geonature modulator sql_process -n modules.module -e

geonature modulator install SIPAF

psqla -f ${source_sql}
cat ${source_csv} | psqla -c "COPY sipaf.tmp_import_sipaf FROM STDIN CSV HEADER DELIMITER ';';"
# psqla -f ${data_dir}/schema_sipaf.sql

# insert routes
${data_dir}/insert_routes.sh -g "${geonature_dir}"

geonature modulator data ${data_dir}/../config/modules/sipaf/features/pf.json

# psqla -f ${data_dir}/import_sipaf.sql
# psqla -f ${data_dir}/patch_sipaf_dataset.sql

# psqla -f ${data_dir}/after_import.sql


