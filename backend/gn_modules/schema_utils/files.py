'''
    SchemaMethods : file (save /load) methods for schemas
'''

from pathlib import Path
import os
import json
import copy
from geonature.utils.env import GN_EXTERNAL_MODULE

from gn_modules import MODULE_CODE

from .errors import (
    SchemaLoadError,
    SchemaDataPathError
)

GN_MODULES_CONFIG_DIR = GN_EXTERNAL_MODULE / MODULE_CODE.lower() / 'config/'


class SchemaFiles():
    '''
        - config_directory          [classmethod]
        - schema_name_from_path     [classmethod] : schema_path -> schema_name
        - schema_path_from_name     [classmethod] : schema_name -> schema_path
        - schema_names              [classmethod] : list all schemas in a directory
        - load_json_file            [classmethod] : file_path -> data from json file

    '''

    @classmethod
    def config_directory(self):
        return GN_MODULES_CONFIG_DIR

    @classmethod
    def schema_name_from_path(cls, schema_path):
        '''
            Renvoie name à partir de schema_path et base_dir
        '''
        base_dir = cls.config_directory()

        # on retire base_dir
        schema_path_short = str(schema_path).replace(str(base_dir), '')

        # on retire le '/' du début s'il existe
        if schema_path_short[0] == '/':
            schema_path_short = schema_path_short[1:]

        # on retire .json
        schema_path_short = schema_path_short.replace('.json', '')

        schema_name = ".".join(schema_path_short.split('/'))

        return schema_name

    @classmethod
    def schema_path_from_name(cls, schema_name):
        '''
            Renvoie le chemin d'un schema à partir de son nom
        '''
        base_dir = cls.config_directory()
        schema_path = base_dir / (
            "{}.json"
            .format(
                "/".join(schema_name.split("."))
            )
        )

        return schema_path

    @classmethod
    def schema_names(cls, base_name=None):
        '''
            Retourne tous les nom de schémas d'un repertoire
        '''

        schema_names = []
        search_dir = cls.config_directory()

        if (search_dir / Path("/".join(base_name.split('.')) + '.json')).is_file():
            return [base_name]

        if base_name:
            search_dir = search_dir / "/".join(base_name.split('.'))
        for root, dirs, files in os.walk(search_dir, followlinks=True):
            for f in filter(
                lambda f: f.endswith('.json') and '-' not in f,
                files
            ):
                schema_names.append(cls.schema_name_from_path(Path(root) / f))
        return schema_names

    @classmethod
    def load_json_file_from_name(cls, schema_name):
        '''
            load json file from name
        '''

        file_path = cls.schema_path_from_name(schema_name)
        return cls.load_json_file_from_path(file_path)

    @classmethod
    def file_path(cls, schema_name, post_name=None):
        file_path = cls.schema_path_from_name(schema_name)
        if post_name:
            file_path = Path(str(file_path).replace('.json', '-{}.json'.format(post_name)))
        return file_path

    @classmethod
    def c_sample(cls, schema_name):
        try:
            return cls.load_json_file_from_path(cls.file_path(schema_name, 'sample'))
        except Exception as e:
            print(e)
        return None

    @classmethod
    def load_json_file_from_path(cls, file_path):
        '''
            Read json file and return data

            TODO process error
        '''
        try:
            with open(file_path) as f:
                # remove comments ()
                s = ''
                for line in f:
                    if line.strip().startswith('//') or line.strip().startswith('#'):
                        continue
                    s += line

                schema = json.loads(s)
                schema = cls.process_schema_config(schema)
                return schema
        except FileNotFoundError:
            raise SchemaLoadError("File not found : {}".format(file_path))
        except json.JSONDecodeError as e:
            raise SchemaLoadError("Json : error in file {} : {}".format(str(file_path).replace(str(cls.config_directory()), ''), str(e)))

    def load(self, schema_name):
        '''
            loads schema from file <...>/gn_modules/schemas/<schem_path_from_name>
        '''

        self._schema_name = schema_name
        self._schemas = {}
        self._schemas['definition'] = self.cls().load_json_file_from_name(schema_name)

        if self.meta('extends'):
            base_schema_name = self.meta('extends.schema_name')
            base_schema = self.cls()(base_schema_name)
            properties = copy.deepcopy(base_schema.properties())
            properties.update(self._schemas['definition'].get('properties', {}))

            # la clé primaire du schema de base est à la fois
            #  - une clé primaire du schema
            #  - et une clé étrangère vers le schema de base

            properties[base_schema.pk_field_name()]['foreign_key'] = True
            properties[base_schema.pk_field_name()]["schema_name"] = base_schema_name
            self._schemas['definition']['properties'] = properties

        if self.autoschema():
            self._schemas['definition'] = self.get_autoschema()
        self._schemas['validation'] = self.process_definition_schema(True)
        self._schemas['form'] = self.process_definition_schema(False)

        return self

    #################################################
    # methodes en cours
    #################################################

    #################################################
    # methodes non validées
    #################################################

    @classmethod
    def data_path(self, data_name):
        '''
            retourne le chemin du fichier de données associé à data_name
            data_name:
                - 'test' => <gn_module>/config/data/test.json
                - 'test.exemple' => <gn_module>/config/data/test/exemple.json
            ou du dossier le cas écheant
        '''

        data_path = self.config_directory() / 'data'

        if not data_name:
            return data_path

        for path_data_name in data_name.split('.'):
            data_path = data_path / path_data_name

        if data_path.is_dir():
            return data_path

        file_path = Path(str(data_path) + '.json')
        if file_path.is_file():
            return file_path

        raise SchemaDataPathError(
            'Le paramètre data_name={}, ne correspond à aucun fichier ou répertoire existant {}(.json)'
            .format(data_name, data_path)
        )
        return False

    def reload(self):
        '''
            reload_schema
        '''
        # reninit model
        self.clear_cache_model()
        self.clear_cache_marshmallow()
        # reinit
        return self.load(self._schema_name)
