# Mise à jour du Référentiel Géographique


## Ajout de type de linéaires et points

```
    geonature modulator features bd_topo.type
```

## Remise à zéros du RefGeo Linéaire

```
DELETE FROM PR_SIPAF.COR_LINEAR_PF;
DELETE FROM REF_GEO.COR_AREAS;
DELETE FROM REF_GEO.COR_LINEAR_AREA;
DELETE FROM REF_GEO.COR_LINEAR_GROUP;
DELETE FROM REF_GEO.T_LINEAR_GROUPS;
DELETE FROM REF_GEO.L_LINEARS;
```

## Récupération des données

- https://outils.cevennes-parcnational.net/demo-sipaf/geonature/api/media/bd_topo.zip


## Intégration et import des données

Adapter `data_path` pour les commandes suivantes
```
    # route
    geonature modulator import -m MODULATOR -o ref_geo.linear_group -d ${data_path}/linear_group_route.csv
    geonature modulator import -m MODULATOR -o ref_geo.linear -d ${data_path}/linear_route.csv

    # voie ferree
    geonature modulator import -m MODULATOR -o ref_geo.linear_group -d ${data_path}/linear_group_vf.csv
    geonature modulator import -m MODULATOR -o ref_geo.linear -d ${data_path}/linear_vf.csv

    # point de repère
    geonature modulator import -m MODULATOR -o ref_geo.point -d ${data_path}/point_pkpr.csv

```

# Corrélation aires-lineaires

```
INSERT INTO ref_geo.cor_linear_area (id_linear, id_area)
  SELECT  id_linear, id_area
    FROM ref_geo.l_areas la
    JOIN ref_geo.l_linears ll ON la.geom && ll.geom
    JOIN ref_geo.bib_areas_types bat ON bat.id_type =la.id_type
    WHERE bat.type_code IN ('DEP', 'REG', 'COM')
;

```

# Corrélation passages à faune-ref_geo

```
SELECT pr_sipaf.process_all_cor_area_pf();
SELECT pr_sipaf.process_all_cor_linear_pf();
```
