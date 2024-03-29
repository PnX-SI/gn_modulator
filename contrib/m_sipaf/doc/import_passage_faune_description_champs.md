

# Import des passages à faune



### Champs

##### uuid_passage_faune
 - *champ d'unicité*
  - *type* : `uuid`
  - *définition* : Identifiant universel unique au format UUID (uuid_pf). Généré automatiquement si non renseigné.
  - champ autogénéré pour les lignes où il est de valeur nulle
##### geom
 - *obligatoire*
  - *type* : `geometry`
  - *geometry_type* : `geometry`
  - *format* (exemples à adapter au `SRID`=`4326`):
    - WKT (par ex. `POINT(0.1 45.2)`
    - XY (remplacer `geom` par les colonnes `x` et `y`)
  - *définition* : Géometrie du passage à faune (SRID=4326)
##### code_ouvrage_gestionnaire
  - *type* : `string`
  - *définition* : Code de l’ouvrage (pour le gestionnaire)
##### commentaires
  - *type* : `string`
  - *définition* : Commentaires sur le passage à faune
##### date_creation_ouvrage
  - *type* : `date`
  - *format* : `YYYY-MM-DD` (par ex. `2023-03-31`)
  - *définition* : Date de la réalisation de l'ouvrage
##### date_requalification_ouvrage
  - *type* : `date`
  - *format* : `YYYY-MM-DD` (par ex. `2023-03-31`)
  - *définition* : Date de la requalification de l'ouvrage
##### diametre
  - *type* : `number`
  - *définition* : Diamètre de la buse en mètre
##### hauteur_dispo_faune
  - *type* : `number`
  - *définition* : Hauteur de l'ouvrage effectivement disponible pour la faune en mètre
##### hauteur_ouvrage
  - *type* : `number`
  - *définition* : Hauteur de l'ouvrage en mètre
##### issu_requalification
  - *type* : `boolean`
  - *format* : `true`,`t`,`false`,`f`
  - *définition* : L'ouvrage est issu d'une opération de requalification ?
##### largeur_dispo_faune
  - *type* : `number`
  - *définition* : Largeur de l'ouvrage effectivement disponible pour la faune en mètre
##### largeur_ouvrage
  - *type* : `number`
  - *définition* : Largeur de l'ouvrage en mètre
##### longueur_franchissement
  - *type* : `number`
  - *définition* : Longueur de franchissement de l'ouvrage en mètres (ne prend pas en compte l'épaisseur des matériaux et éventuels obstacles)
##### nom_usuel_passage_faune
  - *type* : `string`
  - *définition* : Nom usuel utilisé pour dénommer l'ouvrage (nom_usuel_pf)
##### ouvrag_hydrau_tirant_air
  - *type* : `number`
  - *définition* :  Tirant d'air existant entre la banquette et le plafond de l'ouvrage, en mètre
##### ouvrage_hydrau
  - *type* : `boolean`
  - *format* : `true`,`t`,`false`,`f`
  - *définition* : Ouvrage hydraulique ou non
##### ouvrage_type_autre
  - *type* : `string`
##### pi_ou_ps
  - *type* : `boolean`
  - *format* : `true`,`t`,`false`,`f`
  - *définition* : Positionnement du passage vis-à vis de l’infrastructure (inférieur (False) ou supérieur (True))
##### pk
  - *type* : `number`
  - *définition* : Point kilométrique
##### pr
  - *type* : `number`
  - *définition* : Point repère
##### pr_abs
  - *type* : `integer`
  - *définition* : Distance en abscisse curviligne depuis le dernier PR
##### source
  - *type* : `string`
  - *définition* : Source de la donnée
##### id_nomenclature_ouvrage_hydrau_banq_caract
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Caractérisation de la banquette dans le cas d'un ouvrage hydraulique (ouvrage_hydrau_caract_banquette)
  - *valeurs* :
    - **SIM** *Simple*
    - **DOU** *Double*
##### id_nomenclature_ouvrage_hydrau_banq_type
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Type de la banquette dans le cas d'un ouvrage hydraulique (ouvrage_hydrau_type_banquette)
  - *valeurs* :
    - **NAT** *Banquette naturelle*
    - **ECB** *Encorbellement*
    - **AUT** *Autre*
    - **BET** *Banquette béton*
    - **POF** *Ponton flottant*
##### id_nomenclature_ouvrage_hydrau_position
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Ouvrage hydraulique Position (ouvrage_hydrau_position)
  - *valeurs* :
    - **RG** *Rive Gauche*
    - **RD** *Rive Droite*
    - **RGD** *Rive gauche et rive droite*
##### id_nomenclature_ouvrage_specificite
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Exclusivité pour le passage faune (specificite)
  - *valeurs* :
    - **SPE** *Spécifique*
    - **ND** *Non dédié*
    - **MIX** *Mixte*
##### nomenclatures_ouvrage_categorie
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Catégorie d'ouvrage d'art (utilisation)
  - *valeurs* :
    - **VIA** *Viaduc*
    - **PF** *Petite faune*
    - **SPE_CHI** *Ouvrage spécifique: chiroptéroduc*
    - **SPE_CANOP** *Ouvrage spécifique: passage canopée*
    - **TF** *Toute faune*
    - **GF** *Grande faune*
    - **SPE_BAT** *Ouvrage spécifique: batracoduc*
##### nomenclatures_ouvrage_materiaux
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Matériaux composants l'ouvrage d'art (lb_materiaux)
  - *valeurs* :
    - **BET** *Béton*
    - **PLT** *Plastique*
    - **MAC** *Maçonnerie*
    - **IND** *Indéterminé*
    - **MET** *Métal*
    - **BOI** *Bois*
    - **AUT** *Autre*
##### nomenclatures_ouvrage_type
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Type d'ouvrage d'art (lb_type_ouvrage)
  - *valeurs* :
    - **CAD** *Cadre*
    - **AUT** *Autre (préciser)*
    - **VOU** *Voûte sans radier*
    - **DAL** *Dalle*
    - **VIA** *Viaduc*
    - **CAN** *Canalisation*
    - **DIAB** *Diabolo*
    - **TUN** *Tunnel*
    - **BUS** *Buse*
    - **VOU+R** *Voûte avec radier*
    - **POR** *Portique*
    - **DAL+P** *Dalle et palpaplanche*
    - **ARC** *Arc*
    - **PON** *Pont*
    - **DALO** *Dalot*
    - **TRA** *Tranchée*


## Relations



### Acteurs

##### actors.id_nomenclature_type_actor
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *valeurs* :
    - **CON** *Concessionnaire*
    - **GES** *Gestionnaire*
    - **DEP** *Département*
    - **PRO** *Propriétaire*
    - **INT** *Intervenant*
    - **ETA** *État*
##### actors.id_organism
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `organismes`
  - *champ(s)* : `nom_organisme`


### Usages

##### usages.id_nomenclature_usage_type
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *valeurs* :
    - **A** *Agricole*
    - **R** *Routier*
    - **D** *Défense*
    - **H** *Hydraulique*
    - **F** *Forestier*
    - **P** *Piétonnier*
##### usages.commentaire
  - *type* : `string`
##### usages.detail_usage
  - *type* : `string`

