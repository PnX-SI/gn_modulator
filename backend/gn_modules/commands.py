"""
    module MODULES administration commands

    - create_schema : generate schema template
    - sql_schema : generate schema sql
    - test_schema : process tests on a specified schema
"""

import click
import json
import time

from flask.cli import AppGroup, with_appcontext

from geonature.utils.env import DB, MA

from .schema import SchemaMethods


@click.command('create_schema')
@click.option('-g', '--group_name', help='code du module')
@click.option('-o', '--object_namename')
@click.option('-g', '--genre')
@click.option('-l', '--label')
@click.option('-w', '--write-file', is_flag=True)
@click.option('-f', '--force-write-file', is_flag=True)
def cmd_create_schema(group_name, object_name, label, genre, write_file, force_write_file):
    '''
        returns schema template for (group_name, object_name, label, genre)

        options:
            -w, --write-file : if True : write file if not exists
            -f force-write-file : if True : write file even if file exists
    '''

    schema_template = SchemaMethods.create_schema(
        group_name, object_name, label, genre, write_file, force_write_file
    )
    if not (write_file or force_write_file):
        print(schema_template)
    return True


@click.command('sql_schema')
@click.option('-g', '--group_name', 'group_name', required=True, help='code du module')
@click.option('-o', '--object_name', 'object_name', required=True, help='nom du schema')
@click.option('-e', '--exec-sql', is_flag=True, help='exécute le code sql')
@click.option('-f', '--force-exec-sql', is_flag=True, help='force l''exécution du code sql (remove table')
@with_appcontext
def cmd_sql_schema(group_name, object_name, exec_sql, force_exec_sql):
    '''
        Renvoie le code sql pour un schéma
        -e exécute la commandeExécute la commande
    '''

    sm = SchemaMethods(group_name, object_name)

    exec_sql = exec_sql or force_exec_sql

    if exec_sql:

        if not sm.sql_schema_exists():
            sm.sql_exec_txt(sm.sql_txt_create_schema())

        if sm.sql_table_exists():
            if force_exec_sql:
                print('\nSQL - exec : remove table {}'.format(sm.sql_schema_dot_table()))
                sm.sql_exec_txt(sm.sql_txt_drop_table())
            else:
                print(
                    '\nSQL - exec : table {} exists\n\n  - option -f to remove and recreate table\n'
                    .format(sm.sql_schema_dot_table()))
                return
        else:
            print('\nSQL - exec : Create Table {}\n'.format(sm.sql_schema_dot_table()))
            sm.sql_exec_txt(sm.sql_txt_create_table())

    print('\n{}\n'.format(sm.sql_txt_create_table()))


@click.command('test_schema')
@click.option('-g', '--group_name', 'group_name', default='test')
@click.option('-o', '--object_name', 'object_name',  default='example')
@with_appcontext
def cmd_test(group_name, object_name):
    '''
        Commande de test sur un schema
    '''

    print('\n- test schema {}/{} \n'.format(group_name, object_name))

    print('\n- load schema\n')
    sm = SchemaMethods(group_name, object_name)


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

    if sm.sql_table_exists():
        sm.sql_exec_txt(sm.sql_txt_drop_table())

    if not sm.sql_schema_exists():
        sm.sql_exec_txt(sm.sql_txt_create_schema())

    sm.sql_exec_txt(sm.sql_txt_create_table())

    # # models
    print('\n- Modeles\n')

    Model = sm.Model()

    # # test requete simple

    # # insert
    sample = sm.sample()
    print('  - insert', sample)
    m = Model()
    sm.validate_data(sample)
    sm.unserialize(m, sample)
    DB.session.add(m)
    DB.session.commit()

    # # update
    print('  - update')
    code_field_name = sm.code_field_name()
    setattr(m, code_field_name, 'T_02')
    DB.session.commit()

    # # get
    print('  - get')
    m = DB.session.query(Model).filter(getattr(Model, code_field_name) == 'T_02').one()
    DB.session.commit()

    # delete
    print('  - delete', code_field_name)
    Model.query.filter(getattr(m, code_field_name) == 'T_02').delete()
    DB.session.commit()

    # random samples
    nb_samples = 100
    t0 = time.time()
    print('\n- create random samples (nb={}) Model(**data)\n'.format(nb_samples))
    for i in range(nb_samples):
        data = sm.random_sample()
        m = Model(**data)
        # sm.unserialize(m, data)

        # sm.unserialize(m, data)
        DB.session.add(m)
        DB.session.commit()

    t1 = time.time()
    nb_samples = 100
    print('\n- create random samples (nb={}) sm.unserialize(m, data)\n'.format(nb_samples))
    for i in range(nb_samples):
        data = sm.random_sample()
        m = Model()
        sm.unserialize(m, data)
        DB.session.add(m)
        DB.session.commit()
    t2 = time.time()

    print(
        'Compare time\n  - Model(**data) : {}\n  - sm.unserialize(m, data) : {}\n'
        .format(round(t1 - t0, 3), round(t2 - t1, 3))
    )


    # # test generic repo
    print('\n- Repositories and serializers\n')

    # insert_row
    data = sm.random_sample()
    m = sm.insert_row(data)
    print('  - insert_row :\n{}\n'.format(json.dumps(sm.serialize(m), indent=4)))

    # get_row
    id = getattr(m, sm.pk_field_name())
    m = sm.get_row(id).one()
    print('  - get_row {} :\n{}\n'.format(id, json.dumps(sm.serialize(m), indent=4)))

    # update_row
    data[sm.code_field_name()] = 'T_02'
    m = sm.update_row(id, data)
    print('  - update_row {} :\n{}\n'.format(id, json.dumps(sm.serialize(m), indent=4)))

    # delete_row
    m = sm.delete_row(id)
    print('  - delete_row {} :\n{}\n'.format(id, json.dumps(sm.serialize(m), indent=4)))


    # fin des tests
    print('\n- test schema {}/{} ok\n'.format(group_name, object_name))

    return


# liste des commande pour export dans blueprint.py
commands = [
    cmd_create_schema,
    cmd_sql_schema,
    cmd_test,
]