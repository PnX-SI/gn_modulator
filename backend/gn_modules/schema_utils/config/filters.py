'''
config filters
'''

class SchemaConfigFilters():
    '''
        config filters
    '''

    def config_filters(self):
        return {
            'form': {
                'schema': self.config_filters_form_schema(),
                'layout': self.config_filters_form_layout(),

            },
            'defs': self.meta('filters.defs')
        }

    def config_filters_form_schema(self):

        filters_defs = self.meta('filters.defs', {})
        properties = {
            key_filter: {
                "type": filter_def.get('type') or "string",
                "title": filter_def['title'],
            }
            for key_filter, filter_def in filters_defs.items()
        }
        return {
            "properties": properties
        }

    def config_filters_form_layout(self):
        return self.meta('filters.layout')
        # layout = copy.copy(self.meta('filters.layout'))
        # return self.process_filters_form_layout(layout)

    # def process_filters_form_layout(self, layout):

    #     if type(layout) is list:
    #         return [ self.process_filters_form_layout(l) for l in layout]

    #     if type(layout) is dict:

    #         d = {
    #             k: self.process_filters_form_layout(v)
    #             for k, v in layout.items()
    #         }

    #         if d['key'] == 'list-form':
    #             prrr
    #         return d

    #     return layout

    # def config_filters_form_schema_save(self):
    #     return {
    #         "properties": {
    #             "definition": {
    #                 "type": "string"
    #             },
    #             "filters": {
    #                 "type": "array",
    #                 "items": {
    #                     "type": "object",
    #                     "properties": {
    #                         "field": {"type": "string", "enum": self.filter_values()},
    #                         "type": {"type": "string", "enum": self.filter_types()},
    #                         "value": {"type": "string"}
    #                     },
    #                     # "required": ["field", "type", "value"]
    #                 }
    #             }
    #         }
    #     }

    # def config_filters_form_layout(self):
    #     # return None
    #     return [
    #         {
    #             "title": "Filtres",
    #             "key": "filters",
    #             "type": "array",
    #             "fxLayoutGap": "5px",
    #             "items": {
    #                 "type": "flex",
    #                 "flex-direction": "row",
    #                 "fxLayoutGap": "5px",
    #                 "items": ["filters[].field", "filters[].type", "filters[].value"]
    #             }
    #         }
    #     ]

    def filter_values(self):
        # TODO add more
        return self.column_keys(sort=True)

