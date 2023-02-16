## Import de données

### Commande d'import

```
geonature modules import
```

### Exemple d'import de données


#### Import simple depuis un fichier csv *(bien formatté)*

```
geonature modules import -s m_sipaf.pf -d <chemin vers le fichier csv>
```

Cette commande va intégrer (s'il y a correspondance des champs), pour chaque ligne du fichier csv il peut s'agir :
- d'une insertion si la données n'exisite pas
- d'une mise à jour si la données est modifié
- si la ligne existe et que la données n'est pas modifiée on ne fait rien

#### Import avec mapping des données

```
geonature modules import -s m_sipaf.pf -d <chemin vers le fichier csv> -p <chemin vers le fichier pre_process.sql de mapping>
```

où `pre_process` est une vue qui va transformer les colonnes du fichier csv en colonnes assimilables par la table destinataire. (il est très important de garder les noms `:pre_processed_import_view` et `:raw_import_table`)

```
DROP VIEW IF EXISTS :pre_processed_import_view;
CREATE VIEW :pre_processed_import_view AS
SELECT
	uuid_pf AS id_passage_faune,
	CASE
		WHEN type_role_org = 'Concessionaire' THEN 'CON'
		WHEN type_role_org = 'ETAT' THEN 'ETA'
		WHEN type_role_org = 'Département' THEN 'DEP'
		WHEN type_role_org = 'Gestionnaire' THEN 'GES'
		ELSE '???'
	END AS id_nomenclature_type_actor,
	nom_organism AS id_organism,
    NULL AS id_role
	FROM :raw_import_table t
	WHERE nom_organism IS NOT NULL AND nom_organism != ''
;
```


#### Plusieurs imports depuis un fichier csv

```
geonature modules import -i <import_code> -d <data_dir>
```

avec:
    - `<import_code>` le code de l'import
    - `<data_dir>` liens vers le dossier contenant les données

Nous avons par exemple l'import de code `m_sipaf.pf_V1` et défini dans le fichier [m_sipaf.pf_V1.import.yml](../config/modules/contrib/m_sipaf/imports/m_sipaf.pf_V1.import.yml) qui permet d'importer les organismes, passages à - faune et acteurs depuis le même fichier csv et avec un mapping spécifique à chaque destinaire.


```
type: import
code: m_sipaf.pf_V1
title: Données d'exemple m_sipaf
description: import données d'exemple de passage à faune pour SIPAF
items:
  - schema_code: user.organisme
    data: pf_V1.csv
    pre_process: scripts/ppi_organism_V1.sql
  - schema_code: m_sipaf.pf
    data: pf_V1.csv
    pre_process: scripts/ppi_pf_V1.sql
    keep_raw: true
  - schema_code: m_sipaf.actor
    data: pf_V1.csv
    pre_process: scripts/ppi_actor_V1.sql
    keep_raw: true
```
