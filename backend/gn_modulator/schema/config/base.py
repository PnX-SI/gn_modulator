"""
    SchemaMethods : config processing
    - schema
    - display
    - util
"""

import copy


class SchemaConfigBase:
    """
    config used by frontend
    """

    def properties_config(self):
        """
        retourne les propriété en traitant les titles
        - fk
        - relation(fk)
        on peut donner par defaut les clé title et description à la relation
        """

        properties = copy.deepcopy(self.properties())
        for k in list(properties.keys()):
            if self.is_relation_n_1(k):
                prop = self.property(k)
                fk_prop = self.property(prop["local_key"])
                for prop_key in ["title", "description"]:
                    if fk_prop.get(prop_key) and prop_key not in prop:
                        prop[prop_key] = fk_prop[prop_key]
        return properties

    def config(self, object_definition={}):
        return {
            "display": self.config_display(object_definition),
            "utils": self.config_utils(),
            # "form": self.config_form(),
            # "table": self.config_table(),
            # "map": self.config_map(),
            # "filter_defs": self.config_filters(),
            # "details": self.config_details(),
            # "properties": self.properties_config(),
            "properties": self.properties(),
            "json_schema": self.json_schema,
        }

    def config_map(self):
        """
        configmap
        """
        return self.attr("map", {})

    def columns_table(self):
        """
        config table pour tabulator : columns
        """

        columns = []

        layout_field = "table.columns"
        column_keys = self.attr(layout_field) or self.columns()

        for key in column_keys:
            """
            relations un seul . pour l'instant
            """
            column_def = {}
            if "." in key:
                (key_relationship, key_column) = key.split(".")
                relation_def = self.relationship(key_relationship)
                # relation = self.cls(relation_def["schema_code"])
                # relation_column = relation.column(key_column)
                column_def = {
                    "title": relation_def["title"],
                    "field": key,
                    "headerFilter": True,
                    "type": relation_def["type"],
                }
            else:
                column = self.column(key)
                column_def = {
                    "title": column["title"],
                    "field": key,
                    "headerFilter": True,
                    "type": column["type"],
                }

            columns.append(column_def)

        return columns

    def config_details(self):
        return {"layout": self.process_layout(self.attr("details.layout"))}

    def config_table(self):
        """
        config table pour tabulator
        """

        return {
            "columns": self.columns_table(),
            "sort": self.attr("table.sort", ""),
            "url": self.url("/rest/", full_url=True),
        }

    def config_utils(self):
        """
        frontend processing
        """

        return {
            "columns_array": self.columns_array(columns_only=True),
            "urls": {
                "export": self.url("/export/", full_url=True),
                "rest": self.url("/rest/", full_url=True),
                "page_number": self.url("/page_number/", full_url=True),
            },
            "pk_field_name": self.pk_field_name(),
            "label_field_name": self.label_field_name(),
            "title_field_name": self.title_field_name(),
            "value_field_name": self.value_field_name(),
            "geometry_field_name": self.geometry_field_name(),
            "model_name": self.model_name(),
            "schema_code": self.schema_code(),
            "sql_schema_name": self.sql_schema_name(),
            "sql_table_name": self.sql_table_name(),
            "page_size": self.page_size(),
        }

    def page_size(self):
        return self.attr("meta.page_size", 10)

    def config_form(self):
        """
        configuration pour le formulaire en frontend
        destiné au composant ajsf (angular json schema form)
        """

        return {
            "schema": self.remove_field("description", self.json_schema),
            "layout": self.form_layout(),
        }

    def value_field_name(self):
        return self.attr("meta.value_field_name", self.pk_field_name())

    def label_field_name(self):
        return self.attr("meta.label_field_name")

    def title_field_name(self):
        return self.attr("meta.title_field_name")

    def geometry_field_name(self):
        return self.attr("meta.geometry_field_name")

    def list_form_options(self):
        """ """
        return {
            "api": self.url("/rest/", full_url=True),
            "value_field_name": self.value_field_name(),
            "label_field_name": self.label_field_name(),
            "geometry_field_name": self.geometry_field_name(),
            "reload_on_search": True,
            "params": {"page_size": 7},
            "label": self.label(),
        }

    def description(self, object_definition={}):
        return self.attr("meta.description", f"Schéma '{self.schema_code()}'")
