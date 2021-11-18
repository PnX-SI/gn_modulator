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



# 1) ods -> csv

log_process 'ODS -> CSV'
# --infilter pour gérer les accents
# https://unix.stackexchange.com/questions/259361/specify-encoding-with-libreoffice-convert-to-csv
# libreoffice --convert-to csv:"59" --infilter=CSV:44,34,76,1 --outdir ${data_dir}/sources ${source_ods}
gn_venv && deactivate
unoconv -f csv -e FilterOptions="59,34,0,0" ${source_ods}

# 2) csv -> sql
. ${geonature_dir}/config/settings.ini
export PGPASSWORD=${user_pg_pass};

echo "DROP TABLE IF EXISTS public.tmp_import_sipaf;" > ${source_sql}
csvsql ${source_csv} --no-constraints --tables public.tmp_import_sipaf | sed \
    -e 's/DECIMAL/VARCHAR/g' \
    -e 's/BOOLEAN/VARCHAR/g' \
    -e 's/, /,/g' \
    -e 's/"//g' >> ${source_sql}

cp ${source_csv} /tmp/source.csv

# 3) sql

psqla -c 'DROP SCHEMA IF EXISTS sipaf CASCADE;'
psqla -f ${source_sql}
cat ${source_csv} | psqla -c "COPY public.tmp_import_sipaf FROM STDIN CSV HEADER DELIMITER ';';"
# psqla -f ${data_dir}/schema_sipaf.sql
gn_venv
geonature modules sql_process -n schemas.sipaf.pf > ${data_dir}/schema_sipaf.sql
psqla -f ${data_dir}/schema_sipaf.sql
psqla -f ${data_dir}/import_sipaf.sql

