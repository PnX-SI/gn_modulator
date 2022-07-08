'''
    SchemaMethods : file (save /load) methods for schemas
'''

from dataclasses import dataclass
from operator import length_hint
from pathlib import Path
import os
import re
import json
import copy
import jsonschema
from ref_geo.utils import get_local_srid
from geonature.utils.env import GN_EXTERNAL_MODULE, db

from geonature.utils.config import config as gn_config
from gn_modules import MODULE_CODE

from . import errors, SchemaBase

GN_MODULES_DIR = GN_EXTERNAL_MODULE / MODULE_CODE.lower()
class SchemaFiles():
    '''
    '''


    @classmethod
    def modules_directory(self):
        return GN_MODULES_DIR

    @classmethod
    def config_directory(self):
        return GN_MODULES_DIR / 'config'

    @classmethod
    def migrations_directory(self):
        return GN_MODULES_DIR / 'backend/gn_modules/migrations'


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
    def load_json_file_from_name(cls, schema_name):

        file_path = cls.schema_path_from_name(schema_name)
        return cls.load_json_file(file_path)

    @classmethod
    def get_key_file_paths(cls, file_path):
        key_file_paths = {}
        file_name = file_path.stem
        for root, dirs, files in os.walk(file_path.parent):
            for file in filter(
                lambda f: (
                    f.suffix == '.json'
                    and f.stem.startswith(file_name)
                    and len(f.stem.split('-')) == 2
                ),
                map(
                    lambda f: Path(f),
                    files
                )
            ):

                key = file.stem.split('-')[1]
                key_file_paths[key] = Path(root) / file

            # on ne fait pas les sous répertoires
            break

        return key_file_paths

    @classmethod
    def load_json_file(cls, file_path, load_keys=False):
        '''
            Read json file and return data

            TODO process error
        '''
        if load_keys:
            data = cls.load_json_file(file_path)
            # get all files

            for key, key_file_path in cls.get_key_file_paths(file_path).items():
                data[key] = cls.load_json_file(key_file_path)

            return data

        try:
            with open(file_path) as f:
                # remove comments ()
                s = ''
                for line in f:
                    if line.strip().startswith('//') or line.strip().startswith('#'):
                        continue
                    s += line

                schema = json.loads(s)
                return schema
        except FileNotFoundError:
            raise errors.SchemaLoadError("File not found : {}".format(file_path))
        except json.JSONDecodeError as e:
            raise errors.SchemaLoadError("Json : error in file {} : {}".format(str(file_path).replace(str(cls.config_directory()), ''), str(e)))

    def load(self):
        '''
            loads schema from file <...>/gn_modules/schemas/<schem_path_from_name>
        '''

        schema_name = self.schema_name()
        definition = self.definition
        if not definition:
            raise errors.SchemaLoadError('pas de definition pour le schema: {}'.format(schema_name))
        # schema_name = definition['meta']['schema_name']

        self.cls.set_schema_cache(schema_name, 'schema', self)

        self.definition = definition

        try:
            self.definition = self.cls.process_defs(self.definition)

        except Exception as e:
            raise Exception('{}: {}'.format(self.schema_name(), e))
        if self.autoschema():
            self.definition = self.get_autoschema()

        if self.attr('meta.extends'):
            base_schema_name = self.attr('meta.extends.schema_name')
            base_schema = self.cls(base_schema_name)
            properties = copy.deepcopy(base_schema.properties())
            properties.update(self.definition.get('properties', {}))

            # la clé primaire du schema de base est à la fois
            #  - une clé primaire du schema
            #  - et une clé étrangère vers le schema de base

            properties[base_schema.pk_field_name()]['foreign_key'] = True
            properties[base_schema.pk_field_name()]["schema_name"] = base_schema_name
            self.definition['properties'] = properties

        self.json_schema = self.get_json_schema()
        self.validation_schema = self.process_validation_schema(copy.deepcopy(self.json_schema))

        return self

    def check_definition_types(self, msg):
        for key in self.definition['properties']:
            if isinstance(self.definition['properties'][key]['type'], list):
                print('error', msg, self.schema_name(), key)
                break

    #################################################
    # methodes en cours
    #################################################

    #################################################
    # methodes non validées
    #################################################

    @classmethod
    def data_path(cls, data_name):
        '''
            retourne le chemin du fichier de données associé à data_name
            data_name:
                - 'test' => <gn_module>/config/data/test.json
                - 'test.exemple' => <gn_module>/config/data/test/exemple.json
            ou du dossier le cas écheant
        '''

        data_path = cls.config_directory() / 'data'

        if not data_name:
            return data_path

        for path_data_name in data_name.split('.'):
            data_path = data_path / path_data_name

        if data_path.is_dir():
            return data_path

        file_path = Path(str(data_path) + '.json')
        if file_path.is_file():
            return file_path

        raise errors.SchemaDataPathError(
            'Le paramètre data_name={}, ne correspond à aucun fichier ou répertoire existant {}(.json)'
            .format(data_name, data_path)
        )

    @classmethod
    def init_references(cls):

        for root, dirs, files in os.walk(cls.config_directory(), followlinks=True):
            for file in filter(
                lambda f: 'references' in root and f.endswith('.json'),
                files
            ):
                file_path = Path(root) / file
                reference = cls.load_json_file(file_path)

                reference_name = file.replace('.json', '')
                cls.check_reference(reference)

                cls.set_global_cache('reference', reference_name, reference)

    @classmethod
    def check_schema_names(cls, schema_name, item, key=None):
        check = True
        if isinstance(item, dict):
            for item_key, item_value in item.items():
                check = cls.check_schema_names(schema_name, item_value, item_key) and check
        if isinstance(item, list):
            for check_item in [cls.check_schema_names(schema_name, item_value) for item_value in item]:
                check = check_item and check
        if key == 'schema_name' and isinstance(item ,str):
            check = item in cls.schema_names_from_cache()
            if not check:
                raise errors.SchemaNameError(
                    "Le schema {schema_name} fait appel au schema {schema_missing} qui n'est pas présent dans les dossiers de configuration"
                    .format(
                        schema_name=schema_name,
                        schema_missing=item
                    )
                )
        return check

    @classmethod
    def get_definition_from_file_path(cls, file_path):
        definition = cls.load_json_file(file_path, load_keys=True)
        definition = cls.process_schema_config(definition)

        try:
            cls.check_definition(definition)
            return definition
        except jsonschema.exceptions.ValidationError as e:
            # import pdb; pdb.set_trace()
            raise errors.SchemaLoadError(
                f"""- {str(file_path).replace(str(cls.config_directory().parent), '')}
  - {' -> '.join(e.absolute_path)}
  - {str(e)}"""
            )

    @classmethod
    def init_definitions(cls):

        for root, dirs, files in os.walk(cls.config_directory(), followlinks=True):
            for file in filter(
                lambda f: 'definitions' in root and f.endswith('.json') and '-' not in f,
                files
            ):
                definition = cls.get_definition_from_file_path(Path(root) / file)
                schema_name = definition['meta']['schema_name']
                cls.set_schema_cache(schema_name, 'definition', definition)

        # check schema_name s in properties
        check_schema_names = True
        for schema_name, definition in cls.get_schema_cache('*', 'definition').items():
            check_schema_names= cls.check_schema_names(schema_name, definition) and check_schema_names

        return check_schema_names

    @classmethod
    def process_backrefs(cls):
        '''
            ajout des definition des relation avec backref dans le schema correspondant
        '''
        for schema_name in cls.schema_names_from_cache():
            sm = cls(schema_name)

            for relation_key, relation_def in sm.relationships().items():
                if not relation_def.get('backref'):
                    continue
                opposite = sm.opposite_relation_def(relation_def)
                rel = cls(relation_def['schema_name'])
                rel_properties = rel.attr('properties')
                if not rel_properties.get(relation_def['backref']):
                    rel_properties[relation_def['backref']] = opposite

    @classmethod
    def process_complement(cls):
        for schema_name in cls.schema_names_from_cache():
            sm = cls(schema_name)
            if not sm.attr('meta.schema_complement'):
                continue

            # lister les complements
            s_complement = cls(sm.attr('meta.schema_complement'))

            if not s_complement.sql_table_exists():
                continue
            s_complement.Model()

            s_complement.MarshmallowSchema()
            query, _ = s_complement.get_list()
            for complement in query.all():
                sm.definition['properties'][complement.relation_name] = {
                    "type": "relation",
                    "relation_type": "1-1",
                    "local_key": sm.pk_field_name(),
                    "schema_name": complement.schema_name,
                    "title": complement.complement_name,
                    "description": complement.complement_desc
                }

                sm.definition['properties'][f'has_{complement.relation_name}'] = {
                    "type": "boolean",
                    "column_property": "has",
                    "title": f"Est de type {complement.complement_name}?",
                    "relation_key": complement.relation_name
                }


    @classmethod
    def init_schemas(cls):
        cls.clear_global_cache()
        cls.clear_schema_cache()
        cls.init_references()
        cls.init_definitions()

        cls.process_backrefs()

        # init complement ??
        # ici on ajoute les relations dans les definitions
        cls.process_complement()

        # init models
        for schema_name in cls.schema_names_from_cache():
            sm = cls(schema_name)
            try:
                sm.Model()
            except AttributeError as e:
                raise errors.SchemaError(
                    '{}: {}'.format(sm.schema_name(), e))



        for schema_name in cls.schema_names_from_cache():
            sm = cls(schema_name)
            sm.MarshmallowSchema()


    @classmethod
    def process_schema_config(cls, data, key=None):
        '''
            transforme les element commençant par '__CONFIG.' et terminant par '__' par leur valeur correspondante dans
            app.config

            par exemple __CONFIG.LOCAL_SRID__ => 2154
        '''


        # patch local srid config
        gn_config['LOCAL_SRID'] = get_local_srid(db.engine)

        if not hasattr(cls, '_re_CONFIG'):
            setattr(cls, '_re_CONFIG', re.compile(r'__CONFIG\.(.*?)__'))

        # process dict

        if type(data) is dict:
            return {
                k: cls.process_schema_config(v, k)
                for k, v in data.items()
            }

        # process list
        if type(data) is list:
            return [cls.process_schema_config(v) for v in data]

        # process text

        if type(data) is str and '__CONFIG.' in data:
            config_key_str = cls._re_CONFIG.search(data)
            config_key_str = config_key_str and config_key_str.group(1)
            config_key_replace_str = f'__CONFIG.{config_key_str}__'
            if not config_key_str:
                return data

            config_keys = config_key_str.split('.')
            config_value = gn_config
            try:
                for config_key in config_keys:
                    config_value = config_value[config_key]
            except Exception:
                raise errors.SchemaProcessConfigError("La clé {} n'est pas dans la config de geonature".format(config_key_str))

            data = data.replace(config_key_replace_str, str(config_value) or '')

            if key == 'srid':
                data = int(data)

        return data

    @classmethod
    def process_defs(cls, elem, _defs={}):

        if isinstance(elem, dict):
            if '_defs' in elem:
                _defs_new = copy.deepcopy(_defs)
                _defs_new.update(elem['_defs'])
            else:
                _defs_new = _defs
            for key, value in elem.items():
                if key == '_defs':
                    continue
                val = cls.process_defs(value, _defs_new)
                if val is not None:
                    elem[key] = val

            if '__value' in elem:
                return elem['__value']
            return elem

        if isinstance(elem, list):
            elem_out = []
            for item in elem:
                val = cls.process_defs(item, _defs)
                if val:
                    elem_out.append(val)
            return elem_out

        if elem in _defs:
            return cls.process_defs(_defs[elem], _defs)

        if str(elem).startswith('_') and not str(elem).startswith('__f__'):
            raise Exception(
                'Un elément commençant par "_" est présent dans les fichiers de config {}'
                .format(elem)
            )

        return elem

    @classmethod
    def get_layouts(cls):
        '''
            renvoie la liste des layouts
        '''

        layouts = []
        for root, dirs, files in os.walk(cls.config_directory() / 'layout', followlinks=True):
            for file in filter(
                lambda f: f.endswith('.json'),
                files
            ):
                file_path = Path(root) / file
                layout = cls.load_json_file(file_path)
                layout['layout_name'] = layout.get('layout_name', file_path.name)
                layout = cls.process_defs(layout)
                if '_defs' in layout:
                    del layout['_defs']
                layouts.append(layout)

        return layouts