# Layout

Les fichiers de `layout` permettent de définit les éléments du `frontend` d'un module.

Un fichier de layout `layout_test.layout.yml` doit contenir par les clé suivantes.

```
type: layout
code: layout_test
title: layout test
description: description du layout de test

layout: (dictionnaire conteant les éléments de ce layout)
```

## array

- `items`: le layout qui sera utilisé pour une ligne de la liste
- `direction`:
  - si égal à `row`, les éléments de la liste seront disposés en rang.
- `add_title`: (`Ajouter un élément`)
  - texte du tooltip au survol du boutton `+` pour ajouter un élément

## Sections

Un section est composée et regroupe plusieurs items, cela peut être un simple `<div>`, ou un ensemble d'onglets. Ces éléments peuvent

### Options

- `title` _string_ : titre de la section
- `type` _string_:
  - `form`, pour faire de cet élément un formulaire
- `display` _string_! type d'affichage
- `tabs`: onglets
- `fieldset`: coutour + titre dans le contour
- `height_auto`: si `true`, la hauteur cu composant est adaptée à la taille de la page.
  - souvent pour l'élément le plus à la racine de la page
- `overflow` _bool_ : permet de mettre le contenu d'un élément dans un overflow et de déterminer automatiquement sa taille (par exemple formulaire long entre son titre et les boutons de validtation)
- `items` _array, dict_ : élement(s) contenus dans la section
- `direction` _string_:
  - `'row`, les éléments sont disposés horizontalement (verticalement par défault)

## Élémenents de formulaire

Doit avoir un parent qui est une section de type `form`

### Input

- `key`: clé de la donnée associée à cet input.
- `title`: titre du formulaire (valeur de`key` si `title non défini`)
- `required`: le champs est requis
- `placehloder`: texte d'aide dans le composant
- `hint`: texte d'aide en dessous du composant
- `description`: ajout un icône point d'interrogation avec un tooltip contenant le texte de la description
- `type`:
  - `string`: champs texte
  - `number`: nombre flottant
  - `integer`: nombre entier
  - `uuid`: UUID
  - `textarea`: champs texte long
  - `boolean`, `checkbox`: checkbox pour les booléens
- `min`: valeur minimale (`number`, `integer`, `date`)
- `max`: valeur minimale (`number`, `integer`, `date`)
- `hidden`: si `true`, l'élément est caché
- `disabled`: si `true`, l'élément est désactivé

### Select ou `list_form`

- `type` : `list_form`
- `title` : titre du formulaire (valeur de`key` si `title non défini`)
- `required` : le champs est requis
- `placehloder` : texte d'aide dans le composant
- `hint` : texte d'aide en dessous du composant
- `description` : ajout un icône point d'interrogation avec un tooltip contenant le texte de la description
- `return object` :
  - `true` : renvoie l'object entier
  - `false` (_default_): renvoie la valeur de la clé `<value_field_name>`
- `multiple` : selecteur multiple
- `value_field_name` : champs pour la valeur
- `label_field_name` : champs pour l'affichage dans la liste
- `display_field_name` : champs pour le tooltip qui s'affiche au survol de la liste
- `reload_on_search` :
  - `true` : refait une requête en cas de changement dans la recherche
  - `false` : (_default_): toutes les données sont chargées en une seule fois, le filtrage se fait en local
- `items`: liste dans laquelle on choisi.
- `api`: route qui va donner les valeurs de la liste
- `params`: dictionnaire qui contient les paramètres de route `{key1:1 key2: 2}` `=>` `?key1=1&key2=2`
- `items_path`: clé qui permet d'accédeer aux donnée si la route ne renvoie pas une liste mais un dictionnaire
  - `sort`: variable sur laquelle on effectue le tri

#### paramètre d'object

- `module_code` : module_associé au select
- `object_code` : object de module associé au select

Ces paramètre de récupérer automatiquement les valeurs par défaut pour les champs:

- `value_field_name`
- `label_field_name`
- `title_field_name`
- `sort`
- `api`
- ...?

### Listes et dictionnaires

A peu près similaire à `section` mais on précise l'object `key`

- `items`: contient le layout qui sera appliqué à tous les éléments de la liste. Les variable `key` contenues dans ce layout sont relative à la variable `key`.

- `add_title`: (liste seulement) texte du tooltip affiché au survol du bouton d'ajout d'un élément.

Par exemple

```
type: form
items:
    - key: l
      type: array
      items:
        - type: number
          key: n1
        - type: string
          key: s2
    - key: d
      type: dict
      items:
        - type: number
          key: n3
        - type: string
          key: s4

```

- les clés `n1` et `s1` correspondront en absolu au clés `l.n1` et `l.s2`
- les clés `n3` et `s4` correspondront en absolu au clés `l.n3` et `l.s4`

## code ou template

On peut réutiliser un `layout` déjà existant dans un layout, il suffit d'ajout l'élément

```
 code : layout_code
```

Si ce layout contient des paramètres, c'est à dire des chaînes de caractère du genre `__PARAM_1__`, `__PARAM_2__` (commençant et terminant par deux _soulignés_ `__`) on peut (ou bien on doit s'ils n'ont pas de valeur par défaut) comme ceci

```
 code : layout_test_template
 params:
    param_1: un
    param_2: deux
```

Le fichier de template peux être comme ci dessous, avec dans ce cas l'obligation de définir param_2 lors de son utilisation.

```
type: layout
code: layout_test_template
title: layout test template
description: description du layout de test de template

layout:
   type: list_form
   items:
       - 1
       - 2
       - 3
   title: __PARAM_1__
   description: __PARAM_2__
defaults:
   param_1: titre du select
```


## Message

- `type`: `message`
  - permet d'affichier un message dans un cadre
  - `class`
    - `info`: bleu
    - `error`: rouge
    - `warning`: orange
 - `json`: un dictionnaire qui sera affiché dans le composant
 - `html`: du html qui sera affiché dans le composant

## Bouttons

- `type`: `button`
- `action`: `submit`,`delete`, `close`, `edit`, `details`
- `disabled`
- `icon`: icône de fa-icon


## Modales

Par exemple dans les formulaires, on souhaite ajouter une modale pour confirmer la suppression d'un élément.

- Boutton pour ouvrir la modale: 

```
    - flex: "0"
      type: button
      color: warn
      title: Supprimer
      icon: delete
      description: __f__o.label_delete(x)
      hidden: __f__!o.is_action_allowed(x, 'D')
      action:
        type: modal
        modal_name: delete
```

- Code de la modale

```
  type: modal
  modal_name: delete
  title: __f__`Confirmer la suppression ${o.du_label(x)} ${o.data_label(x)}`
  direction: row
  items:
    - type: button
      title: Annuler
      action: close
      icon: refresh
      color: primary
    - type: button
      title: Suppression
      action: delete
      icon: delete
      color: warn

```

## Objects (de module)

- `type`: `object`
  - permet d'afficher des composant de base pour un schema
- `object_code`: le nom du Schéma
- `module_code`: le nom du Schéma
- `display`: type de composant parmi
  - `geojson`: affiche sous forme de geojson (doit être dans un composant carte)
  - `table`: affiche les resultats obtenus dans un tableau
  - `filters`: choix des filtres pour un objet
  - `null`: pour un élément (`value`) => le layout défini par `items` est affiché, avec la valeur de l'object récupéré (par exemple pour les pages de détails ou d'édition)
- `value`: valeur d'un object à mettre en focus
- `filters`: filtre sur la liste d'un objet
- `prefilters`: pré-filtres sur la liste d'un object

### Options spécifiques pour chaque display

#### `geojson`
Affiche le ou les lignes sous forme de geojson (doit être dans un composant carte)

- `open_popup`: ouvre le popup dès que l'object est chargé
- `style`: style appliqué aux layers
- `zoom`: on zoome sur les layers dès qu'ils sont chargés
- `tooltip_permanent`: tooltip affiché (sinon juste au survol)
- `bring_to_front`: ramène les layers sur le devant de la scène.
- `key`: pour afficher un élement de géométrie du dictionnaire `data`, (où pour l'éditer dans le cadre d'un formulaire)
- `deflate`: pour afficher les polygone et ligne sous forme de point (cercles) lorsque le zoom est trop faible pour les voir correctement
- `activate`: si `false`: desactivé par défaut dans la liste des contrôles
- `title` :  titre utilisé par les contrôles
- `popup_fields`: champs utilisés pour renseigner le popup lors du click sur un élément

#### `table`

- `page_size`: nombre de ligne du tableau (s'adapte à la taille du tableau (TODO rendre optionnel ????))
- `items`: ensemble des champs qui seront utilisée dans le tableau
  - peut être une chaine de caractères `<key>`
  - un dictionnaire:
```
    key: <key>
    hidden: true
    type: <type> # string, date, etc... 
```
- `sort`: variable utilisée pour le tri
- `display_filters`:  affiche les filtres (TODO à retravailler)
- `actions`: dictionnaire pour redéfinir une actions
  - par exemple pour rediriger vers la fiche de la synthèse
```
actions:
    R:
        url: "#/synthese/occurrence/<id>"
        title: Liens vers le module de synthese
```
- ``

#### `filters`

- `items`: champs pour le formulaire des filtres
```
- uuid_passage_faune
- key: id_nomenclature_ouvrage_specificite
  multiple: true
  type: list_form

```

- `filter_defs`: dictionnaire de définition pour les filtres
```
# filtre de type LIKE (~) avec la valeur de uuid_passage_faune
  uuid_passage_faune:
    type: "~"

# pour créer un filtre du type area.id_area in [id_1, id_2, id_3]
  regions:
    field: areas.id_area
    key: id_area ## valeurs à récupérer depuis la liste de dict { id_area: 1, area_code: 27, ...}

```
## composant d'import




## Valeurs dynamiques

Les paramètres peuvent être définis dynamiquement et dépendre des valeurs des données, des layout et du contexte.

Quasiment tous les paramètre peuvent être dynamiques, il est cependant déconseillé de le faire avec les paramètres `key` et `type`.

La chaîne de caractère doit commencer par `__f__` pour être interprétée comme une fonction

Le language est le javascript

Pour renvoyer un valeur qui depend de la clé `truc` de `data` ou peut utiliser les notations suivantes:

```

    // notation complète
    '__f__{ return data.truc }'

    // sans les accolades
    '__f__return data.truc'

    // sans le return
    '__f__data.truc'

    // l'espace devant ne joue pas
    '__f__ data.truc'

    // chaîne de caractère avec `
    '__f__`Truc : ${data.truc}` '

    // pour faire du debug
    '__f__{ console.log(data); return data.truc }'
```

Les variables disponibles sont:

```
    data: {},        // dictionaire correspondant à l'élément en cours
    layout: {},      // le layout de l'élément
    globalData: {},  //les données globales
    formGroup: {},   //  à utiliser seulement pour `change`
                     //  - pour pouvoir modifier la valeur des champs de façon programmée

    u: {             // fonctions utiles
        today: () => {},
        departementsForRegion: () => {},
        YML: {},
        get_cd_nomenclature: () => {}

    },
    o: {             // fonctions sur les objects et le contexte
        prefilters: () => {},
        filters: () => {},
        config: () => {},
        value: () => {},
        schema_code: () => {},
        label: () => {},
        labels: () => {},
        du_label: () => {},
        des_labels: () => {},
        data_label: () => {},
        tab_label: () => {},
        title_details: () => {},
        title_create_edit: () => {},
        label_edit: () => {},
        label_create: () => {},
        label_delete: () => {},
        is_action_allowed: () => {},
        has_permission: () => {},
        geometry_type: () => {},
        geometry_field_name: () => {},
        object: () => {},
        url_export: () => {}
    },
    context: {}, // contexte
```

