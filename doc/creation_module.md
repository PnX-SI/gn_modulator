# Création d'un module

## Aide au développement

### Backend

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



### Frontend

L'ajout du paramètre de route `?debug` à l'url courante permet d'afficher certaines informations sur les différents composants de la page.






Nous prenons comme exemple un projet de suivi de parcs éoliens.

## Configuration du module

La structure du dossier de la configuration du module est la suivante :

```
/
    # fichier de configuration du module
    module.yml

    # fichiers de définition des objects (tables, modèles) associés à ce module
    definitions/

    # données additionnelles
    features/

    # fichiers images, médias, etc..
    assets/

    # fichiers contenant la configuration des pages du modules
    layouts/
```

### `module.yml`

Dictionnaire définissant la configuration du module, avec les clés suivantes :

- **module** :
   - informations destinées à la table `gn_commons.t_modules`

     ```
     module :
        module_code : m_eole
        module_label : Modules de suivi éolien
        module_desc : POC pour le projet suivi éolien
        module_picto : fa-puzzle-piece
        active_frontend : true
     ```

- **objects** :
   - permet de définir les données qui vont être manipulées dans ce module :   
      - pour chaque clé on va définir :   
         - **schema_code** : défini la table
         - **cruved** : quelles sont les api qui vont être ouvertes et pour quels type d'action
         - **prefilters** :
            - par exemple pour les gîtes on souhaite avoir seulement les sites de catégorie `gîtes`
            - `prefilters : category.code = GIT`
            - l'API créée pour cet object (et ce module) appliquera toujours les pré-filtres definis ici
         - **label** : redéfinition du nom de l'objet
         - **labels** : redéfinition du nom (pluriel de l'objet
         - **genre** : `'M'|'F'` redéfinition du genre de l'objet (masculin / féminin)
         - **map** : 
            - **style** : style css des layers :
               - **color**
            - **bring_to_front** : *boolean*, si l'on souhaite ramener ces éléments au premier plan
         - **exports** : liste des noms d'export (`export_code`) associés à l'objet

- **tree** : un dictionnaire qui définit une hiérachie entre les pages, classiquement :
   - site
      -visite
         - observation

- **pages** : la définition des pages qui composent le module_label
   - pages
      - parc_list
         - url : '' 
         - layout : 
            - code : m_eole.parc_list

- **exports** :
   - m_sipaf.pf : # code de l'export ou `export_code`
      - export_label : Test
      - object_code : pf
      - fields : 
         - id_passage_faune 
         - ...
