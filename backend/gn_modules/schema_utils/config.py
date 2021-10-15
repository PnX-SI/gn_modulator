'''
    SchemaMethods : config processing
    - schema
    - display
    - util
'''

from gn_modules.utils import unaccent
import copy


import json

class SchemaConfig():
    '''
    config used by frontend
    '''
    def config(self):
        '''
        frontend config
        '''

        self.reload()

        return {
            'schema_raw': self.schema(),
            'form': self.config_form(),
            'display': self.config_display(),
            'utils': self.config_utils(),
            'table': self.config_table()
        }


    def columns_table(self):
        """
            config table pour tabulator : columns
        """

        columns = []

        column_keys = (
            self._schema['$meta']
                .get('table',{})
                .get('columns')
            or self.properties(processed_properties_only=True).keys()
        )

        for key in column_keys:

            '''
                relations un seul . pour l'instant
            '''
            column_def = {}
            if '.' in key:
                (key_rel, key_prop) = key.split('.')
                rel = self.get_relation(key_rel)
                prop = rel.get_property(key_prop)
                column_def = {'title': prop['label'], 'field': key, 'headerFilter': True}
            else:
                prop = self.get_property(key)
                column_def = {'title': prop['label'], 'field': key, 'headerFilter': True}

            columns.append(column_def)

        return columns

    def config_table(self):
        """
            config table pour tabulator
        """

        return {
            'columns': self.columns_table(),
            'url': self.url('/rest/', full_url=True)
        }


    def config_display(self):
        '''
        frontend display (label, etc..)
        '''
        return {
            "label": self.label(),
            "labels": self.labels(),
            "def_label": self.def_label(),
            "undef_label": self.undef_label(),
            "undef_label_new": self.undef_label_new(),
            "undef_labels_new": self.undef_labels_new(),
            "prep_label": self.prep_label(),
            "def_labels": self.def_label(),
            "undef_labels": self.undef_labels(),
            "description": self.description(),
        }

    def config_utils(self):
        '''
        frontend processing
        '''

        return {
            'properties_array': self.properties_array(processed_properties_only=True),
            'urls': {
                'rest': self.url('/rest/', full_url=True)
            },
            'pk_field_name': self.pk_field_name(),
            'model_name': self.model_name(),
            'full_name': self.full_name(),
            'sql_schema_name': self.sql_schema_name(),
            'sql_table_name': self.sql_table_name(),
        }

    def definition_ref(self):
        return '#/definitions/{}'.format(self.full_name('/'))
        #return '#/definitions/{}/{}'.format(self.self.object_name())

    def definition(self):
        '''
            definition pour les schema ajsf
        '''
        definition = {
            'type': 'object',
            'properties': self.properties(processed_properties_only=True)
        }

        return definition

    def config_form(self):
        '''
            configuration pour le formulaire en frontend
            destiné au composant ajsf (angular json schema form)
        '''

        return {
            "schema": self.schema_ajsf(),
            "layout": self.layout_form()
        }

    def layout_form(self):
        '''
            layout destiné au composant formulaire du frontend
        '''

        return self._schema['$meta'].get('form', {}).get('layout', self.auto_layout())




    def value_field_name(self):
        return self._schema['$meta'].get('value_field_name', self.pk_field_name())

    def label_field_name(self):
        return self._schema['$meta']['label_field_name']


    def list_form_options(self):
        '''
        '''
        return {
            'api': self.url('/rest/', full_url=True),
            'value_field_name': self.value_field_name(),
            'label_field_name': self.label_field_name(),
            "data_reload_on_search": True,
            "params": {
                "size": 7
            },
            "label": self.label(),
        }

    def auto_layout(self):
        layout = []
        for k, v in self.properties(processed_properties_only=True).items():
            # cle primaires non affichées
            print(k)
            if v.get('primary_key'):
                continue

            elif v.get('foreign_key'):
                relation = self.__class__().load_from_reference(v.get('foreign_key'))
                layout.append({
                    'key': k,
                    'type': 'list-form',
                    'options': {
                        **relation.list_form_options(),
                        'label': v['label']
                    }
                })

            else:
                layout.append({ 'key': k, 'type': v['type'] })

        return layout


    def schema_ajsf(self):
        '''
            schema pour le composant angulat json form
            https://github.com/hamzahamidi/ajsf
        '''

        properties = self.properties(processed_properties_only=True)

        # definitions pour les références

        definitions = {}
        for k,v in properties.items():
            if v['type'] == 'geom':

                geojson_geometry = {}
                geom_file_name = self.__class__.cls_schema_file_path('geom', 'Geometry')
                with open(geom_file_name) as f:
                    geojson_geometry = json.load(f)
                definitions['geom'] = {
                    **geojson_geometry,
                    "$id": "geom"
                }
                properties[k]['$ref']="#/definitions/geom"

        for k,v in self.relationships().items():
            relation_reference = v['$ref']
            sm_relation = self.__class__().load_from_reference(relation_reference)

            #definitions[sm_relation.object_name()] = sm_relation.definition()

            definitions[sm_relation.group_name()] = definitions.get(sm_relation.group_name(), {})
            definitions[sm_relation.group_name()][sm_relation.object_name()] = sm_relation.definition()

            properties[k] = {
                '$ref': sm_relation.definition_ref()
            }


        return {
            'definitions': definitions,
            'type': 'object',
            'properties': properties,
        }

    def genre(self):
        '''
            returns schema genre
        '''
        return self._schema['$meta']['genre']

    def new(self):
        return (
            'nouvelle ' if self.genre() == 'F'

            else 'nouvel ' if self.is_first_letter_vowel(self.label())
            else 'nouveau '
        )

    def news(self):
        return (
            'nouvelles ' if self.genre() == 'F'
            else 'nouveaux '
        )

    def label(self):
        '''
            returns schema label in lowercase
        '''
        return self._schema['$meta']['label'].lower()

    def labels(self):
        return self._schema['$meta'].get('labels', '{}s'.format(self.label()))

    def is_first_letter_vowel(self, string):
        '''
            returns True if unaccented first letter in 'aeiouy'
        '''
        return unaccent(self.label()[0]) in 'aeiouy'

    def article_def(self):
        '''
            renvoie l'article défini pour le label

            prend en compte:
            - le genre (depuis $meta)
            - si le label commence par une voyelle
            - s'il y a un espace après l'article ou non
        '''
        return (
            "l'" if self.is_first_letter_vowel(self.label())
            else 'la ' if self.genre() == 'F'
            else 'le '
        )

    def article_undef(self):
        '''
            renvoie l'article indéfini pour le label

            cf article_def
        '''

        return (
            'une ' if self.genre() == 'F'
            else 'un '
        )

    def preposition(self):
        '''
            du, de la, de l'
        '''
        return (
            "de l'" if self.is_first_letter_vowel(self.label())
            else 'de la ' if self.genre() == 'F'
            else 'du '
        )

    def def_label(self):
        '''
        Renvoie le label précédé de l'article défini
        '''
        return '{}{}'.format(self.article_def(), self.label())

    def undef_label(self):
        '''
        Renvoie le label précédé de l'article indéfini
        '''
        return '{}{}'.format(self.article_undef(), self.label())

    def undef_label_new(self):
        '''
        Renvoie le label précédé de l'article indéfini et de self.new()
        '''
        return '{}{}{}'.format(self.article_undef(), self.new(), self.label())

    def undef_labels_new(self):
        '''
        Renvoie le labels précédé de l'article indéfini et de self.new()
        '''
        return 'des {}{}'.format(self.news(), self.labels())

    def prep_label(self):
        '''
        Renvoie le label précédé de la préposition
        '''
        return '{}{}'.format(self.preposition(), self.label())

    def def_labels(self):
        return 'les {}'.format(self.labels())

    def undef_labels(self):
        return 'des {}'.format(self.labels())

    def description(self):
        return self._schema['$meta'].get('description', "Schéma '{}' pour le module '{}'".format(self.object_name(), self.group_name()))
