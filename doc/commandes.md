# Commandes

Le module présente un ensemble d\'action à effectuer en ligne de
commandes

## Documentation

### Description champs import

```
geonature modulator doc m_sipaf.pf import  > contrib/m_sipaf/doc/import_passage_faune_description_champs.md
```
## Gestion des modules


### Installation

TODO

### Suppression

TODO

## Visualisation de la configuration

### Grammaire

Cette commande permet de visualiser dans leur ensemble les éléments de texte qui seront affiché pour les titre, les tooltips de
boutons, etc... et de détecter plus facilement si une erreur s'est glissée dans la configuration (ou bien dans le traitement de la
grammaire).

```
geonature modulator grammar
```

Des options sont displonibles pour n'afficher qu'un ensemble restreint de ces éléments :

-   `-s`: `schema_code` pour un schéma donné
-   `-m`: `module_code` pour un module donné
-   `-o`: `object_code` pour un object donné (l'option `module_code` doit être choisie)
-   `-g`: `grammar_type` pour ne voir qu\'un type donné, à choisir parmi `label`, `labels`, `le_label`, `les_labels`, `un_label`, `des_labels`, 
    `un_nouveau_label`, `du_nouveau_label`, `d_un_nouveau_label`, `des_nouveaux_labels`, `du_label`.

Par exemple, la commande `geonature modulator grammar -m m_monitoring` va afficher la sortie suivante :

```
...
- des_labels
   - des categories des sites
   - des groupes de sites
   - des modules
   - des observations
   - des sites
   - des visites

- un_nouveau_label
   - une nouvelle categorie des sites
   - un nouveau groupe de sites
   - un nouveau module
   - une nouvelle observation
   - un nouveau site
   - une nouvelle visite
...
```
