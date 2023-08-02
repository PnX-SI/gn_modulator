#
# Script permettant de récupérer les fichiers de bd_topo pour toutes les regions
#
# - Récupération des données par régions en utilisant lftp
#
#  - Voir la pagef de l'ign https://geoservices.ign.fr/bdtopo#telechargementshpreg
#
# - Codes région :
#
#   - R11 : Ile de France
#   - R24 : Centre-Val de Loire
#   - R27 : Bourgogne-Franche-Comté
#   - R28 : Normandie
#   - R32 : Hauts-de-France
#   - R44 : Grand Est
#   - R52 : Pays de la Loire
#   - R53 : Bretagne
#   - R75 : Nouvelle-Aquitaine
#   - R76 : Occitanie
#   - R84 : Auvergne-Rhône-Alpes
#   - R93 : Provence-Alpes-Côte d'Azur
#   - R94 : Corse
#
# DOM TOM ?? TODO

#set -ex pipefail

current_script=$(readlink -f "$0")
current_dir=$(dirname "${current_script}")
source_dir=${current_dir}/../sources/bd_topo
shapes_dir=${current_dir}/../sources/bd_topo/shapes
mkdir -p ${source_dir} ${shapes_dir}

# On récupère les donnée par ftp, pour chaque région

# REGION_CODES BD_TOPO_DATE BD_TOPO_VERSION
source $current_dir/.data

# Téléchargement des archives par région
for region_code in $(echo "$REGION_CODES");
do


    data_output_dir="${source_dir}/${region_code}"
    data_archives_dir="${source_dir}/archives"
    mkdir -p $data_output_dir
    mkdir -p $data_archives_dir
    data_archive_file_path="${data_archives_dir}/${region_code}.7z"

    url1='https://wxs.ign.fr/859x8t863h6a09o9o6fy4v60/telechargement/prepackage/'
    url2='BDTOPOV3-TOUSTHEMES-REGION-PACK_232$BDTOPO_'${BD_TOPO_VERSION}'_TOUSTHEMES_SHP_LAMB93_'${region_code}"_${BD_TOPO_DATE}/"
    url3="file/BDTOPO_${BD_TOPO_VERSION}_TOUSTHEMES_SHP_LAMB93_${region_code}_${BD_TOPO_DATE}.7z"
    url="${url1}${url2}${url3}"

    # Téléchargement du fichier (s'il n'est pas présent)
    if [ ! -f "${data_archive_file_path}" ]; then
        echo Fetch data for region $region_code
        wget -O $data_archive_file_path $url
    fi


    # Extraction des shapes
    ARCHIVE_FILTERS=""
    for data_type in $(echo $DATA_TYPES); do
        if [ ! -f ${data_output_dir}/${data_type}.shp ]; then
            ARCHIVE_FILTERS="$ARCHIVE_FILTERS ${data_type}*"
        fi
    done

    if [ ! -z "${ARCHIVE_FILTERS}" ]; then
        7z e -o${data_output_dir} ${data_archive_file_path} $ARCHIVE_FILTERS -r
    fi

done

# Regroupement des shapefiles en un seul fichier
for data_type in $(echo ${DATA_TYPES}); do

    shapefile=${shapes_dir}/${data_type}.shp
    shapefile_inter=${shapes_dir}/${data_type}_inter.shp

    if [ -f ${shapefile} ]; then
        continue
    fi

    echo process ${data_type}

    for region_code in $(echo ${REGION_CODES}); do

        region_shapefile=${source_dir}/$region_code/${data_type}.shp
        fields_data_type="fields_${data_type}"
        filter_data_type="filter_${data_type}"
        if [ -z "${!fields_data_type}" ]; then
            echo $fields_data_type
            eval "$fields_data_type='*'"
            echo $fields_data_type "${!fields_data_type}"
        fi
        sql_txt="SELECT '${region_code}' as shp_src, ${!fields_data_type} FROM ${data_type} ${!filter_data_type}"
        echo - ${region_code} : "$sql_txt"
        if [ ! -f ${shapefile} ]; then

            ogr2ogr \
                ${shapefile} \
                ${region_shapefile} \
                -lco ENCODING=UTF-8 \
                -sql "${sql_txt}"

        else

            ogr2ogr \
                -update \
                -append ${shapefile} \
                ${region_shapefile} \
                -sql "${sql_txt}"
        fi

	done

done

# fichier sncf formes-des-lignes-du-rfn 
for data_type in $(echo $DATA_SNCF_TYPES); do

    sncf_archive=$data_archives_dir/"$data_type.zip"
    sncf_shapefile=$shapes_dir/"$data_type.shp"

    if [ ! -f $sncf_archive ]; then
        wget -O $sncf_archive "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/$data_type/exports/shp?lang=fr&timezone=Europe%2FParis"
    fi

    if [ ! -f $sncf_shapefile ]; then
        unzip $sncf_archive -d $shapes_dir
    fi

done