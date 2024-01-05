# Installation du sous-module SIPAF

Préalable :

- récupérer les données routes et passages faune et placer les fichiers dans le dossier `<data_dir_path>`

```
source <GeoNature>/backend/venv/bin/activate

# Installation du module Modulator
geonature install-gn-module ~/gn_modulator MODULATOR

# Installation du sous-module SIPAF
geonature modulator install -p ./contrib/m_sipaf

# Import du ref_geo linéaire des routes
geonature modulator import -i ref_geo.route -d  <data_dir_path>

# Import des données des passages à faune (v5 pour l'exemple)
geonature modulator import -i m_sipaf.pf_V1 -d  <data_dir_path>
```
