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
    def config(self):
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

    def columns_table(self, short=False):
        """
            config table pour tabulator : columns
        """

        columns = []

        layout_field = 'table.columns{}'.format('_short' if short else '')
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
                column_def = {'title': relation_def['title'], 'field': key, 'headerFilter': True}
            else:
                column = self.column(key)
                column_def = {'title': column['title'], 'field': key, 'headerFilter': True}

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
            'columns_short': self.columns_table(short=True),
            'sort': self.attr('table.sort', []),
            'url': self.url('/rest/', full_url=True)
        }

    def config_display(self):
        '''
        frontend display (label, etc..)
        '''
        return {
            "label": self.label(),
            "labels": self.labels(),
            "le_label": self.le_label(),
            "les_labels": self.les_labels(),
            "un_label": self.un_label(),
            "des_labels": self.des_labels(),
            "un_nouveau_label": self.un_nouveau_label(),
            "des_nouveaux_labels": self.des_nouveaux_labels(),
            "du_label": self.du_label(),
            "description": self.description(),
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

    def genre(self):
        '''
            returns schema genre
        '''
        return self.attr('meta.genre')

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
        return self.attr('meta.label').lower()

    def labels(self):
        return self.attr('meta.labels', '{}s'.format(self.label()))

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

    def le_label(self):
        '''
        Renvoie le label précédé de l'article défini
        '''
        return '{}{}'.format(self.article_def(), self.label())

    def un_label(self):
        '''
        Renvoie le label précédé de l'article indéfini
        '''
        return '{}{}'.format(self.article_undef(), self.label())

    def un_nouveau_label(self):
        '''
        Renvoie le label précédé de l'article indéfini et de self.new()
        '''
        return '{}{}{}'.format(self.article_undef(), self.new(), self.label())

    def des_nouveaux_labels(self):
        '''
        Renvoie le labels précédé de l'article indéfini et de self.new()
        '''
        return 'des {}{}'.format(self.news(), self.labels())

    def du_label(self):
        '''
        Renvoie le label précédé de la préposition
        '''
        return '{}{}'.format(self.preposition(), self.label())

    def les_labels(self):
        return 'les {}'.format(self.labels())

    def des_labels(self):
        return 'des {}'.format(self.labels())

    def description(self):
        return self.attr('meta.description', "Schéma '{}'".format(self.schema_name()))
