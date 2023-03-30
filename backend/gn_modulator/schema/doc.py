class SchemaDoc:
    """
    methodes pour faire de la doc
    """

    pass

    def doc_markdown(self, doc_type, exclude=[]):
        """
        retourne la doc d'un schema en markdown
        """

        if doc_type == "import":
            return self.doc_import(exclude)

        txt = ""

        txt += f"### Table `{self.sql_schema_dot_table()}`\n"
        txt += "\n"

        for key, property_def in self.columns().items():
            txt += f"- `{key}`\n"
            txt += f"  - *type*: `{property_def['type']}`\n"
            if property_def.get("description"):
                txt += f"  - *définition*: {property_def['description']}\n"

        return txt

    def doc_import_key(self, key):
        txt = ""

        property_def = self.property(key)
        txt += f"- `{key}`\n"
        type = property_def["type"]
        if property_def.get("schema_code"):
            type = "clé simple"

        if type == "relation":
            type = "liste de clé séparée par une virgule `,`"

        txt += f"  - *type*: `{type}`\n"

        if type == "geometry":
            txt += f"  - *geometry_type*: `{self.property(key)['geometry_type']}`\n"
            txt += "  - format:\n"
            txt += "    - WKT\n"
            txt += f"    - XY (remplacer {key} par les colonnes x et y)"

        if property_def.get("schema_code"):
            rel = self.cls(property_def["schema_code"])
            txt += f"  - *référence*: `{rel.labels()}`\n"

            champs = (
                ["cd_nomenclature"]
                if property_def["schema_code"] == "ref_nom.nomenclature"
                else rel.unique()
            )
            champs_txt = ", ".join(map(lambda x: f"`{x}`", champs))
            txt += f"  - *champ(s)*: {champs_txt}\n"

        if property_def.get("description"):
            txt += f"  - *définition*: {property_def['description']}\n"

        if property_def.get("nomenclature_type"):
            txt += self.doc_nomenclature_values(key)

        return txt

    def doc_nomenclature_values(self, key):
        txt = ""
        property_def = self.property(key)
        nomenclature_type = property_def["nomenclature_type"]
        txt += "  - *valeurs*:\n"
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

    def doc_import(self, exclude=[]):
        txt = ""

        import_keys = list(
            filter(
                lambda x: (
                    not (
                        self.property(x)["type"] == "relation"
                        and self.property(x)["relation_type"] != "n-n"
                    )
                    and (not self.property(x).get("primary_key"))
                    and (not self.property(x).get("is_column_property"))
                    and (not x in exclude)
                ),
                self.properties(),
            )
        )

        import_keys.sort(key=lambda x: (self.property(x).get("schema_code") or "", x))

        required_import_keys = list(
            filter(
                lambda x: self.is_required(x) and not self.property(x).get("default"), import_keys
            )
        )

        non_required_import_keys = list(
            filter(lambda x: x not in required_import_keys, import_keys)
        )

        txt += "\n\n#### Champs obligatoires\n\n"

        for key in required_import_keys:
            txt += self.doc_import_key(key)

        txt += "\n\n#### Champs facultatifs\n\n"

        for key in non_required_import_keys:
            txt += self.doc_import_key(key)

        return txt
