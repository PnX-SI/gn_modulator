# Création d'un module

## Aide au développement


(Voir la page aide au développement.)[./aide_developpement.md]


## Configuration d'un sous-module

Pour ce qui va suivre nous nous baserons sur le module de passage à faune (m_sipaf)[../contrib/m_sipaf]

### Structure


#### Module simple

Si le module n'a pas besoin de définir des modèles et des migrations, son dossier peut se limiter aux dossier config. Voir le prochain paragraphe.

#### Cas d'un module python

La structure du dossier de la configuration du module est la suivante :

```
/
   - VERSION
   - README.md
   - setup.py

   # partie module python
   - backend/
      - m_sipaf
         - blueprint.py
         - config_schema_toml.py
         - models.py
         - migrations/
            - data/
               ...<fichiers sql pour les migrations>
            - version/
               fichier python pour les migrations

   # config
  asset - config/
      # definition du module
      - m_sipaf.module.yml
      - assets
         - module.jpg

      # schemas associés au modèles du module
      - definitions/
        - m_sipaf.pf.schema.yml
        - ...

      # fichier de données (nomenclature etc...)
      - features/
         m_sipaf.utils.data.yml (nomenclatures, etc..)
         bd_topo.type.data.yml (type de données pour ref_geo lineaire)

      # fichier pour les pages du frontend...
      - layouts/
         - m_sipaf.site_list.yml

   ######################################################
   optionel

   # pour documenter des traitement de données annexes
   # par exemple bd_topo, données sinp etc....
   - data/

   # documentation
   doc/

```

#### Fichier de configuration du module`m_sipaf.module.yml`

Dictionnaire définissant la configuration du module, avec les clés suivantes :

- `module` :
   - informations destinées à la table `gn_commons.t_modules`

```
module:
  module_label: Passages faune
  module_desc: Module permettant la visualisation et la gestion des passages à Faune de France
  module_picto: fa-road
  active_frontend: true

```

-  `objects` :
   - permet de définir les données qui vont être manipulées dans ce module :
      - pour chaque clé on va définir :
         - **schema_code** : défini la table
         - **cruved** : quelles sont les api qui vont être ouvertes et pour quels type d'action
         - **prefilters** :
            - l'API créée pour cet object (et ce module) appliquera toujours les pré-filtres definis ici
         - **label** : redéfinition du nom de l'objet
         - **labels** : redéfinition du nom (pluriel de l'objet
         - **genre** : `'M'|'F'` redéfinition du genre de l'objet (masculin / féminin)
         - **map** :
            - **style** : style css des layers :
               - **color**
            - **bring_to_front** : *boolean*, si l'on souhaite ramener ces éléments au premier plan

- `tree` : un dictionnaire qui définit une hiérachie entre les pages, classiquement :
```
   site
      diagnostic
```
- `pages_definition` : la définition des pages qui composent le module_label
```
   site:
      list:
         root: true
      create:
         layout: # redefinition du layout pour la page de création
            code: m_sipaf.site_edit
      edit:
      details:

   diagnostic:
      details:
      edit:
      create:
         layout:
            code: m_sipaf.diagnostic_edit
```

Ce dictionnaire va définir les paramètre des pages.
Pour chaque object on defini differentes actions (list, create, edit, details), et cela va créer une page par actions avec une url et un layout associé.

Par exemple on va avoir pour :
- liste de  site:
- avec la clé `root: true` cela signifie que l'on est à la racine du module
 - `url` : `/#/modulator/m_sipaf`:
 - `layout` : `code: m_sipaf.site_list`:
- détails d'un site:
  - `url` : `/#/modulator/m_sipaf/site_details/<value>`:
  - `layout`:  `code: m_sipaf.site_details`
- édition d'un site:
  - `url` : `/#/modulator/m_sipaf/site_edit/<value>`:
  - `layout`:  `code: m_sipaf.site_edit`
- création d'un site: d
  - dans ce cas, on redéfini le layout pour reprendre celui de la page d'édition
  - `url` : `/#/modulator/m_sipaf/site_create`:
  - `layout`:  `code: m_sipaf.site_edit`

- `features`:

Liste des (code de) fichiers de données associées au module.

```
features:
  - m_sipaf.utils
  - m_sipaf.permissions
  - bd_topo.type

```

- `config_params`:
Paramètre prédefinis et pouvant être réutilisé dans les layout du module.
- Ici définis dans un fichier à paert pour alléger le fichier `m_sipaf.module.yml`

```
config_params: !include ./config.yml
```

- par exemple:
```
site_details_fields:
  display: tabs
  overflow: true
  items:
    - label: Propriétés
  ....100+ lignes
```

Ce champs est réutilisé ici dans le fichier [m_sipaf.site_edit.layout.yml](../contrib/m_sipaf/config/layouts/m_sipaf.site_edit.layout.yml) avec le champs `__SITE_FORM_FIELD__` qui prendra la valeur de `site_details_fields`.

```
layout:
  height_auto: true
  items:
    code: utils.object_form_map
    template_params:
      object_code: site
      layout: __SITE_FORM_FIELDS__
      zoom: "__f__o.value(x) ? 12 : null"
      skip_ref_layers: __SKIP_REF_LAYERS__
      keep_zoom_center: __f__!o.value(x)
      geojsons:
        - code: m_sipaf.geojson_pkpr
```