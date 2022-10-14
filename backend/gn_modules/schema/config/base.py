'''
    SchemaMethods : config processing
    - schema
    - display
    - util
'''

from gn_modules.utils import unaccent


class SchemaConfigBase():
    '''
    config used by frontend
    '''

    def config(self, object_definition={}):
        return {
            'display': self.config_display(object_definition),
            'utils': self.config_utils(),
            'form': self.config_form(),
            'table': self.config_table(),
            'map': self.config_map(),
            'filters': self.config_filters(),
            'details': self.config_details(),
            'definition': self.definition,
        }

    def config_old(self):
        '''
        frontend config
        '''

        # self.reload()

        return {
            'definition': self.definition,
            'validation': self.validation_schema,
            'form': self.config_form(),
            'display': self.config_display(),
            'utils': self.config_utils(),
            'table': self.config_table(),
            'map': self.config_map(),
            'filters': self.config_filters(),
            'details': self.config_details(),
        }

    def config_map(self):
        '''
            configmap
        '''
        return self.attr('map', {})

    def columns_table(self):
        """
            config table pour tabulator : columns
        """

        columns = []

        layout_field = 'table.columns'
        column_keys = (
            self.attr(layout_field)
            or
            self.columns()
        )

        for key in column_keys:

            '''
                relations un seul . pour l'instant
            '''
            column_def = {}
            if '.' in key:

                (key_relationship, key_column) = key.split('.')
                relation_def = self.relationship(key_relationship)
                relation = self.cls(relation_def['schema_name'])
                relation_column = relation.column(key_column)
                column_def = {
                    'title': relation_def['title'],
                    'field': key,
                    'headerFilter': True,
                    'type': relation_def['type']
                }
            else:
                column = self.column(key)
                column_def = {
                    'title': column['title'],
                    'field': key,
                    'headerFilter': True,
                    'type': column['type']
                }

            columns.append(column_def)

        return columns

    def config_details(self):
        return {
            'layout': self.process_layout(self.attr(
                'details.layout'
            ))
        }

    def config_table(self):
        """
            config table pour tabulator
        """

        return {
            'columns': self.columns_table(),
            'sort': self.attr('table.sort', ''),
            'url': self.url('/rest/', full_url=True)
        }

    def config_display(self, object_definition={}):
        '''
        frontend display (label, etc..)
        '''
        return {
            "label": self.label(object_definition),
            "labels": self.labels(object_definition),
            "le_label": self.le_label(object_definition),
            "les_labels": self.les_labels(object_definition),
            "un_label": self.un_label(object_definition),
            "des_labels": self.des_labels(object_definition),
            "un_nouveau_label": self.un_nouveau_label(object_definition),
            "du_nouveau_label": self.du_nouveau_label(object_definition),
            "d_un_nouveau_label": self.d_un_nouveau_label(object_definition),
            "des_nouveaux_labels": self.des_nouveaux_labels(object_definition),
            "du_label": self.du_label(object_definition),
            "description": self.description(object_definition),
        }

    def config_utils(self):
        '''
        frontend processing
        '''

        return {
            'columns_array': self.columns_array(columns_only=True),
            'urls': {
                'export': self.url('/export/', full_url=True),
                'rest': self.url('/rest/', full_url=True),
                'page_number': self.url('/page_number/', full_url=True)
            },
            'pk_field_name': self.pk_field_name(),
            'label_field_name': self.label_field_name(),
            'title_field_name': self.attr('meta.title_field_name'),
            'value_field_name': self.value_field_name(),
            'geometry_field_name': self.geometry_field_name(),
            'model_name': self.model_name(),
            'schema_name': self.schema_name(),
            'sql_schema_name': self.sql_schema_name(),
            'sql_table_name': self.sql_table_name(),
            'page_size': self.page_size()
        }

    def page_size(self):
        return self.attr('meta.page_size', 10)

    def config_form(self):
        '''
            configuration pour le formulaire en frontend
            destiné au composant ajsf (angular json schema form)
        '''

        return {
            "schema": self.remove_field('description', self.json_schema),
            "layout": self.form_layout()
        }

    def value_field_name(self):
        return self.attr('meta.value_field_name', self.pk_field_name())

    def label_field_name(self):
        return self.attr('meta.label_field_name')

    def geometry_field_name(self):
        return self.attr('meta.geometry_field_name')

    def list_form_options(self):
        '''
        '''
        return {
            'api': self.url('/rest/', full_url=True),
            'value_field_name': self.value_field_name(),
            'label_field_name': self.label_field_name(),
            'geometry_field_name': self.geometry_field_name(),
            "data_reload_on_search": True,
            "params": {
                "page_size": 7
            },
            "label": self.label(),
        }

    def genre(self, object_definition={}):
        '''
            returns schema genre
        '''

        return object_definition.get('genre') or self.attr('meta.genre')

    def new(self, object_definition={}):
        return (
            'nouvelle ' if self.genre(object_definition) == 'F'
            else 'nouvel ' if self.is_first_letter_vowel(self.label(object_definition))
            else 'nouveau '
        )

    def news(self, object_definition={}):
        return (
            'nouvelles ' if self.genre(object_definition) == 'F'
            else 'nouveaux '
        )

    def label(self, object_definition={}):
        '''
            returns schema label in lowercase
        '''
        label = object_definition.get('label') or self.attr('meta.label')
        return label.lower()

    def labels(self, object_definition={}):
        labels = (
            object_definition.get('labels')
            or self.attr('meta.labels')
            or f'{self.label(object_definition)}s'
        )

        return labels.lower()

    def is_first_letter_vowel(self, string):
        '''
            returns True if unaccented first letter in 'aeiouy'
        '''
        return unaccent(self.label()[0]) in 'aeiouy'

    def article_def(self, object_definition={}):
        '''
            renvoie l'article défini pour le label

            prend en compte:
            - le genre (depuis $meta)
            - si le label commence par une voyelle
            - s'il y a un espace après l'article ou non
        '''
        return (
            "l'" if self.is_first_letter_vowel(self.label(object_definition))
            else 'la ' if self.genre(object_definition) == 'F'
            else 'le '
        )

    def article_undef(self, object_definition={}):
        '''
            renvoie l'article indéfini pour le label

            cf article_def
        '''

        return (
            'une ' if self.genre(object_definition) == 'F'
            else 'un '
        )

    def preposition(self, object_definition={}, check_voyel=True):
        '''
            du, de la, de l'
        '''
        return (
            "de l'" if self.is_first_letter_vowel(self.label(object_definition)) and check_voyel
            else 'de la ' if self.genre(object_definition) == 'F'
            else 'du '
        )

    def le_label(self, object_definition={}):
        '''
        Renvoie le label précédé de l'article défini
        '''
        return f'{self.article_def(object_definition)}{self.label(object_definition)}'

    def un_label(self, object_definition={}):
        '''
        Renvoie le label précédé de l'article indéfini
        '''
        return f'{self.article_undef(object_definition)}{self.label(object_definition)}'

    def un_nouveau_label(self, object_definition={}):
        '''
        Renvoie le label précédé de l'article indéfini et de self.new()
        '''
        return f'{self.article_undef(object_definition)}{self.new(object_definition)}{self.label(object_definition)}'

    def d_un_nouveau_label(self, object_definition={}):
        '''
        Renvoie le label précédé de l'article indéfini et de self.new()
        '''
        return f"d'{self.article_undef(object_definition)}{self.new(object_definition)}{self.label(object_definition)}"

    def du_nouveau_label(self, object_definition={}):
        '''
        Renvoie le label précédé de la préposition et de self.new()
        '''
        return f'{self.preposition(check_voyel=False)}{self.new(object_definition)}{self.label(object_definition)}'

    def des_nouveaux_labels(self, object_definition={}):
        '''
        Renvoie le labels précédé de l'article indéfini et de self.new()
        '''
        return f'des {self.news(object_definition)} {self.labels(object_definition)}'

    def du_label(self, object_definition={}):
        '''
        Renvoie le label précédé de la préposition
        '''
        return f'{self.preposition(object_definition)}{self.label(object_definition)}'

    def les_labels(self, object_definition={}):
        return f'les {self.labels(object_definition)}'

    def des_labels(self, object_definition={}):
        return f'des {self.labels(object_definition)}'

    def description(self, object_definition={}):
        return self.attr('meta.description', f"Schéma '{self.schema_name()}'")
