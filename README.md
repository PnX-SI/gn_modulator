# Modulator - Module de modules

## Présentation

Ce module donne accès à des outils qui permettent de créer des sous-module geonature.


Les modules sont listés sur la page d'accueil du module `modulator`.

Un exemple de sous-module est le module `m_sipaf` pour les passage à faune:

- page d'accueil du module `m_sipaf` avec une carte, liste et filtres les objets du sous-module :

![image](https://user-images.githubusercontent.com/4418840/217202599-44988f09-2651-49b4-966a-623d7abdcab9.png)

- fiche détail et de saisie de chaque objet :

![image](https://user-images.githubusercontent.com/4418840/217202865-45eb1a87-6826-4108-a8d5-6fa1a1392810.png)

## Installation

Compatible avec la version 2.13.0 (et plus) de GeoNature.

- Téléchargez le module dans ``/home/<myuser>/``, en remplacant ``X.Y.Z`` par la version souhaitée

```bash
cd
wget https://github.com/PnX-SI/gn_modulator/archive/X.Y.Z.zip
unzip X.Y.Z.zip
rm X.Y.Z.zip
```

- Renommez le répertoire du module

```bash
mv ~/gn_modulator-X.Y.Z ~/gn_modulator
```

- Lancez l'installation du module

```bash
source ~/geonature/backend/venv/bin/activate
geonature install-gn-module ~/gn_modulator MODULATOR
sudo systemctl restart geonature
sudo systemctl restart geonature-worker
deactivate
```

### Installation de sous-modules

La commande suivante permet d'installer un sous-module :

```bash
geonature modulator install -p <chemin_du_module>
sudo systemctl restart geonature
```

Cette commande : 
- installe le module python
- le module dans la base de données
- fait les migrations
- copie le dossier de configuration du sous-module dans le dossier `/backend/media/modulator/config` de GeoNature

Pour mettre à jour un sous-module, il faut relancer sa commande d'installation.

Le formalisme pour les codes des sous-modules est le suivante :   
- en minuscule
- prefixé par `m_`
- par exemple `m_sipaf`

Des sous-modules sont déjà présents dans le dossier
`/config/modules/contrib` :

- Le module SIPAF (passages à faune) :   
   - `geonature modulator install -p ./contrib/m_sipaf`

par exemple pour le module `m_sipaf`

```bash
geonature modulator install -p <chemin vers gn_modulator>/contrib/m_sipaf
```

### Mise à jour

#### Modulator

-   Téléchargez la nouvelle version du module

    ```
    wget https://github.com/PnX-SI/gn_modulator/archive/X.Y.Z.zip
    unzip X.Y.Z.zip
    rm X.Y.Z.zip
    ```

-   Renommez l'ancien et le nouveau répertoire

    ```
    mv ~/gn_modulator ~/gn_modulator_old
    mv ~/gn_modulator-X.Y.Z ~/gn_modulator
    ```

-   Si vous avez encore votre configuration du module dans le dossier `config` du module, copiez le vers le dossier de configuration centralisée de GeoNature :

    ```
    cp ~/gn_modulator_old/config/conf_gn_module.toml  ~/geonature/config/import_config.toml
    ```

-   Lancez la mise à jour du module

    ```
    source ~/geonature/backend/venv/bin/activate
    geonature install-gn-module ~/gn_modulator MODULATOR
    sudo systemctl restart geonature
    ```

#### Sous-module

Relancer la commande d'installation du module

```
geonature modulator install -p <chemin vers le sous-module> <CODE_DU_SOUS_MODULE>
```

## Développement

## Création d'un sous-module

[Documentation sur la création de sous module](./doc/creation_module.md)
