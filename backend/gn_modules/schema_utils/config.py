'''
    SchemaMethods : config processing
    - schema
    - display
    - util
'''

from gn_modules.utils import unaccent

class SchemaConfig():
    '''
    config used by frontend
    '''

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
            "undef_labels": self.undef_label(),
            "description": self.description(),
        }

    def config_utils(self):
        '''
        frontend processing
        '''

        return {
            'properties_array': self.properties_array(processed_properties_only=True),
            'urls': {
                'rest': self.url(pre_url='rest', post_url='s/', full_url=True)
            },
            'pk_field_name': self.pk_field_name(),
            'model_name': self.model_name(),
            'full_name': self.full_name(),
            'sql_schema_name': self.sql_schema_name(),
            'sql_table_name': self.sql_table_name(),
        }

    def config(self):
        '''
        frontend config 
        '''
        return {
            'schema': self.schema(),
            'display': self.config_display(),
            'utils': self.config_utils()
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
            returns true if unaccented first letter in 'aeiouy'
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
        return self._schema['$meta'].get('description', "Schéma '{}' pour le module '{}'".format(self.schema_name(), self.module_code()))
