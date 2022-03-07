class SchemaDoc():
    '''
        methodes pour faire de la doc
    '''
    pass

    def doc_markdown(self):
        """
            retourne la doc d'un schema en markdown
        """

        txt = ""

        txt += f"### Table `{self.sql_schema_dot_table()}`\n"
        txt += "\n"

        for key, property_def in self.columns().items():
            txt += f"- `{key}`\n"
            txt += f"  - *type*: `{property_def['type']}`\n"
            if property_def.get('description'):
                txt += f"  - *définition*: {property_def['description']}\n"

        return txt