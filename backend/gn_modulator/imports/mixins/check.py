from gn_modulator import SchemaMethods
from pypnnomenclature.repository import get_nomenclature_list

from .utils import ImportMixinUtils


class ImportMixinCheck(ImportMixinUtils):
    def process_check(self):
        self.check_required()
        self.check_resolve_keys()

    def check_required(self):
        # pour toutes les colonnes de raw
        # si une colonne est requise
        # et que la valeur dans raw est nulle
        # erreur
        raw_table = self.tables["raw"]
        sm = SchemaMethods(self.schema_code)

        for key in SchemaMethods.get_table_columns(raw_table):
            if not sm.is_required(key):
                continue

            txt_check_required = f"""
SELECT
    COUNT(*), ARRAY_AGG(id_import)
    FROM {raw_table}
    WHERE {key} is NULL
"""

            res = SchemaMethods.c_sql_exec_txt(txt_check_required).fetchone()
            nb_lines = res[0]
            lines = res[1]
            str_lines = lines and ", ".join(map(lambda x: str(x), lines)) or ""
            if nb_lines == 0:
                continue
            self.add_error(
                code="ERR_IMPORT_REQUIRED",
                key=key,
                lines=lines,
                msg=f"La colonne {key} est obligatoire. {nb_lines} ligne(s) concernée(s) : [{str_lines}]",
            )

        return

    def check_resolve_keys(self):
        raw_table = self.tables["raw"]
        process_table = self.tables["process"]
        sm = SchemaMethods(self.schema_code)

        for key in SchemaMethods.get_table_columns(raw_table):
            if not (sm.has_property(key) and sm.property(key).get("foreign_key")):
                continue

            txt_check_resolve_keys = f"""
SELECT COUNT(*), ARRAY_AGG(r.id_import)
FROM {raw_table} r
JOIN {process_table} p 
    ON r.id_import = p.id_import
WHERE
    p.{key} is NULL and r.{key} is NOT NULL
            """

            res = SchemaMethods.c_sql_exec_txt(txt_check_resolve_keys).fetchone()
            nb_lines = res[0]
            lines = res[1]
            str_lines = lines and ", ".join(map(lambda x: str(x), lines)) or ""
            if nb_lines == 0:
                continue

            values = None
            if code_type := sm.property(key).get("nomenclature_type"):
                values = list(
                    map(
                        lambda x: {
                            "cd_nomenclature": x["cd_nomenclature"],
                            "label_fr": x["label_fr"],
                        },
                        get_nomenclature_list(code_type=code_type)["values"],
                    )
                )
            self.add_error(
                code="ERR_IMPORT_UNRESOLVED",
                key=key,
                lines=lines,
                msg=f"La colonne {key} est non nulle et n'a pas de correspondance. {nb_lines} ligne(s) concernée(s) : [{str_lines}]",
                values=values,
            )
