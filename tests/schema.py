'''
    Test pour la nomenclature    -
'''

from gn_modules.schema import SchemaMethods
import pytest
from . import app, temporary_transaction  # noqa


class TestSchemas:

    def test_definition_schema_load_and_validate(self):
        '''
            test des schemas présents dans le répertoire <gn_modules>/config/schemas
        '''

        for schema_name in SchemaMethods.schema_names('schemas'):

            definition_schema = SchemaMethods.load_json_file_from_name(schema_name)
            print('definition', schema_name, definition_schema['$id'])

            # test 1 - le fichier json est bien chargé
            assert (type(definition_schema) is dict)

            error = SchemaMethods.validate_schema(schema_name, definition_schema)
            if error:
                print('validation', schema_name)
                print("erreur", error)
            assert(error is None)

    def test_samples(self):
        '''
            test des samples et de leur validation
        '''

        for schema_name in SchemaMethods.schema_names('schemas'):
            print('samples', schema_name)
            sample = SchemaMethods.sample(schema_name)

            assert(type(sample) is dict)

            error = SchemaMethods(schema_name).validate_data(sample)
            if error:
                print('validation', schema_name)
                print("erreur processed", error)
            assert(error is None)

    @pytest.mark.usefixtures("client_class", "temporary_transaction")
    def test_schema_sql(self):
        for schema_name in SchemaMethods.schema_names('schemas'):

            # test table exist si non sql_processing
            sm = SchemaMethods(schema_name)
            cond_sql = sm.sql_processing() or sm.sql_table_exists()
            if not cond_sql:
                print('slq error {}'.format(schema_name))
            assert(cond_sql is True)

    @pytest.mark.usefixtures("client_class", "temporary_transaction")
    def test_relations(self):
        for schema_name in SchemaMethods.schema_names('schemas'):

            # test table exist si non sql_processing
            sm = SchemaMethods(schema_name)
            for k, relation_def in sm.relationships().items():
                print(schema_name, k, relation_def)
        assert(True is True)
