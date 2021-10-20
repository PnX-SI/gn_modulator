'''
    SchemaMethods : file (save /load) methods for schemas
'''

from pathlib import Path
import json
import re

import string
import random
from geonature.utils.env import GN_EXTERNAL_MODULE
from geonature.utils.config import config

from gn_modules import MODULE_CODE

from .errors import (
    SchemaValidationError,
    SchemaLoadError,
    SchemaProcessConfigError
)

GN_MODULES_SCHEMAS_DIR = GN_EXTERNAL_MODULE / MODULE_CODE.lower() / 'config/schemas/'

class SchemaFiles():
    '''
        file_path load save
    '''

    def schema_file_path(self, group_name=None, object_name=None, post_name=""):
        return self.cls_schema_file_path(
            group_name or self.group_name(),
            object_name or self.object_name(),
            post_name
        )

    def schemas_dir(self):
        return GN_MODULES_SCHEMAS_DIR

    @classmethod
    def cls_schema_file_path(cls, group_name=None, object_name=None, post_name=""):
        '''
            returns schema file_path <GN_MODULES_SCHEMAS_DIR>/<group_name>/<object_name>
        '''
        return (
            Path(
                GN_MODULES_SCHEMAS_DIR / '{}/{}{}.json'
                .format(
                    group_name,
                    object_name,
                    post_name
                )
            )
        )

    # load / save

    def load_from_file(self, file_path):
        '''
        loads schema from file
        '''
        self._schema = self.load_json_file(file_path)
        return self

    def sample(self):
        return self.load_json_file(
            self.schema_file_path(post_name='-sample')
        )

    def random_sample(self):
        '''
            return random data for schema (test purpose)
        '''
        rand_sample = {}
        random.seed()
        for k,v in self.properties(processed_properties_only=True).items():
            p_type = v['type']
            if v.get('primary_key'):
                continue
            if v.get('foreign_key'):
                rand_sample[k] = random.randint(10, 99)
                continue
            if p_type == 'integer':
                rand_sample[k] = random.randint(0, 1e6)
            if p_type == 'text':
                rand_sample[k] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

        return rand_sample

    def load_json_file(self, file_path):
        '''
            load json file
            return dict
        '''
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # on remplace les valeurs commençant par __CONFIG. par les valeur de la config de l'appli
                # par exemple pour LOCAL_SRID pour les geometries
                data = self.process_schema_config(data)
                return data
        except FileNotFoundError as e:
            raise SchemaLoadError("File not found : {}".format(file_path))
        except json.JSONDecodeError as e:
            raise SchemaLoadError(
                "Json : error in file {} : {}"
                .format(file_path, str(e))
            )

    def process_schema_config(self, data):
        if type(data) is dict:
            return {
                k: self.process_schema_config(v)
                for k,v in data.items()
            }

        if type(data) is list:
            return [ self.process_schema_config(v)  for v in data]

        if type(data) is str and '__CONFIG.' in data:
            config_key_str = re.search(r'__CONFIG\.(.*?)__', data)
            config_key_str = config_key_str and config_key_str.group(1)
            if config_key_str:
                config_keys = config_key_str.split('.')
                config_value = None
                try:
                    for config_key in config_keys:
                        config_value = config[config_key]
                except Exception as e:
                    raise SchemaProcessConfigError("La clé {} n'est pas dans la config de geonature".format(config_key_str))

                return data.replace(data, str(config_value) or '')

        return data

    def reload(self):
        '''
            reload_schema
        '''
        # reninit model
        self.clear_cache_model()
        self.clear_cache_marshmallow()
        # reinit
        return self.load()


    def load(self, group_name=None, object_name=None):
        '''
            loads schema from file <...>/gn_modules/schemas/<group_name>/<object_name>
        '''

        return self.load_from_file(
            self.schema_file_path(
                group_name or self.group_name(),
                object_name or self.object_name()
            )
        )

    def load_from_reference(self, ref):
        '''
            load from ref '../<group_name>/<object_name>'
        '''


        ref_array = ref.replace('.json', '').split('/')

        group_name = ref_array[-2]
        object_name = ref_array[-1]

        return self.load(group_name, object_name)

    def save(self, file_path):
        '''
            save schema in file given by file_path

            TODO add test if file exists ? option force ??
        '''
        with open(file_path, 'w') as f:
            json.dump(self._schema, f)

    def save(self):
        '''
            save schema in file given by self.file_path()

        '''
        return self.save(self.schema_file_path())