#!/bin/bash

#   utils.sh
#
#   Variables etFonction pour l'import des données
#
#   Variables
#
#       psqla: commande psql avec les options pour la bdd geonature
#
#   Fonctions:
#
#       log_process : pour procéder aux log écran ou fichier
#       parseScriptOptions : gestion des paramètres de script
#       printScriptUsage : affichage de l'aide pour le script


# DESC: Usage help
# ARGS: None
# OUTS: None
function printScriptUsage() {
  cat << EOF
Usage: ./$(basename $BASH_SOURCE)[options]
     -h | --help: display this help
     -g | --geonature-dir: geonature directory
     -v | --verbose: display more infos
     -x | --debug: display debug script infos
EOF
  exit 0
}

# DESC: Parameter parser
# ARGS: $@ (optional): Arguments provided to the script
# OUTS: Variables indicating command-line parameters and options
function parseScriptOptions() {
  # Transform long options to short ones
  for arg in "${@}"; do
    shift
    case "${arg}" in
      "--help") set -- "${@}" "-h" ;;
      "--verbose") set -- "${@}" "-v" ;;
      "--debug") set -- "${@}" "-x" ;;
      "--geonature-dir") set -- "${@}" "-g" ;;
      "--"*) echo "ERROR : parameter '${arg}' invalid ! Use -h option to know more."; exit 1;;
      *) set -- "${@}" "${arg}"
    esac
  done

  while getopts "hvxdg:" option; do
    case "${option}" in
      "h") printScriptUsage ;;
      "v") readonly VERBOSE=true ;;
      "x") readonly DEBUG=true; set -x ;;
      "g") readonly geonature_dir=${OPTARG}; ;;
      *) echo "ERROR : parameter invalid ! Use -h option to know more."; exit 1;;
    esac
  done
}


# log_process
#
# but:
#   affiche un message ou l'écrit à la fin du fichier
#
# input:
#   $1: msg, message à logger
#
log_process() {
    msg="${@}"
    if [ ! -z "$VERBOSE" ]; then
        echo $msg
    fi
    if [ ! -z "$log_file" ]; then
        echo $msg >> $log_file
    fi
}

psqla() {
    . ${geonature_dir}/config/settings.ini
    export PGPASSWORD=${user_pg_pass}; psql -d ${db_name} -h ${db_host} -U ${user_pg} -p ${db_port} -v ON_ERROR_STOP=1 "${@}"
}