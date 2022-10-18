cor_type = [
    {"definition": "integer", "sql": "INTEGER"},
    {"definition": "boolean", "sql": "BOOLEAN"},
    {"definition": "number", "sql": "FLOAT"},
    {"definition": "string", "sql": "VARCHAR"},
    {"definition": "date", "sql": "DATE"},
    {"definition": "datetime", "sql": "DATETIME"},
    {"definition": "uuid", "sql": "UUID"},
    {"definition": "geometry", "sql": "GEOMETRY"},
    {"definition": "json", "sql": "JSONB"},
]


class SchemaTypes:
    """
    types methods
    """

    @classmethod
    def c_get_type(cls, type_in, field_name_in, field_name_out):
        """
        TODO simplifier ??
        """
        if field_name_in == "sql" and "geometry" in type_in.lower():
            inter = type_in.lower().replace("geometry(", "").replace(")", "")
            inter = inter.split(",")
            geometry_type = inter[0]
            srid = int(inter[1])

            return {"type": "geometry", "srid": srid, "geometry_type": geometry_type}

        # autres
        type_out = next(
            (
                item[field_name_out]
                for item in cor_type
                if item[field_name_in] == type_in
            ),
            None,
        )
        return {"type": type_out}
