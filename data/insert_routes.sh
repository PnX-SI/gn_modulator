# un7zip

current_script=$(readlink -f "$0")
data_dir=$(dirname "${current_script}")

utils_file=${data_dir}/utils.sh

log_file=${data_dir}/sources/insert_routes.log

# - chargement des fonctions utiles

. ${utils_file}


# - options de script et tests

parseScriptOptions "${@}"


if [ ! -d "${geonature_dir}" ]; then
    log_process "Erreur : le dossier de geonature ${geonature_dir} n'est pas correctement défini"
    exit 1;
fi


if [ ! -f "${data_dir}/sources/routes/autoroutes.shp" ]; then
    cd ${data_dir}/sources/routes
    7z x autoroutes.shp
    7z x routes-nationales.shp
fi

. ${geonature_dir}/config/settings.ini
export PGPASSWORD=${user_pg_pass};

psqla -c 'DROP TABLE IF EXISTS  sipaf.tmp_import_autoroutes'
psqla -c 'DROP TABLE IF EXISTS  sipaf.tmp_import_routes_nationales'
shp2pgsql -s 2154 -I "${data_dir}/sources/routes/autoroutes.shp" sipaf.tmp_import_autoroutes | psqla > $log_file
shp2pgsql -s 2154 -I "${data_dir}/sources/routes/routes_nationales.shp" sipaf.tmp_import_routes_nationales | psqla > $log_file

psqla -f "${data_dir}/insert_routes.sql"
