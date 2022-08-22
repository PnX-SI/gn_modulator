======
Layout
======

Sections
========

- ``title`` *string*
    - Titre de la section
- ``type`` *string*
    - différent choix possible
        - ``form``: le contenu de cette section est un formulaire
        - ``fieldset``: entouré avec le titre dans la bordure
        - **TODO** ``tabs``: les items sont dans des tabs
        - **TODO** ``accordeon``: les items sont dans un accordéon
- ``items`` *liste*
    - les éléments de cette section
- ``direction``  *string*
    - si égal à `row`, les éléments seront disposés en rang.

- ``height_auto`` *boolean*
    - si égal à true : la hauteur du composant est adaptée à la hauteur de la page

Les clés
========

- ``key`` *string*
    - clé de l'élément, qui permet de récupérer sa valeur dans ``data``
- ``title`` *string*
    - ``Label de l'élément (si null on utilise ``key``)
- ``hint`` *string*
    - texte court s'affichant sous l'élément pour aider à la saisie
- ``description`` *string*

- ``type`` *string* ``array|object``
    - permet dde préciser si la données associée l'élément est un object (dictionnaire) ou une liste

- ``change`` *string*
    - description de la fonction qui s'applique lors du changement de la donnée associée à cette clé

- ``hidden`` *string*
    - si égal à ``true``, le composant n'est pas affiché


Les contraintes
---------------
- ``required``
    - pour indiquer que ce champs est obligatoire
- ``min``
    - pour les types ``number``, ``integer``, ``date``, ``datetime``
    - permet
- ``max``
    - cf ``min``


object
------
- ``items``:
    - le layout représentant l'object
- ``direction``: les éléments de l'object sont
    - si égal à ``row``, les éléments seront disposés en rang.

array
-----

- ``items``: le layout qui sera utilisé pour une ligne de la liste
- ``direction``:
    - si égal à ``row``, les éléments de la liste seront disposés en rang.
- ``add_title``: (`Ajouter un élément`)
    -  texte du tooltip au survol du boutton ``+`` pour ajouter un élément

Bouttons
========

- ``type``: ``button``
    - permet de positionner un boutton

- ``action``
- ``disabled``
- ``icon``

Message
=======

- ``type``: ``message``
    - permet d'affichier un message dans un cadre
    - ``class``
        - ``info``: bleu
        - ``error``: rouge
        - ``warning``: orange


Schéma
======

- ``type``: ``schema``
    - permet d'afficher des composant de base pour un schema
- ``schema_name``:  le nom du Schéma
- ``component``: type de composant parmi
    - ``map``
    - ``details``
    - ``form``
    - ``value``



Valeurs dynamiques
==================

Certain paramètre peuvent dépendre des données, on peut utiliser une chaîne de caractère qui sera interprétée comme un fonction, et appelée avec les entrée suivantes

- ``data``
    - le dictionnaire des données correspondant à l'élément en cours
- ``globalData``
    - les données globales
- ``formGroup``
    - à utiliser seulement pour ``change``
    - pour pouvoir modifier la valeur des champs de façon programmée

Les règles sont les suivantes:

- la chaîne de caractère doit commencer par ``__f__`` pour être interprétée comme une fonction

- le language est le javascript

- pour renvoyer un valeur qui depend de la clé ``truc`` de ``data`` ou peut utiliser les notations suivantes

::

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

- **TODO** pour les fonction plus conséquentes, il est possible de fournir un liste de chaîne de caractères
    - le premier élément de cette liste doit commencé par ``__f__``
    - il faut faire attention à bien mettre des `;` à la fin d'une instruction
    - par exemple

::

    [
      "__f__{",
      "let a = data.res1;",
      "let b = data.res2;",
      console.log("calcul en cours, a, b);",
      "return `a et b : ${a+b}`;",
      "}"
    ]

Choix de valeur dans une liste
==============================

Composant permettant de choisir une (ou plusieurs valeurs dans une liste), prédéfini

- ``type`` : ``list_form``

- `items`: liste de valeurs
    - valeurs `simples`
        - nombres, chaînes de caractères
    - dictionnaire:
        - qui contiennent des valeurs associées aux clés
            - ``value_field_name``, ``label_field_name``, (``title_field_name``, optionnel)

- ``value_field_name``
    - clé qui contient la valeur de l'item
    - par défault: ``value``
- ``value_field_name``
    - clé qui contient le label de l'item pour affichage dans la liste
    - par défault: ``label``
- ``title_field_name``
    - clé qui contient la description (qui va s'afficher au survol de l'item)
    - par défault: ``title``

Liste récupérée depuis une api
------------------------------

- ``api`` *string*:
    - route vers l'api qui va nous fournir les items
        - (si relative on rajoute l'adresse)

- ``cache`` *boolean* (`false`):
    - si on souhaite mettre le résultat de l'api en cache
    - pour les listes de taille raisonable et qui changent rarement

- ``items_path``
    - clé pour localiser les items dans le  retour de l'api
    - lorque le résultat de l'api est un dictionnaire et non une liste
    - par exemple pour la route des nomenclatures de GN
        - ``nomenclatures/nomenclature/STADE_VIE``
        - le retour est un dictionnaire la liste est donnée par la clé ``value``

- TODO ``params``

- TODO ``schema_name``