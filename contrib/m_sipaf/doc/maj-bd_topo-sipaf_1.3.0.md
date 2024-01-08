# Mise à jour du Référentiel Géographique

Ajout de linéaires pour les voies navigables.

## Ajout de type de linéaires et points

```
geonature modulator features bd_topo.type
```

## Récupération des données

- https://outils.cevennes-parcnational.net/demo-sipaf/geonature/api/media/linear_group_vn.csv
- https://outils.cevennes-parcnational.net/demo-sipaf/geonature/api/media/linear_vn.csv

## Intégration et import des données

Adapter `data_path` pour les commandes suivantes

```

# Voies navigables
geonature modulator import -m MODULATOR -o ref_geo.linear_group -d ${data_path}/linear_group_vn.csv
geonature modulator import -m MODULATOR -o ref_geo.linear -d ${data_path}/linear_vn.csv

```

# Corrélation entre passages à faune et ref_geo

```
SELECT pr_sipaf.process_all_cor_linear_pf();
```
