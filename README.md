# Modulator - Module de modules

## Présentation

Ce module GeoNature est un générateur de modules, qui permet construire dynamiquement des sous-modules disposant de leur propre modèle de données, 
à partir de fichiers de configuration YAML.

Chaque sous-module dispose d'une page d'accueil avec une carte, liste et filtres des objets du sous-module :

![image](https://user-images.githubusercontent.com/4418840/217202599-44988f09-2651-49b4-966a-623d7abdcab9.png)

Et une fiche détail et de saisie de chaque objet :

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
deactivate
```

- [Liste des commandes du module](./doc/commandes.md)

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
- par exemple `m_sipaf`, `m_monitoring`, `m_protocol_test`

Des sous-modules sont déjà présents dans le dossier
`/config/modules/contrib` :

- Le module SIPAF (passages à faune) :   
   - `geonature modulator install -p ./contrib/m_sipaf`

- Le module gestionnaire de sites :   
   - `geonature modulator install -p ./contrib/m_monitoring`
   - Définit les tables suivantes :
      - site
      - groupe de sites
      - visite
      - observation
   - Les API (liste, get, post, patch, delete) associées
   - Les pages associées au module suivent la hiérarchie:
      - site -> visite -> observation
   - Des données d'exemples peuvent être ajoutées avec la commande
     `geonature modulator features m_monitoring.exemples`

- Un protocole de test pour le module Monitoring : 
   - Il faut avoir installé au préalable le sous-module
     `m_monitoring`
   - Puis installer le protocole de test : 
     `geonature modulator install -p ./contrib/m_protocol_test` : 
      - module (protocole) -> site -> visite -> observation
   - Des données d'exemple peuvent être ajoutées avec la commande
     `geonature modulator features m_monitoring.exemples`

## Développement

## Création d'un sous-module

La méthode pour créer un sous-module est exposée
[ici](./doc/creation_module.md)
