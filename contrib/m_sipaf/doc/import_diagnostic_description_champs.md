

# Import des diagnostics



### Champs

##### date_diagnostic
 - *champ d'unicité*, *obligatoire*
  - *type* : `date`
  - *format* : `YYYY-MM-DD` (par ex. `2023-03-31`)
  - *définition* : Date d'établissemnt du diagnostic de fonctionalité
##### id_passage_faune
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `passages à faune`
  - *champ(s)* : `uuid_passage_faune`
##### amenagement_biodiv_autre
  - *type* : `string`
##### amenagement_faire
  - *type* : `string`
  - *définition* : Détails aménagements ou autres mesures à réaliser pour rendre l'ouvrage plus fonctionel
##### commentaire_amenagement
  - *type* : `string`
  - *définition* : champs libre pour information complémentaire indicatives
##### commentaire_diagnostic
  - *type* : `string`
  - *définition* : champs libre pour information complémentaire indicatives
##### commentaire_perturbation_obstacle
  - *type* : `string`
  - *définition* : champs libre pour information complémentaire indicatives
##### commentaire_synthese
  - *type* : `string`
  - *définition* : champs libre pour information complémentaire indicatives
##### obstacle_autre
  - *type* : `string`
##### perturbation_autre
  - *type* : `string`
##### id_nomenclature_amenagement_entretient
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *valeurs* :
    - **BON** *Bonne*
    - **MOY** *Moyenne*
    - **OCC** *Occasionelle*
    - **NUL** *Nulle*
##### id_nomenclature_franchissabilite
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Estimation de la franchissabilité de l'ouvrage pour les animaux
  - *valeurs* :
    - **BON** *Bonne*
    - **MOY** *Moyenne*
    - **OCC** *Occasionelle*
    - **NUL** *Nulle*
##### id_nomenclature_interet_grande_faune
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Intérêt pour la grande_faune
  - *valeurs* :
    - **FAI** *Faible*
    - **MOY** *Moyen*
    - **FOR** *Fort*
##### id_nomenclature_interet_petite_faune
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Intérêt pour la petite_faune
  - *valeurs* :
    - **FAI** *Faible*
    - **MOY** *Moyen*
    - **FOR** *Fort*
##### id_nomenclature_ouvrage_hydrau_racc_banq
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : État du raccordement entre la banquette et la berge aux sorties d'un ouvrage mixte hydraulique
  - *valeurs* :
    - **BON** *Bon*
    - **INS** *Insuffisant*
    - **ABS** *Absent*
##### nomenclatures_diagnostic_amenagement_biodiv
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Types d'aménagement complémentaires en faveur de la faune
  - *valeurs* :
    - **PAR** *Parapet d'accultation*
    - **PLA** *Plantations*
    - **MUR** *Andains / muret*
    - **MAR** *Mares*
    - **AUT** *Autre (préciser)*
##### nomenclatures_diagnostic_obstacle
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Obstacles aux déplacement pouvant affecter la fonctionalité d'n ouvrage
  - *valeurs* :
    - **NEA** *Néant*
    - **CLOT** *Clôtures*
    - **TROT** *Trottoirs*
    - **GLIS** *Glissières*
    - **DENIV** *Dénivelé*
    - **DEP** *Dépôts*
    - **STAG** *Stagnation d'eau*
    - **INFR** *Infrastructure*
    - **AUT** *Autre (préciser)*
##### nomenclatures_diagnostic_ouvrage_hydrau_dim
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Dimensions de l'ouvrage hydraulique inadaptées
  - *valeurs* :
    - **LARG_INF** *Largeur trop faible*
    - **LARG_SUP** *Largeur trop élevée*
    - **HAUT_INF** *Hauteur insuffisante*
    - **DEF_PENTE** *Ne respecte pas la pente*
##### nomenclatures_diagnostic_ouvrage_hydrau_etat_berge
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : État des berges à l'entrée de l'ouvrage (ouvrage hydraulique)
  - *valeurs* :
    - **STA** *Stable*
    - **ERO** *Érodé*
    - **RIPC** *Ripisylve continue*
    - **RIPD** *Ripisylve discontinue*
    - **ENRO** *Enrochement*
    - **TECHV** *Technique végétale*
    - **ENHB** *Enherbées*
##### nomenclatures_diagnostic_perturbation
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Éléments pouvant perturber la fonctionalité d'un ouvrage
  - *valeurs* :
    - **C_P** *Circulation Piéton*
    - **CV** *Circulation Voiture*
    - **C2RQ** *Circulation 2-roues & quad*
    - **CTR** *Circulation tracteur*
    - **CHA** *Chasse*
    - **SONO** *Sonore*
    - **VISU** *Visuelle*
    - **AUT** *Autre (préciser)*
##### id_organisme
  - *type* : `clé simple`
  - *référence* : `organismes`
  - *champ(s)* : `nom_organisme`
  - *définition* : Organisme en charge du suivi
##### id_role
  - *type* : `clé simple`
  - *référence* : `utilisateurs`
  - *champ(s)* : `identifiant`
  - *définition* : Personne en charge du suivi


## Relations



### Diagnostics de clôture`

##### clotures.id_nomenclature_clotures_guidage_etat
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : État des clôtures pouvant guider les animaux vers le passage
  - *valeurs* :
    - **BON** *Bon*
    - **MOY** *Moyen*
    - **DEG** *Dégradée*
    - **NOJ** *Non jointive*
    - **AUT** *Autre (préciser)*
##### clotures.clotures_guidage_etat_autre
  - *type* : `string`
##### clotures.clotures_guidage_type_autre
  - *type* : `string`


### Diagnostics de vegetation tablier`

##### vegetation_tablier.id_nomenclature_vegetation_couvert
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Couverture végétale pour ce type de végétationd
  - *valeurs* :
    - **1** *0-25 %*
    - **2** *25-50 %*
    - **3** *50-75 %*
    - **4** *75-100 %*


### Diagnostics de vegetation débouchés`

##### vegetation_debouche.id_nomenclature_vegetation_couvert
 - *champ d'unicité*, *obligatoire*
  - *type* : `clé simple`
  - *référence* : `nomenclatures`
  - *champ(s)* : `cd_nomenclature`
  - *définition* : Couverture végétale pour ce type de végétation
  - *valeurs* :
    - **1** *0-25 %*
    - **2** *25-50 %*
    - **3** *50-75 %*
    - **4** *75-100 %*

