from gn_modulator.schema import SchemaMethods
from gn_modulator.utils.env import schema_import
from gn_modulator import ModuleMethods


import_steps = [
    "init",
    "data_table",
    "mapping_view",
    "pre_check",
    "raw_view",
    "import_view",
    "relations_view",
    "post_check",
    "count",
    "update",
    "insert",
    "relations_data",
]


class ImportMixinUtils:
    """
    Classe de mixin destinée à TImport

    Fonction utiles utilisées dans les autres fichiers de ce dossier
    """

    # correspondance type schema, type sql
    sql_type_dict = {
        "integer": "INTEGER",
        "boolean": "BOOLEAN",
        "number": "FLOAT",
        "string": "VARCHAR",
        "date": "DATE",
        "datetime": "TIMESTAMP",
        "uuid": "UUID",
        "geometry": "GEOMETRY",
        "json": "JSONB",
    }

    def remaining_import_steps(self):
        remaining_import_steps = []
        for step in self.import_steps():
            if step in self.steps or step in self.options.get("skip_steps", []):
                continue
            remaining_import_steps.append(step)
            if self.options.get("target_step") == step:
                break
        return remaining_import_steps

    def import_steps(self):
        return import_steps

    def process_step_init(self):
        """
        Initialisation de l'import
        """

        # récupération de schema_code à partir de
        #   - schema_code
        #   - (module_code_object_code)
        self.schema_code = self.schema_code or ModuleMethods.schema_code(
            self.module_code, self.object_code
        )
        if not self.schema_code:
            self.add_error(
                error_code="ERR_IMPORT_SCHEMA_CODE_NOT_FOUND",
                error_msg=f"Il n'y a pas de schema pour module_code={self.module_code}, object_code={self.object_code}",
            )
            return

        if not self.sm().definition:
            self.add_error(
                error_code="ERR_IMPORT_SCHEMA_CODE_NOT_VALID",
                error_msg=f"Il n'y a pas de schema {self.schema_code}",
            )
            return
        # Creation du schema d'import s'il n'existe pas
        SchemaMethods.c_sql_exec_txt(f"CREATE SCHEMA IF NOT EXISTS {schema_import}")

        # Verification du srid fourni dans les options
        # - on verifie que c'est bien un entier
        # - pour éviter les injections sql
        if self.options.get("srid"):
            try:
                int(self.options.get("srid"))
            except ValueError:
                self.add_error(
                    error_code="ERR_IMPORT_OPTIONS",
                    error_msg=f"Le srid n'est pas valide {self.options.get('srid')}",
                )

    def count_and_check_table(self, table_type, table_name):
        """
        Commande qui va
          - compter le nombre de lignes dans une table ou vue (créer pour l'import)
          - permet de vérifier l'intégrité de la table/vue
        """

        if self.errors:
            return

        try:
            self.res[f"nb_{table_type}"] = SchemaMethods.c_sql_exec_txt(
                f"SELECT COUNT(*) FROM {table_name}"
            ).scalar()

        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_COUNT_VIEW",
                error_msg=f"Erreur avec la table/vue '{table_type}' {table_name}: {str(e)}",
            )
            return

        if self.res[f"nb_{table_type}"] == 0:
            self.add_error(
                error_code="ERR_IMPORT_COUNT_VIEW",
                error_msg=f"Erreur avec la table/vue '{table_type}' {table_name}: il n'y a n'a pas de données",
            )

    def table_name(self, type, key=None):
        """
        nommange de la table
        """

        if type == "data" and key is None:
            return f"{schema_import}.t_{self.id_import}_{type}"
        else:
            rel = f"_{key}" if key is not None else ""
            return f"{schema_import}.v_{self.id_import}_{type}_{self.schema_code.replace('.', '_')}{rel}"

    def add_error(
        self,
        error_code=None,
        error_msg=None,
        key=None,
        lines=None,
        valid_values=None,
        error_values=None,
    ):
        """
        ajout d'une erreur lorsque qu'elle est rencontrée
        """
        self.errors.append(
            {
                "error_code": error_code,
                "error_msg": error_msg,
                "key": key,
                "lines": lines,
                "valid_values": valid_values,
                "error_values": error_values,
            }
        )
        self.status = "ERROR"

    def get_table_columns(self, table_name, reset_cache=False):
        """
        récupération des colonnes d'une table
        - avec mise en cache pour éviter de multiplier les requetes
        """
        if reset_cache:
            self._columns[table_name] = None
        if not self._columns.get(table_name):
            self._columns[table_name] = SchemaMethods.get_table_columns(table_name)
        return self._columns[table_name]

    def id_digitiser_key(self):
        """
        gestion du numérisateur
        - on regarde si la table destinataire possède un champs nommé
          - id_digitiser
          - ou id_digitizer
        """
        for key in ["id_digitiser", "id_digitizer"]:
            if SchemaMethods(self.schema_code).has_property(key):
                return key

    def clean_column_name(self, x):
        return f'"{x}"' if "." in x else x

    def clean_column_names(self, x):
        return map(lambda y: self.clean_column_name(y), x)

    def sm(self):
        return SchemaMethods(self.schema_code)

    def has_mapping(self):
        return (
            self.id_mapping is not None
            or self.id_mapping_value is not None
            or self.id_mapping_field is not None
        )

    def has_errors(self):
        return len(self.errors) > 0 or any(child.has_errors() for child in self.imports_1_n)

    def Model(self):
        return self.sm().Model()
