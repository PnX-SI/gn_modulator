# Aide au développement


## Backend

- debug des configurations contenues dans les fichiers yml.

Les fichiers de configuration `yml` des modules sont analysés et traités à chaque démarrage de l'application flask.
En cas d'erreurs, ces dernières sont affichées dans les logs et le module `MODULATOR` n'est pas chargé.

En phase de développement, il est pratique d'avoir l'application flask qui redémarre automatiquement en cas de changement des fichiers de
configuration (yml). Pour cela vous pouvez lancer l'application avec les commandes suivantes :

```bash
source <GEONATURE_DIR>/backend/venv/bin/activate
extra_files=
export FLASK_APP=geonature.app; export FLASK_DEBUG=1;
geonature run --port 8000 --host 0.0.0.0 --extra-files="$(find -L /home/joel/info/sipaf/app//GeoNature/backend/media/modulator/config -type f -name \*.yml -o -name \*.json | sed -n '1{h};1!{H};${g;s/\n/:/pg}')
```

Avec cette commande de lancement de l'application, pour voir les effets des changements de la configuration au niveau du frontend, il suffit de  recharger la page du navigateur (`CTRL + MAJ + R` ou `MAJ + F5`).


Dans le cas d'un ajout de fichier `yml` il faudra relancer cette commande pour prendre en compte ce niveau fichier.

Les erreurs indiquent la ligne du fichier qui pose problème ainsi que l'erreur associée.

Par exemple:

- une erreur dans le yml du fichier:

```
  - ERR_LOAD_YML Erreur dans le fichier yaml: while scanning a simple key
could not find expected ':'
  in "...../m_sipaf/m_sipaf.module.yml", line 15, column 1
```

- cas où l'on référence un fichier de donnée qui n'a pas été trouvé

```

- ...../m_sipaf/m_sipaf.module.yml

  - ERR_GLOBAL_CHECK_MISSING_FEATURES Le ou les features (données) suivantes ne sont pas présentes dans les définitions : 'bd_topo.typeppopop'

```

- une erreur dans les fonction dynamique `js` (on ne peut pas forcement tester la fonction en condition réelle )à ce statde, mais on peut faire remonter des erreurs sur le code js):

```
- ...../m_sipaf/m_sipaf.module.yml

  - ERR_LOCAL_CHECK_DYNAMIC [config_params.site_filters_fields.items.1.items.0.items.0.test] : Uncaught ReferenceError: varErrorFatal is not defined at undefined:5:13
    __f__varErrorFatal
```



## Frontend

### Paramètre `debug`

L'ajout du paramètre de route `?debug` à l'url courante permet d'afficher certaines informations sur les différents composants de la page.

![Image frontend en mode debug](./images/debug_full_page.png)

Pour chaque élément on peut voir des informations sur le type de composant et accéder à plus en survolant avec la souris les lettres en vert.

- `d` (pour `data`): les données liées à ce composant (pour un formulaire il s'agit des données globale)
- `ed`(pour `element data`): les données liée à ce composant (pour un élement de formulaire (par ex un input), cela correspond à la valeur de cet élément)
- `l` (comme `layout`): le layout associé à cet élément (options, pour l'affichage, etc..) peut contenir des variables dynamiques (qui commencent par `__f__`)
- `cl` (commme `computed layout`): associé au layout, contient les valeur calculées (lorsqu'il y en a)
-  `cx` (comme `context`): contient des valeur qui peuvent provenir soit du `layout`, soit du `layout` des éléments parents, soit de valeurs globales définies dans la page courant ou le module. Par exemple+
    - le code du module en cours ou le code de l'object.
    - l'id du formulaire en cours
    - etc..

### Bac à sable

Sur la page `/#/modulator/test_layout`, il y a la possibilité de créer, éditer et tester les differents  layout.

![Image bac à sable layout](./images/bac_a_sable_layout.png)
