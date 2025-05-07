# Données INPN

## Procédure de création d'un fichier csv destiné à l'import

-  1) rapatrier le fichier de données `Demande_4192.zip`.

```
- St_Communes.csv
- St_Descr.csv
- St_Principal.csv
- St_AttrAdd_Suj.csv
- St_Departements.csv
- St_Mailles.csv  St_Regrp.csv

- point.shp
- ...
- ligne.shp
- ...
- polygone.shp
- ...

- CA.xlsx   
- JDD.xlsx  
```

- 2)  Le placer dans le dossier `<gn_modulator>/contrib/m_sipaf/data/sources/inpn`

```
    mv Demande_4192.zip <gn_modulator>/contrib/m_sipaf/data/sources/inpn/.
```

- 3) Se placer dans le dossier `<gn_modulator>/contrib/m_sipaf/data/` et lancer la commande suivante


```
./scripts/process_inpn.sh sources/inpn/Demande_4192.zip <GeoNature>/config/settings.ini
```

Le fichier `settings.ini` peut être le fichier de configuration de GeoNature, mais peut aussi être un fichier contenant les accès à une base de données postgres.

```
db_host=localhost
db_port=5432
db_name=geonature
user_pg=xxx
user_pg_pass=xxx
```

Le fichier csv est créé à l'emplacement `gn_modulator>/contrib/m_sipaf/data/processed/inpn/Demande_4192.csv`

4) Refaire ce fichier

On peut jouer sur le fichier [data/scripts/process_inpn.sql](../data/scripts/process_inpn.sql) pour changer les données (ajouter les données sensibles par exemple)

Il faut supprimer le fichier `gn_modulator>/contrib/m_sipaf/data/processed/inpn/Demande_4192.csv` pour pouvoir le recréer avec la commande précédente.
