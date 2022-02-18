"""
    MODULES administration commands

    - create_schema : generate schema template
    - sql_schema : generate schema sql
    - test_schema : process tests on a specified schema
"""

from distutils.log import error
import click
import json

from flask.cli import with_appcontext
from flask_marshmallow import Schema
from gn_modules.schema.models import SchemaModel

from .schema import SchemaMethods
from .module import ModuleMethods
from .schema import errors


from sqlalchemy.orm.exc import NoResultFound

# @click.command('schema')
# @click.argument('schema_name')
# @click.option('-p', '--schema_path', default=None, help="chemin vers les elements du schema: '$meta', 'properties[<key>]'")
# @click.option('-v', '--validation', is_flag=True)
# def cmd_schema(schema_name, schema_path=None, validation=False):
#     '''
#         Affiche le schema depuis <schema_name>

#           - par exemple:
#             - schemas.test.example
#     '''
#     schema = SchemaMethods(schema_name).schema(schema_type=('validation' if validation else 'definition'))

#     if schema_path:
#         for p in schema_path.split('.'):
#             schema = schema[p]

#     SchemaMethods.pprint(schema)


@click.command('check')
@click.option('-n', '_schema_name', default=None)
@with_appcontext
def cmd_check(_schema_name=None):
    '''
        list les schemas et affiche si
          - le schéma est valide
          - la table sql existe pour ce schéma
    '''

    for schema_name in filter(lambda n: (not _schema_name) or n == _schema_name, schema_names):

        print('check {}'.format(schema_name))
        sm = SchemaMethods(schema_name)

        error_definition = SchemaMethods.validate_schema(schema_name, sm.definition)
        has_sample = SchemaMethods.file_path(schema_name, 'sample').is_file()

        schema_infos = {
            "schema_name": schema_name,
            "definition_schema_valid": not error_definition,
        }

        schema_infos["error_sample_jsonschema"] = None
        schema_infos['valid_sample_jsonschema'] = False
        schema_infos["error_sample_marshmallow"] = None
        schema_infos['valid_sample_marshmallow'] = False
        schema_infos["has_sample"] = has_sample

        if has_sample:

            schema_infos['error_sample_jsonschema'] = sm.validate_data(SchemaMethods.c_sample(schema_name))
            schema_infos['valid_sample_jsonschema'] = not schema_infos['error_sample_jsonschema']
            m = sm.Model()()
            schema_infos['error_sample_marshmallow'] = sm.unserialize(m, SchemaMethods.c_sample(schema_name))
            schema_infos['valid_sample_marshmallow'] = not schema_infos['error_sample_marshmallow']

            print(schema_infos['valid_sample_marshmallow'], schema_infos['error_sample_marshmallow'])
        for key in schema_infos.keys():
            if key in [
                'schema_name',
                'error_sample_marshmallow',
                'error_sample_jsonschema'
            ]:
                continue
            schema_infos[key] = (
                'o' if schema_infos[key] is True
                else 'x' if schema_infos[key] is False
                else '?'
            )

        txt = '{schema_name:40s} definition: {definition_schema_valid}, '.format(**schema_infos)
        txt += 'sample (json_schema): {valid_sample_jsonschema}, sample (marshmallow): {valid_sample_marshmallow}'.format(**schema_infos)
        print(txt)

        if error_definition:
            print('  - Erreur schema\n', error_definition)

        if schema_infos['error_sample_marshmallow']:
            print('  - Erreur data (marshmallow)\n', schema_infos['error_sample_marshmallow'])

        if schema_infos['error_sample_jsonschema']:
            print('  - Erreur data (jsonschema)\n', schema_infos['error_sample_jsonschema'])

@click.command('sample')
@click.option('-n', '--schema-name', help='nom du schema')
@click.option('-v', '--value', help='value')
@click.option('-f', '--field_name', help='field_name')
@click.option('-w', '--write-file', is_flag=True)
@click.option('-b', '--write-base', is_flag=True)
@with_appcontext
def cmd_sample(schema_name, value=None, field_name=None, write_file=False, write_base=False):
    '''
        print sample for schema_name value (field_name optional)
        if write file -> save in sample file
    '''

    if value:
        # depuis la base
        sample = SchemaMethods.c_get_sample(schema_name, value, field_name)
    else:
        # depuis le fichier xxx-sample.json
        sample = SchemaMethods.c_sample(schema_name)

    if write_base and not value:
        sm = SchemaMethods(schema_name)
        sm.insert_row(sample)

    SchemaMethods.pprint(sample)

    if write_file:
        file_path = SchemaMethods.file_path(schema_name, 'sample')
        print('\nsaved in file {}'.format(file_path))
        with open(file_path, 'w') as f:
            json.dump(
                sample,
                f,
                indent=2,
                sort_keys=True,
                ensure_ascii=False
            )


@click.command('data')
@click.argument('data_file_path', type=click.Path(exists=True))
@with_appcontext
def cmd_process_data(data_file_path):
    '''
        traite le fichier de données renseigné

        {
            schema_name:
            items: [
                {}
            ]
        }
    '''

    infos = {'data': SchemaMethods.process_data(data_file_path) }
    print(SchemaMethods.txt_data_infos(infos))


    # try:
    #     infos = SchemaMethods.process_data_name(data_name)
    #     SchemaMethods.log(SchemaMethods.txt_data_infos(infos))
    #     return True

    # except SchemaDataPathError as e:
    #     SchemaMethods.log('\n{}\n'.format(e))

    # return False


@click.command('explore_data')
@click.argument('schema_name')
@click.option('-a', '--attr-name')
@click.option('-l', '--limit', default=10)
@click.option('-t', '--print-txt', is_flag=True)
@with_appcontext
def cmd_explore_data(schema_name, attr_name=None, limit=10, print_txt=False):
    '''
        explore data for schema

        for each attr of model
            '<attr_name>': <ARRAY_AGG(DISTINCT <attr_name>)>

        - attr-name: choose keys:
            - key1 (one key)
            - key1,key2,key3 (multiple keys separated with commas)
    '''
    sm = SchemaMethods(schema_name)
    txts = []

    for column_key, column_def in sm.columns(sort=True).items():
        if attr_name is not None and column_key not in attr_name.split(','):
            continue
        txt = (
            """SELECT
    '{column_key}' AS field_name,
    (SELECT COUNT(*) FROM {schema_dot_table} WHERE {column_key} IS NOT NULL) AS nb_not_null,
    (SELECT COUNT(*) FROM {schema_dot_table}) AS nb_total,
    (SELECT ARRAY_AGG(DISTINCT {column_key}::varchar)
        FROM (SELECT
            DISTINCT {column_key}
            FROM {schema_dot_table}
            WHERE {column_key} IS NOT NULL LIMIT {limit}
        )a) AS sample
"""
            .format(
                column_key=column_key,
                schema_dot_table=sm.sql_schema_dot_table(),
                limit=limit
            )
        )

        txts.append(txt)

    txt = 'UNION\n'.join(txts)

    if print_txt:
        print(txt)
        return
    res = SchemaMethods.c_sql_exec_txt(txt)

    for r in sorted(res):
        d = {
            'field_name': r[0],
            'label': sm.column(r[0])['label'],
            'nb_not_null': r[1],
            'nb_total': r[2],
            'percent': r[1] / r[2] * 100,
            'sample': ', '.join(r[3] if r[3] else ''),
        }
        print('{field_name} - {label}: {percent:.0f}% (total : {nb_total}, not null : {nb_not_null})'.format(**d))
        if d['sample']:
            print('\n- sample : {sample}\n\n'.format(**d))
        else:
            print('\n')
# @click.command('create_schema')
# @click.option('-n', '--')
# @click.option('-g', '--genre')
# @click.option('-l', '--label')
# @click.option('-w', '--write-file', is_flag=True)
# @click.option('-f', '--force-write-file', is_flag=True)
# def cmd_create_schema(schema_name, label, genre, write_file, force_write_file):
#     '''
#         returns schema template for (schema_name, label, genre)

#         options:
#             -w, --write-file : if True : write file if not exists
#             -f force-write-file : if True : write file even if file exists
#     '''

#     schema_template = SchemaMethods.create_schema(
#         schema_name, label, genre, write_file, force_write_file
#     )
#     if not (write_file or force_write_file):
#         print(schema_template)
#     return True


@click.command('sql_process')
@click.option('-n', '--schema__name', 'schema_name', required=True, help='nom du schema')
@click.option('-e', '--exec-sql', is_flag=True, help='exécute le code sql')
# @click.option('-f', '--force-exec-sql', is_flag=True, help='force l''exécution du code sql (remove table')
@with_appcontext
def cmd_sql_schema(schema_name, exec_sql):
    '''
        Renvoie le code sql pour un schéma
        -e exécute la commandeExécute la commande
    '''

    SchemaMethods.init_schemas()

    sm = SchemaMethods(schema_name)

    exec_sql = exec_sql

    if exec_sql:

        if not sm.sql_schema_exists():
            SchemaMethods.c_sql_exec_txt(sm.sql_txt_process())

    else:
        print('\n{}\n'.format(sm.sql_txt_process()))


@click.command('install')
@click.argument('module_name')
@with_appcontext
def cmd_install_module(module_name):
    """
        enregistre un module en base
    """

    ModuleMethods.install_module(module_name)


@click.command('test')
@with_appcontext
def cmd_test():
    """
        test update schemas
    """

    sm_pf = SchemaMethods('sipaf.pf')
    m = sm_pf.get_row(1)
    out = sm_pf.serialize(
        m,
        fields=[
            'label_communes',
            'label_departements',
            'nb_infrastructures',
            'has_infrastructures',
        ]
    )
    print(out)

    sm_pf = SchemaMethods('sipaf.infrastructure')
    m = sm_pf.get_row(1)
    out = sm_pf.serialize(
        m,
        fields=[
            'nb_passages_faune',
            'has_passages_faune',
        ]
    )
    print(out)



# liste des commande pour export dans blueprint.py
commands = [
    cmd_sql_schema,
    cmd_process_data,
    cmd_sample,
    cmd_check,
    # cmd_schema,
    cmd_explore_data,
    cmd_install_module,
    cmd_test,
]
