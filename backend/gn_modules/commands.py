"""
    Commandes pour l'administration du module MODULES
"""

import click
from flask.cli import AppGroup, with_appcontext

from .schema import SchemaMethods
from geonature.utils.env import DB

@click.command('test_schema')
@click.option('-m', '--module_code', 'module_code', default='test')
@click.option('-s', '--schema_name', 'schema_name',  default='example')
@with_appcontext
def cmd_test(module_code, schema_name):
    '''
        Commande de test

        TODO :
          - test de validation sur le schema
            - faire un schema de schema ??
              - completer l'existant
          - refléchir au nommage
            - schema, table, class modele
    '''

    '''
        Etape 1
    '''

    print('\n- test schema {}/{} \n'.format(module_code, schema_name))

    print('\n- load schema\n')
    sm = SchemaMethods(module_code, schema_name)


    print('\n- Lister les proprietes\n')
    for key, value in sm.properties(processed_properties_only=True).items():
        print(
            "{} :\t{}\t{}"
            .format(
                key,
                value['type'],
                '(pk)' if value.get('pk_field_name') else '' 
            )
        )

    print(
        '\n- Supprimer la table si elle existe\n\t{}\n'
        .format(sm.sql_drop_table(check_if_exists=True, mode='exec'))
    )

    print(
        '\n- Supprimer le schema s''il existe\n\t{}\n'
        .format(sm.sql_drop_schema(check_if_exists=True, mode='exec'))
    )

    print(
        '\n- Script SQL create schema\n\n{}\n'
        .format(sm.sql_create_schema(mode='exec'))
    )

    print(
        '\n- Script SQL create table\n\n{}\n'
        .format(sm.sql_create_table(mode='exec'))
    )


    # # models
    print('\n- Modeles\n')

    Model = sm.Model()

    # # test requete simple


    # # insert
    sample = sm.sample()
    print('  - insert', sample)
    m = Model(**sample)
    DB.session.add(m)
    DB.session.commit()

    # # update
    print('  - update')
    m.example_name = 'Test 02'
    m.example_code = 'T_02'
    DB.session.commit()
    
    # # get
    print('  - get')
    DB.session.query(Model).filter(Model.example_code == 'T_02').one()
    
    # # delete
    print('  - delete')
    Model.query.filter_by(example_code = 'T_02').delete()
    DB.session.commit()

    # add  lines
    nb = 100
    for i in range(nb):
        m = Model(**{'example_name': "Test {}".format(i), 'example_code': "T_{}".format(i)})
        DB.session.add(m)
    DB.session.commit()

    # # test generic repo

    # # routes TODO

    # # remove table test
    # # print('- Script SQL remove table')
    # # txt_remove_table = remove_table_txt(schema_test)
    # # print(txt_remove_table)
    # # DB.engine.execute(txt_remove_table)

    # # 


    '''
        - 
        - Comment gerer les meta
          - champs $meta
          - schema, table
        - schema de schema ??
        - SQL
          - [] texte
          - [] jouer dans une transaction
        - api rest
        - delete
    '''


    print('\n- test schema {}/{} ok\n'.format(module_code, schema_name))

    return


# liste des commande pour export dans blueprint.py
commands = [
    cmd_test
]