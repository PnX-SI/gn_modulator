"""
config filters
"""


class SchemaConfigFilters:
    """
    config filters
    """

    def config_filters(self):
        return {
            "form": {
                "schema": self.config_filters_form_schema(),
                "layout": self.config_filters_form_layout(),
            },
            "defs": self.attr("filters.defs"),
        }

    def config_filters_form_schema(self):

        filters_defs = self.attr("filters.defs", {})
        properties = {
            key_filter: {
                "type": filter_def.get("type") or "string",
                "title": filter_def["title"],
            }
            for key_filter, filter_def in filters_defs.items()
        }
        return {"properties": properties}

    def config_filters_form_layout(self):
        return self.attr("filters.layout")

    def filter_values(self):
        # TODO add more
        return self.column_keys(sort=True)
