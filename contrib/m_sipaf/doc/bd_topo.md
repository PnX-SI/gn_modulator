# Gestion des référentiels géographique

## I - Téléchargement de la BD_TOPO

Les données de la bd_topo sont disponibles sur le site à cette adresse.

https://geoservices.ign.fr/bdtopo#telechargementshpreg

Pour les données des voies ferrées, on utilise aussi le fichier `lignes par statut` et `lignes-lgv-et-par-ecartement` pour avoir accès au nom des lignes (non disponible dans la bd_topo)

https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/lignes-par-statut/exports/shp?lang=fr&timezone=Europe%2FParis

https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/lignes-lgv-et-par-ecartement/exports/shp?lang=fr&timezone=Europe%2FParis


Les données sont téléchargeables par région.

Pour Télécharger ces données vous pouvez exécuter le script suivant.

`<m_sipaf>/data/script/fetch_bd_topo.sh`

Ces données seront placées dans le dossier

`<m_sipaf>/data/sources/bd_topo`

Dans le fichier `<m_sipaf>/data/script/.data` script vous pouvez modifier les valeurs des variables :

```
BD_TOPO_DATE="2023-06-15"
BD_TOPO_VERSION="3-3"
```

## II - Création des fichiers csv destinés à l'import


### WIP

Étapes:
    - regrouper les shapefiles par theme
    - en base ?
    - traitement
        - -> fichiers csv destinés à l'import ?

    - ROUTE_NUMEROTEE_OU_NOMMEE -> linear group
        - linear_code (id par ex ROUTNOMM0000000004055518)
    - TRONCON_DE_ROUTE
        - linear_code (id)
        - linear_name ?



```
<m_sipaf>/data/script/fetch_bd_topo.sh
```

Ce script va générer les fichiers suivants:

```
- <m_sipaf>/data/processed/bd_topo
    - linear_group_route.csv
    - linear_group_vf.csv
    - linear_route.csv
    - linear_vf.csv
    - point_pkpr.csv

```

## III - Import des données de la BD_TOPO dans la base GeoNature

Pour importer les données de la BD_TOPO dans la base, nous allons nous servir des fonctionalité d'import de modulator.

Les données ciblées sont

- les linéaires routiers (autoroutes, routes nationales, départementales)
- les linéaires des voies férrées ()

Données à faire ?

Linéaire des voies fluviales ??

### Type de géométrie

Pour insérer les types de linéaires correspondant à la bd_topo:
- routes
    - autoroutes
    - nationales
    - départementales
- voies férrées
    - LGV
    - principales ?

```
    geonature modulator features bd_topo.type
```

### Import des geometries

```
    # route
    data_path=data/processed/bd_topo
    geonature modulator import -m MODULATOR -o ref_geo.linear_group -d ${data_path}/linear_group_route.csv
    geonature modulator import -m MODULATOR -o ref_geo.linear -d ${data_path}/linear_route.csv

    # voie ferree
    geonature modulator import -m MODULATOR -o ref_geo.linear_group -d ${data_path}/linear_group_vf.csv
    geonature modulator import -m MODULATOR -o ref_geo.linear -d ${data_path}/linear_vf.csv

    # point de repère
    geonature modulator import -m MODULATOR -o ref_geo.point -d ${data_path}/point_pkpr.csv

```

