'''
    methodes pour les layout ajsf du frontend
'''


import copy
from ..errors import SchemaLayoutError


class SchemaConfigLayout():

    def form_layout(self):
        '''
            layout destiné au composant formulaire du frontend
        '''

        # - soit $meta.form.layout est defini,
        # - ou alors toutes les cle de properties
        form_layout = self.meta('form', {}).get('layout', list(self.properties().keys()))

        return self.process_form_layout(form_layout)

    def process_form_layout(self, layout):
        '''
            process recursif
        '''

        if type(layout) is str:
            return self.process_layout_key(layout)

        if type(layout) is list:
            return [self.process_form_layout(elem) for elem in layout]

        if type(layout) is dict:
            # soit c'est un groupe
            if self.is_form_layout_group(layout):
                return self.process_form_layout_group(layout)
            # soit c'est une cle
            if self.is_form_layout_key(layout):
                return self.process_layout_key(layout)


        raise SchemaLayoutError('layout non traité : {}'.format(layout))

    def is_form_layout_key(self, layout):

        if type(layout) is str:
            # étendre
            try:
                return self.get_property(layout) is not None
            except Exception:
                return False

        if type(layout) is dict and layout.get('key'):
            return self.is_form_layout_key(layout.get('key'))

        return False

    def is_form_layout_group(self, layout):
        return type(layout) is dict and 'key' not in layout

    def process_form_layout_group(self, layout):
        processed_layout = {
            'items': self.process_form_layout(layout.get('items', [])),
            "fxLayoutGap": "5px",  # pour eviter bug pourris gapValue is undefined flex.es5.js
        }

        processed_layout['type'] = 'div'

        if layout.get('title'):
            processed_layout['title'] = layout.get('title')

        if layout.get('direction') == 'row':
            processed_layout['type'] = 'flex'
            processed_layout['flex-direction'] = 'row'

        return processed_layout

    def process_layout_key(self, layout):
        processed_layout = copy.copy(layout)
        if type(layout) is str:
            key = layout
            processed_layout = {
                'key': key,
            }
        else:
            key = processed_layout['key']
            processed_layout['key'] = key,

        property = self.get_property(key)
        print(key, property)

        processed_layout['title'] = processed_layout.get('title') or property.get('label') or key.split('.')[-1]

        if property.get('geometry_type') == 'point':
            return {
                **processed_layout,
                **self.layout_geom_point(key)
            }

        if processed_layout.get('direction') == 'row':
            processed_layout['type'] = 'flex'
            processed_layout['flex-direction'] = 'row'

        if property['type'] == 'array':
            if processed_layout.get('direction') == 'row':
                processed_layout["displayFlex"] = "True"  # pour eviter bug pourris gapValue is undefined flex.es5.js
            processed_layout["fxLayoutGap"] = "5px"  # pour eviter bug pourris gapValue is undefined flex.es5.js
            processed_layout['type'] = 'array'
            processed_layout = {
                **processed_layout,
                **property
            }

            # sm = self.cls()(property['rel'])
            print('items', property['items'])
            processed_layout['items'] = self.process_form_layout(property['items'])


            # list(
            #     map(
            #         lambda item_key: '{}[].{}'.format(processed_layout['key'], item_key),
            #         layout.get('items')
            #     )
            # )
            # processed_layout['items'] = (
            #     {
            #         "fxLayoutGap": "5px",
            #         "type": "flex",
            #         "flex-direction": "row",
            #         'items': items
            #     } if layout.get('direction') == 'row'
            #     else items
            # )
        return processed_layout

    def layout_geom_point(self, key):
        return {
            "type": "div",
            "fxLayoutGap": "5px",
            "items": [
                # "{key}.type.format(key)",
                {
                    "title": " ",
                    "fxLayoutGap": "5px",
                    "listItems": 2,
                    "maxItems": 2,
                    "minItems": 2,
                    "add": None,
                    "key": "{}.coordinates".format(key),
                    "type": "array",
                    # "displayFlex": True,
                    # "flex-direction": "row",
                    "items": [
                        {
                            "key": "geom.coordinates[]",
                            "type": "number"
                        }
                    ]
                }
            ]
        }


    # def

        # form_layout = []
        # for key, column_def in self.columns().items():
        #     # cle primaires non affichées
        #     if column_def.get('primary_key'):
        #         continue

        #     elif self.get_foreign_key(column_def):

        #         relation = self.get_relation_from_foreign_key(self.get_foreign_key(column_def))
        #         options = {
        #             **relation.list_form_options(),
        #             'label': column_def['label']
        #         }
        #         if (column_def.get('nomenclature_type')):
        #             options['params'] = {
        #                 **options['params'],
        #                 'filters': [
        #                     {
        #                         'field': 'type.mnemonique',
        #                         'type': 'eq',
        #                         'value': column_def.get('nomenclature_type')
        #                     }
        #                 ]
        #             }

        #         form_layout.append({
        #             'key': key,
        #             'type': 'list-form',
        #             'options': options
        #         })

        #     elif self.is_geometry(column_def):
        #         form_layout.append({'key': key, '$ref': "#/definitions/geom/{}".format(column_def['geometry_type'])})
        #     else:
        #         form_layout.append({'key': key, 'type': column_def['type']})

        # return form_layout