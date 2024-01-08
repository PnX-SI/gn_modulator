# Mise en production SIPAF 1.3.0

## Mise à jour du module (déjà installés)

Rapatrier le module à la version voulue, puis installer les modules :

```
pip install -e <gn_modulator>/.
pip install -e <gn_modulator>/contrib/m_sipaf
```

Vérifier que les liens symboliques dans `<GeoNature>/backend/media/modulator` sont toujours valides, puis lancer la mise à jour de la BDD :

```
geonature db autoupgrade
```

## Features

Mettre à jour les features

```
geonature modulator features modulator.permissions
geonature modulator install m_sipaf
```

## MAJ du ref_geo, ajout des canaux

Voir le fichier [maj-bd_topo-sipaf_1.3.0](./maj-bd_topo-sipaf_1.3.0.md)

## A faire sur GeoNature

- Installer le module IMPORT
- Revoir les permissions des groupes d'utilisateurs
- Passer le paramètre `AUTO_DATASET_CREATION` à `False` pour ne plus créer automatiquement un CA et JDD à chaque fois qu'un utilisateur créé un compte + Supprimer les CA et JDD individuels créés automatiquement jusque là
- Revoir la conf du formulaire de création de compte ? A vérifier avec CEREMA
- Mettre à jour la charte d'utilisation ? A vérifier avec CEREMA
- Basculer sur BBOX mondiale pour inclure les DOM - Conf GN globale
  - choix de `MAP_CONFIG` `zoom_level` dans `geonature_config.toml`
- Ajouter vue d'export des PAF dans schéma gn_imports
- Intégrer canaux dans Ref_Geo (cf ci-dessus)
- Importer extraction INPN (données non sensibles uniquement) - PNE avec module IMPORT après MEP
- Modifier la conf GN pour ajouter la couche additionnelle des PAF dans les autres modules :
```
[[MAPCONFIG.REF_LAYERS]]
   code = "passages_faune"
   label = "Passages à faune G"
   type = "geojson"
   url = "http://localhost:8000/modulator/rest/m_sipaf/site/?sort=id_passage_faune&fields=id_passage_faune,uuid_passage_faune,nom_usuel_passage_faune,label_infrastructures,label_communes,scope&flat_keys=true&no_info=true&as_geojson=true"
   activate = true
   style = { color = "red"}
```
- Revoir des nomenclatures - Relancer l'installation du module (cf ci-dessus)
- Plus tard : étudier le changement de projection de la BDD...
