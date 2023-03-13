# Import

# TODO 
    donner exemple pour chaque étapes

## Les étapes

### 1) Données

Chargement du fichier de données dans une table `gn_modulator_import.t_<id_import_data>`
  - Toutes les colonnes sont de type `VARCHAR`
  - On passe tous les champs de valeur `''` à `NULL`
  - La première ligne donne le nom des colonnes
  - seulement pour les fichiers csv, à voir si l'on prévoit d'autres formats

### 2) Mapping (optionnel)

Creation du vue de mapping pour réorganiser les colonnes de la table de données à partir d'une instruction select `SELECT`

### 3) Vue brute (`raw`)

En partant de vue de mapping si elle existe, ou de la table de donnée, on cherche à donner le bon type aux colonnes.

### 4) Vue process

En partant de la vue brute, on cherche à résoudre les clé étrangère
La vue process est prête à être intégrée telle quelle dans la table destinataire elle possède les bonnes id


### 5) Vérification des données

On collecte des erreur si
- dans la table `raw`, une colonnes requise possède une valeur NULL.
- dans la table `process` il y a ube clé étrangère NULL aors qu'elle est non nulles dans la table `raw`.

### 5) Insertion des données

On insère dans la table destinataire les lignes de la table process pour lequelles la colonne corespondant à la clé primaire est nulle.

### 6) Mise à jour des données (optionnel)

On met à jour les ligne sde la table destinataire qui correspondent aux lignes de la table process
- pour lequelles la colonne corespondant à la clé primaire est nulle.
- et où une au moins des colonnes est différente de celle de la ligne destinataire

### 7) Traitement des relations n-n

- Effacement de toutes les lignes concernées
- Insert des lignes selon les données