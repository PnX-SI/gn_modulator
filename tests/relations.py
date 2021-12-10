'''
    test sur les realtions

    d'abord sur les schemas test child et parent

    puis sur l'ensemble
'''


import pytest

from gn_modules.schema import SchemaMethods

from . import app, temporary_transaction  # noqa


class TestSchemas:
    def test_raw_schema(self):
        '''
            test si les schemas raw sont valides
        '''

        schema_names = ['schemas.test.child', 'schemas.test.parent']

        for schema_name in schema_names:
            print('raw', schema_name)
            sm = SchemaMethods(schema_name)

            error = sm.validate_raw_schema()

            if error:
                print(error)
            assert(error is None)

    def test_processed_schema(self):
        '''
            test sur les schemas processed
        '''

        schema_names = ['schemas.test.child', 'schemas.test.parent']

        for schema_name in schema_names:
            sm = SchemaMethods(schema_name)

            processed_schema = sm.schema('validation')

            for key, relation_def in sm.relationships().items():

                if sm.relation_type(relation_def) == 'n-1':
                    print('n_1', schema_name, key, relation_def)
                    assert ('object' == processed_schema["properties"][key]["type"])

                if sm.relation_type(relation_def) == '1-n':

                    print('1_n', schema_name, key, relation_def)

                    print(key, relation_def, '1n')
                    assert ('array' == processed_schema["properties"][key]["type"])

                if sm.relation_type(relation_def) == 'n-n':
                    print('n_n', schema_name, key, relation_def)
                    assert ('array' == processed_schema["properties"][key]["type"])

    @pytest.mark.usefixtures("client_class", "temporary_transaction")
    def test_chainage_parent_child(self):
        '''
            test sql, model, repo, serializer
        '''

        # sql

        smChild = SchemaMethods('schemas.test.child')
        smExample = SchemaMethods('schemas.test.example')
        smParent = SchemaMethods('schemas.test.parent')

        drop_schema_txt = 'DROP SCHEMA IF EXISTS {} CASCADE;'.format(smChild.sql_schema_name())
        SchemaMethods.c_sql_exec_txt(drop_schema_txt)
        assert(smChild.sql_schema_exists() is False)

        txt = smChild.sql_txt_process()
        SchemaMethods.c_sql_exec_txt(txt)
        assert(smChild.sql_table_exists() is True)
        assert(smParent.sql_table_exists() is True)
        assert(smExample.sql_table_exists() is True)

        # test Model

        # test
        # create one parent

        data_example = [
            {'example_code': 'E1', 'example_name': 'Ex 1'},
            {'example_code': 'E2', 'example_name': 'Ex 2'}
        ]

        data_children = [
            {'child_code': 'BN', 'child_name': 'Ben', 'examples': data_example},
            {'child_code': 'FR', 'child_name': 'François'}
        ]

        data_parent = {'parent_code': 'RL', 'parent_name': 'Roland', 'children': data_children}

        # assert (True is False)

        mParent = smParent.insert_row(data_parent)

        mParent_data = smParent.serialize(mParent)
        assert (mParent_data['parent_name'] == data_parent['parent_name'])
        assert (len(mParent_data['children']) == 2)

        mChild = smChild.get_row('BN', 'child_code')
        mChild_data = smChild.serialize(mChild)
        assert (type(mChild_data['parent']) is dict)
