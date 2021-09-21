'''
    SchemaMethods : file (save /load) methods for schemas
'''

from pathlib import Path
import json

from geonature.utils.env import GN_EXTERNAL_MODULE

from gn_modules import MODULE_CODE

from .errors import (
    SchemaValidationError,
    SchemaLoadError
)

GN_MODULES_SCHEMAS_DIR = GN_EXTERNAL_MODULE / MODULE_CODE.lower() / 'config/schemas/'

class SchemaFiles():
    '''
        file_path load save
    '''

    def schema_file_path(self, module_code=None, schema_name=None, post_name=""):
        '''
            returns schema file_path <GN_MODULES_SCHEMAS_DIR>/<module_code>/<schema_name>
        '''
        return (
            Path(
                GN_MODULES_SCHEMAS_DIR / '{}/{}{}.json'
                .format(
                    module_code or self.module_code(),
                    schema_name or self.schema_name(),
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
        return self._schema

    def sample(self):
        return self.load_json_file(
            self.schema_file_path(post_name='-sample')
        )

    def load_json_file(self, file_path):
        '''
            load json file
            return dict
        '''
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError as e:
            raise SchemaLoadError("File not found : {}".format(file_path))
        except json.JSONDecodeError as e: 
            raise SchemaLoadError(
                "Json : error in file {} : {}"
                .format(file_path, str(e))
            )
        
    def load(self, module_code, schema_name):
        '''
            loads schema from file <...>/gn_modules/schemas/<module_code>/<schema_name>
        '''
        return self.load_from_file(self.schema_file_path(module_code, schema_name))

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