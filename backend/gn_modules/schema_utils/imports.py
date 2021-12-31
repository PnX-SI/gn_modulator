'''
    SchemaData methode pour gerer les données depuis des fichiers.json
    par exemple la nomenclature
'''

import os
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from .errors import SchemaDataTypeError

class SchemaImports:

    @classmethod
    def load_and_validate_data(cls, data_file_path):
        '''
            - charge des données depuis un fichier json
            - recupère le schéma associé depuis schema_name
            - valide la donnée par raport au schema
            - retourne la données
        '''

        # lecture des fichiers data et schema

        # data_path = cls.data_path(data_name) / '{}.json'.format(data_name)
        # if data_path.is_dir():
        #     for root, dirs, files in os.walk(data_path, followlinks=True):
        #         for f in files:
        #             if f.endswith('.json'):
        #                 cls.load_and_validate_data

        data = cls.load_json_file_from_path(data_file_path)

        schema = cls.load_json_file_from_name('references.data')

        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            print(e)
            return

        return data

    @classmethod
    def data_file_sub_path(cls, data_file_path):
        return str(data_file_path).replace(str(cls.config_directory() / 'data') + '/', '')

    @classmethod
    def process_data_name(cls, data_name=None):
        '''
        '''

        infos = {}

        for schema_name in filter(lambda n: n.startswith('data.'), cls.schema_names(data_name)):
            infos[schema_name] = cls.process_data(schema_name)

        return infos

    @classmethod
    def process_data(cls, schema_name):
        '''
        '''

        if not schema_name.startswith('data.'):
            return

        data_file_path = cls.schema_path_from_name(schema_name)
        data = cls.load_and_validate_data(data_file_path)

        infos = []

        for data_item in data:

            info = cls.process_data_item(data_item)

            infos.append({
                'file_path': str(data_file_path),
                'schema_name': data_item['schema_name'],
                'updates': info['updates'],
                'inserts': info['inserts'],
                'items': data_item['items'],
            })

        return infos

    def pre_process_data(self, d):
        for key_process, keys in self.meta('import.get_foreign_key', {}).items():
            sm_rel = self.cls()(self.column(key_process)['schema_name'])
            rel_test_keys = sm_rel.meta('import.test_keys')
            rel_test_values = [d[test_key] for test_key in keys]
            m = sm_rel.get_row(rel_test_values, rel_test_keys)
            d[key_process] = getattr(m, key_process)

            for key in keys:
                if key not in self.columns():
                    d.pop(key)

        for key, keys in self.meta('import.copy', {}).items():
            for k in keys:
                d[k] = d.get(k, d[key])
            if key not in self.columns():
                d.pop(key)

    @classmethod
    def process_data_item(cls, data_item):

        schema_name = data_item['schema_name']
        sm = cls(schema_name)

        updates = []
        inserts = []

        test_keys = sm.meta('import.test_keys')

        for d in data_item['items']:

            # validate_data

            # pre traitement
            sm.pre_process_data(d)
            values = [d[key] for key in test_keys]

            # pour visualiser quel ligne est insérée / modifiée
            value = ', '.join([str(value) for value in values])

            # on tente un update
            try:
                _, b_update = sm.update_row(
                    values,
                    d,
                    test_keys
                )
                if b_update:
                    updates.append(value)

            # si erreur NoResultFound -> on tente un insert
            except NoResultFound:
                sm.insert_row(d)
                inserts.append(value)

        return {'updates': updates, 'inserts': inserts}


    @classmethod
    def process_data_jdd(cls, elements):

        updates = []
        inserts = []
        test_keys = ['dataset_name']

        sm = cls('schemas.utils.jdd')

        for d in elements:
            id_acquisition_framework = cls('schemas.utils.ca').get_row(
                d['acquisition_framework_name'],
                'acquisition_framework_name',
            ).id_acquisition_framework

            full_data = d
            full_data['id_acquisition_framework'] = id_acquisition_framework
            values = [full_data[key] for key in test_keys]
            full_data.pop('acquisition_framework_name')
            value = ', '.join(values)

            try:
                _, b_update = sm.update_row(
                    values,
                    full_data,
                    test_keys
                )
                if b_update:
                    updates.append(value)

            except NoResultFound:
                sm.insert_row(full_data)
                inserts.append(value)

        return {'updates': updates, 'inserts': inserts}

    @classmethod
    def process_data_ca(cls, elements):
        updates = []
        test_keys = ['acquisition_framework_name']

        inserts = []
        sm = cls('schemas.utils.ca')

        for d in elements:

            full_data = d
            values = [full_data[key] for key in test_keys]
            value = ', '.join(values)
            try:
                _, b_update = sm.update_row(
                    values,
                    full_data,
                    test_keys
                )
                if b_update:
                    updates.append(value)

            except NoResultFound:
                sm.insert_row(full_data)
                inserts.append(value)

        return {'updates': updates, 'inserts': inserts}


    @classmethod
    def process_data_nomenclature_type(cls, elements):

        data_type = 'nomenclature_type'
        updates = []
        inserts = []
        sNomenclatureType = cls('schemas.utils.nomenclature_type')

        for d in elements:
            # donnée au format nomenclature_type
            full_data = {
                'mnemonique': d['mnemonique'],
                'label_default': d['label'],
                'label_fr': d['label'],
                'definition_default': d['definition'],
                'definition_fr': d['definition'],
                'source': d['source'],
            }
            key = 'mnemonique'
            value = full_data[key]

            try:
                _, b_update = sNomenclatureType.update_row(
                    value,
                    full_data,
                    key
                )
                if b_update:
                    updates.append(value)

            except NoResultFound:
                sNomenclatureType.insert_row(full_data)
                inserts.append(value)

        return {'updates': updates, 'inserts': inserts}

    @classmethod
    def process_data_nomenclature(cls, elements):
        # nomenclatures

        data_type = 'nomenclature'
        updates = []
        inserts = []
        sNomenclature = cls('schemas.utils.nomenclature')
        sNomenclatureType = cls('schemas.utils.nomenclature_type')

        for d in elements:
            # donnée au format nomenclature_type
            id_type = (
                sNomenclatureType
                .get_row(d['type'], field_name='mnemonique')
                .id_type
            )

            full_data = {
                'cd_nomenclature': d['cd_nomenclature'],
                'mnemonique': d['mnemonique'],
                'label_default': d['label'],
                'label_fr': d['label'],
                'definition_default': d['definition'],
                'definition_fr': d['definition'],
                'source': d['source'],
                'type': {
                    'id_type': id_type,
                    'mnemonique': d['type']
                },
                'id_type': id_type,
                'active': True
            }

            field_names = ['type.mnemonique', 'cd_nomenclature']
            values = [d['type'], d['cd_nomenclature']]

            try:
                _, b_update = sNomenclature.update_row(
                    values,
                    full_data,
                    field_names
                )

                if b_update:
                    updates.append(values)

            except NoResultFound:
                sNomenclature.insert_row(full_data)
                inserts.append(values)

        return {'updates': updates, 'inserts': inserts}

    @classmethod
    def log_data_info_detail(cls, info, info_type):
        '''
            affichage du detail pour insert ou update
            un peu compliqué
        '''
        items = info[info_type]
        nb = len(items)

        if items and type(items[0]) is list:
            list_first_key = list(dict.fromkeys([elem[0] for elem in items]))
            items_new = []
            for elem_first_key in list_first_key:
                list_second_key = [elem[1] for elem in filter(lambda e: e[0] == elem_first_key, items)]
                elem_new = '{}.({})'.format(
                    elem_first_key,
                    ', '.join(list_second_key)
                )
                items_new.append(elem_new)
            items = items_new

        # detail = '\n  - {}  ({})'.format(info_type, nb)
        detail = ''

        if nb:
            tab = '      - '
            detail += '{}{}'.format(
                tab,
                ('\n' + tab).join(items)
            )
            detail += '\n'
        return detail

        # return '\n    - '.join(['' + '.'.join(elem) if type(elem) is list else elem for elem in info[info_type]])

    @classmethod
    def txt_data_info(cls, info):
        txt = ''
        detail_updates = cls.log_data_info_detail(info, 'updates')
        detail_inserts = cls.log_data_info_detail(info, 'inserts')
        txt += '  - {schema_name}\n'.format(schema_name=info['schema_name'])
        txt += '    - items ({})\n'.format(len(info['items']))
        txt += '    - updates ({})\n'.format(len(info['updates']))
        txt += '{}'.format(detail_updates)
        txt += '    - inserts ({})\n'.format(len(info['inserts']))
        txt += '{}'.format(detail_inserts)

        return txt

    @classmethod
    def txt_data_infos(cls, infos_file):
        txt_list = []
        for schema_name, info_file_value in infos_file.items():
            txt = '- {} - nb_type ({})\n'.format(schema_name, len(info_file_value))
            for info in info_file_value:
                txt += '\n{}'.format(cls.txt_data_info(info))
            txt_list.append(txt)
        return '\n\n'.join(txt_list)
