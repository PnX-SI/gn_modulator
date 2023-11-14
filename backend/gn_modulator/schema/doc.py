import yaml
from gn_modulator.utils.yaml import YmlLoader


class SchemaDoc:
    """
    methodes pour faire de la doc
    """

    pass

    def doc_markdown(self, doc_type, exclude=[], file_path=None):
        """
        retourne la doc d'un schema en markdown
        """

        if doc_type == "import":
            return self.doc_import(exclude)

        if doc_type == "import_fields":
            return self.doc_import_fields(exclude)

        if doc_type == "table":
            return self.doc_table(exclude)

        if doc_type == "csv":
            return self.doc_csv(file_path)

    def doc_csv(self, file_path):
        with open(file_path) as f:
            data = yaml.load(f, YmlLoader)
            txt = ";".join(data[0].keys()) + "\n"
            for d in data:
                txt += ";".join(map(lambda x: str(x), d.values()))
            return txt

    def doc_table(self, exclude=[]):
        txt = ""

        txt += f"### Table `{self.sql_schema_dot_table()}`\n"
        txt += "\n"

        for key, property_def in self.columns().items():
            txt += f"- `{key}`\n"
            txt += f"  - *type* : `{property_def['type']}`\n"
            if property_def.get("description"):
                txt += f"  - *définition* : {property_def['description']}\n"

        return txt

    def doc_import_key(
        self,
        key,
        unique=False,
        relation_key=None,
    ):
        txt = ""

        key_txt = f"{relation_key}.{key}" if relation_key is not None else key

        property_def = self.property(key)
        # txt += f"- `{key_txt}`\n"
        txt += f"##### {key_txt}\n"

        type = (
            "clé simple"
            if property_def.get("schema_code")
            else "liste de clés séparées par une virgule"
            if property_def.get("relation_type") == "n-n"
            else property_def["type"]
        )

        column_default = self.property(key).get("default") or (
            self.get_column_info(key) or {}
        ).get("default")

        infos = []
        if unique:
            infos.append("champ d'unicité")
        if self.is_required(key) and not column_default:
            infos.append("obligatoire")

        if len(infos) > 0:
            info_txt = ", ".join(map(lambda x: f"*{x}*", infos))
            txt += f" - {info_txt}\n"

        txt += f"  - *type* : `{type}`\n"

        if type == "geometry":
            txt += f"  - *geometry_type* : `{self.property(key)['geometry_type']}`\n"
            txt += f"  - *format* (exemples à adapter au `SRID`=`{self.property(key)['srid']}`):\n"
            txt += "    - WKT (par ex. `POINT(0.1 45.2)`\n"
            txt += f"    - XY (remplacer `{key}` par les colonnes `x` et `y`)\n"

        if type == "date":
            txt += "  - *format* : `YYYY-MM-DD` (par ex. `2023-03-31`)\n"

        if type == "boolean":
            txt += "  - *format* : `true`,`t`,`false`,`f`\n"

        if property_def.get("schema_code"):
            rel = self.cls(property_def["schema_code"])
            txt += f"  - *référence* : `{rel.labels()}`\n"

            champs = (
                ["cd_nomenclature"]
                if property_def["schema_code"] == "ref_nom.nomenclature"
                else rel.unique()
            )
            champs_txt = ", ".join(map(lambda x: f"`{x}`", champs))
            txt += f"  - *champ(s)* : {champs_txt}\n"

        if property_def.get("description"):
            txt += f"  - *définition* : {property_def['description']}\n"

        if property_def.get("nomenclature_type"):
            txt += self.doc_nomenclature_values(key)

        if unique:
            if column_default:
                txt += "  - champ autogénéré pour les lignes où il est de valeur nulle\n"

        return txt

    def doc_nomenclature_values(self, key):
        txt = ""
        property_def = self.property(key)
        nomenclature_type = property_def["nomenclature_type"]
        txt += "  - *valeurs* :\n"
        sm_nom = self.cls("ref_nom.nomenclature")
        res = sm_nom.query_list(
            params={
                "fields": ["label_fr", "cd_nomenclature"],
                "filters": [f"nomenclature_type.mnemonique = {nomenclature_type}"],
            }
        ).all()
        values = sm_nom.serialize_list(res, ["label_fr", "cd_nomenclature"])

        for v in values:
            txt += f"    - **{v['cd_nomenclature']}** *{v['label_fr']}*\n"

        return txt

    def import_keys(self, exclude=[]):
        exclude = exclude or self.attr("meta.import_excluded_fields") or []
        import_keys = list(
            filter(
                lambda x: (
                    not (
                        self.property(x)["type"] == "relation"
                        and self.property(x)["relation_type"] != "n-n"
                    )
                    and (not self.property(x).get("primary_key"))
                    and (not self.property(x).get("is_column_property"))
                    and (x not in exclude)
                ),
                self.properties(),
            )
        )

        import_keys.sort(key=lambda x: (self.property(x).get("schema_code") or "", x))

        unique_import_keys = list(filter(lambda x: x in self.unique(), import_keys))

        required_import_keys = list(
            filter(
                lambda x: self.is_required(x)
                and not self.property(x).get("default")
                and x not in unique_import_keys,
                import_keys,
            )
        )

        non_required_import_keys = list(
            filter(
                lambda x: x not in required_import_keys and x not in unique_import_keys,
                import_keys,
            )
        )

        return unique_import_keys, required_import_keys, non_required_import_keys

    def doc_import_fields(self, exclude=[]):
        required_import_keys, non_required_import_keys = self.import_keys(exclude)

        return ",".join(required_import_keys + non_required_import_keys)

    def doc_import(self, exclude=[], relation_key=None):
        txt = ""

        unique_import_keys, required_import_keys, non_required_import_keys = self.import_keys(
            exclude
        )

        if relation_key is None:
            txt += f"\n\n# Import des {self.labels()}\n\n"
            txt += "\n\n### Champs\n\n"
        else:
            txt += f"\n\n### {self.labels().capitalize()}`\n\n"

        # txt += "\n\n#### Champs d'unicité\n\n"

        for key in unique_import_keys:
            txt += self.doc_import_key(key, unique=True, relation_key=relation_key)

        if len(required_import_keys) > 0:
            # txt += "\n\n#### Champs obligatoires\n\n"

            for key in required_import_keys:
                txt += self.doc_import_key(key, relation_key=relation_key)

        if len(non_required_import_keys):
            # txt += "\n\n#### Champs facultatifs\n\n"

            for key in non_required_import_keys:
                txt += self.doc_import_key(key, relation_key=relation_key)

        if relation_key:
            return txt

        relations_1_n_import_keys = [
            relation_key
            for relation_key in self.relationship_1_n_keys()
            if relation_key not in self.attr("meta.import_excluded_fields", [])
        ]

        if len(relations_1_n_import_keys) == 0:
            return txt

        txt += "\n\n## Relations\n\n"

        for relation_key in relations_1_n_import_keys:
            rel = self.cls(self.property(relation_key)["schema_code"])
            exclude = rel.attr("meta.import_excluded_fields", [])
            exclude.append(self.pk_field_name())
            txt += rel.doc_import(relation_key=relation_key, exclude=exclude)

        return txt
