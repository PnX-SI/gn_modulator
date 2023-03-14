## Exemple d'import simple sur `ref_geo.l_areas`

Nous allons voir un exemple d'import d'un fichier csv dans la table `ref_geo.l_areas` a fin d'illustration. Ici les champs correspondent exactement à ceux de la table destinataire.

### 1) Données

Ici les champs d'unicité sont
- `id_type` : pour ce champs on fourni la valeur de `type_code` du type d'aire qui permettra de retrouver `id_type`
- `area_code`

Le champ `geom` peut être renseigné au format `WKT` ou `WKB`, il doit bien être de la même projection que la colonne destinaire.



```
id_type,area_name, aera_code,geom
ZC,Parc National du Triangle,PNTRI,"POLYGON((6.48 48.87, 5.22 47.84, 6.87 47.96, 6.48 48.87))"
ZC,Parc National du Carré,PNCAR,"POLYGON((3.29 45.05, 5.49 44.91, 5.42 43.80, 3.12 44.11, 3.29 45.05))"
```

La commande de creation de table va être:

```
CREATE TABLE IF NOT EXISTS gn_modulator_import.t_xxx_data (
    id_import SERIAL NOT NULL,
    id_type VARCHAR,
    area_name VARCHAR,
    area_code VARCHAR,
    geom VARCHAR,
    CONSTRAINT pk_gn_modulator_import_t_xxx_data_id_import PRIMARY KEY (id_import)
);
```

### 2) Mapping

Pas de mapping pour cet exemple, les champs du fichiers csv correspondent aux champs de la table destinataire.

### 4) Vue brute (`raw`)

Ici, seul le champs de `geom` doit être converti en géométrie.

```
CREATE VIEW gn_modulator_import.v_xxx_raw_ref_geo_area AS
WITH pre_process AS (
SELECT
    id_import,
    id_type,
    area_name,
    area_code,
    ST_MULTI(
        ST_SETSRID(
            ST_FORCE2D(
                geom::GEOMETRY
            ), 2154
        )
    )
    AS geom
FROM gn_modulator_import.t_xxx_data
)
SELECT
    CONCAT(pp.id_type, '|', pp.area_code) AS id_area,
    pp.id_import,
    pp.id_type,
    pp.area_name,
    pp.area_code,
    pp.geom
FROM pre_process pp;
```

### 5) Vue process

Cette vue permet de résoudre les clé étrangère et la clé primaire.

- `id_type`: avec une jointure sur `ref_geo.bib_areas_types` et une condition sur `type_code`
- `id_area`: les champs d'unicité sont `id_type` et `area_code`
  - on se ressert de la jointurte précédente pour avoir la valeur de `id_type`
  - on fait une jointure sur la table `ref_geo.l_areas` avec des condition sur `id_type` et `area_code`
```

CREATE VIEW gn_modulator_import.v_260_process_ref_geo_area AS
SELECT
    id_import,
    j_0.id_type AS id_type,
    t.area_name AS area_name,
    t.area_code AS area_code,
    t.geom AS geom,
    j_pk.id_area
FROM gn_modulator_import.v_260_raw_ref_geo_area t
LEFT JOIN ref_geo.bib_areas_types j_0 ON
      j_0.type_code::TEXT = t.id_type::TEXT
LEFT JOIN ref_geo.l_areas j_pk ON
      j_pk.id_type::TEXT = j_0.id_type::TEXT
        AND (j_pk.area_code::TEXT = SPLIT_PART(t.id_area, '|', 2)::TEXT OR (j_pk.area_code IS NULL AND SPLIT_PART(t.id_area, '|', 2) IS NULL));


```