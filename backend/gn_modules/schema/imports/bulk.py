from geonature.utils.env import db

class SchemaBulkImports():

    @classmethod
    def process_csv_file(cls, schema_name, file_path, pre_process_file_path=None, verbose=False):
        '''
            import de données
        '''

        sm = cls(schema_name)
        raw_import_table = f"public.tmp_import_{sm.schema_name('_')}"
        pre_processed_view = f"public.v_pre_processed_import_{sm.schema_name('_')}"
        raw_import_view = f"public.v_raw_import_{sm.schema_name('_')}"
        processed_import_view = f"public.v_processed_import_{sm.schema_name('_')}"

        print(raw_import_table)

        db.engine.execute(f'DROP TABLE IF EXISTS {raw_import_table} CASCADE;')
        # db.engine.execute(f'DROP VIEW IF EXISTS {pre_processed_view} CASCADE;')
        # db.engine.execute(f'SELECT * FROM {raw_import_table} LIMIT 1;')
        # db.engine.execute(f'SELECT * FROM {pre_processed_view} LIMIT 1;')
        db.session.commit()

        # return

        # 0) clean
        cls.clean_import(raw_import_view)
        # db.engine.execute(f"DROP VIEW IF EXISTS {processed_import_view}")
        # db.engine.execute(f"DROP VIEW IF EXISTS {raw_import_view}")
        # db.engine.execute(f"DROP VIEW IF EXISTS {pre_processed_view}")
        # db.engine.execute(f"DROP TABLE IF EXISTS {raw_import_table}")

        # 1) csv -> table temporaire
        cls.bulk_import_process_csv(schema_name, file_path, raw_import_table)
        nb_csv = db.engine.execute(f"SELECT COUNT(*) FROM {raw_import_table}").fetchone()[0]

        # 2) pre-process
        if pre_process_file_path is not None:
            with open(pre_process_file_path, 'r') as f:
                txt_pre_process_raw_import_view = (
                    f.read()
                    .replace(':raw_import_table', raw_import_table)
                    .replace(':pre_processed_import_view', pre_processed_view)
                    .replace('%', '%%')
                )
                verbose and print(txt_pre_process_raw_import_view.replace('%%', '%'))
                db.engine.execute(txt_pre_process_raw_import_view)
                raw_import_table = pre_processed_view

        # table temporaire -> vue brute
        txt_create_raw_import_view = cls.txt_create_raw_import_view(schema_name, raw_import_table, raw_import_view)
        verbose and print(txt_create_raw_import_view)
        db.engine.execute(txt_create_raw_import_view)
        db.engine.execute(f'SELECT * FROM {raw_import_table} LIMIT 1')
        db.session.commit()

        # 3) vue brute -> vue prête pour l'import avec les clés étrangéres et primaires résolues
        txt_create_processed_import_view = cls.txt_create_processed_import_view(schema_name, raw_import_view, processed_import_view)
        verbose and print(txt_create_processed_import_view)
        db.engine.execute(txt_create_processed_import_view)
        db.engine.execute(f'SELECT * FROM {processed_import_view} LIMIT 1')

        nb_processed = db.engine.execute(f"SELECT COUNT(*) FROM {processed_import_view}").fetchone()[0]
        nb_raw = db.engine.execute(f"SELECT COUNT(*) FROM {raw_import_view}").fetchone()[0]
        nb_insert = db.engine.execute(f"SELECT COUNT(*) FROM {processed_import_view} WHERE {sm.pk_field_name()} IS NULL").fetchone()[0]
        nb_update = db.engine.execute(f"SELECT COUNT(*) FROM {processed_import_view} WHERE {sm.pk_field_name()} IS NOT NULL").fetchone()[0]
        print(f'-- {schema_name} CSV {nb_csv} RAW {nb_raw} PROCESSED {nb_processed} INSERT {nb_insert} UPDATE {nb_update}')

        # return
        # 4) INSERT / UPDATE

        # 4-1) INSERT
        txt_import_view_to_insert = cls.txt_import_view_to_insert(schema_name, processed_import_view)
        verbose and print(txt_import_view_to_insert)
        db.engine.execute(txt_import_view_to_insert)

        # 4-2) UPDATE
        txt_import_view_to_update = cls.txt_import_view_to_update(schema_name, processed_import_view)
        verbose and print(txt_import_view_to_update)
        db.engine.execute(txt_import_view_to_update)

        # # 5) process relations ???
        ## ?? au moins n-n
        cls.bulk_import_process_relations(schema_name, raw_import_table, verbose)
        # return "ok"

    @classmethod
    def bulk_import_process_relations(cls, schema_name, raw_import_table, verbose):

        sm = cls(schema_name)

        columns = cls.get_table_columns(raw_import_table)

        for index, column in enumerate(columns):
            if not sm.is_relationship(column.key):
                continue
            property = sm.property(column.key)

            # on commence par les n-n
            if property.get('relation_type') in ('n-n'):
                cls.bulk_import_process_relation_n_n(schema_name, raw_import_table, column.key, verbose)

    @classmethod
    def bulk_import_process_relation_n_n(cls, schema_name, raw_import_table, key, verbose):

        sm = cls(schema_name)

        property = sm.property(key)
        cor_table = property['schema_dot_table']
        rel = cls(property['schema_name'])

        raw_delete_import_view = f"public.v_raw_delete_import_{sm.schema_name('_')}_{key}"
        processed_delete_import_view = f"public.v_processed_delete_import_{sm.schema_name('_')}_{key}"
        raw_import_view = f"public.v_raw_import_{sm.schema_name('_')}_{key}"
        pre_processed_view = f"public.v_pre_processed_import_{sm.schema_name('_')}"
        processed_import_view = f"public.v_processed_import_{sm.schema_name('_')}_{key}"

        # 0) clean
        db.engine.execute(f'DROP VIEW IF EXISTS {processed_import_view}')
        db.engine.execute(f'DROP VIEW IF EXISTS {raw_import_view}')
        db.engine.execute(f'DROP VIEW IF EXISTS {processed_delete_import_view}')
        db.engine.execute(f'DROP VIEW IF EXISTS {raw_delete_import_view}')

        # 1) create raw_temp_table for n-n
        txt_raw_unnest_table = cls.txt_create_raw_import_view(schema_name, raw_import_table, raw_import_view, keys=[key], key_unnest=key)
        verbose and print(txt_raw_unnest_table)
        db.engine.execute(txt_raw_unnest_table)

        txt_process_table = cls.txt_create_processed_import_view(schema_name, raw_import_view, processed_import_view, keys=[key])
        verbose and print(txt_process_table)
        db.engine.execute(txt_process_table)

        # 3) insert / update / delete ??

        # - delete : tout depuis raw_import_table
        # create_view for delete
        txt_raw_delete_table = cls.txt_create_raw_import_view(schema_name, raw_import_table, raw_delete_import_view, keys=[])
        verbose and print(txt_raw_delete_table)
        db.engine.execute(txt_raw_delete_table)

        txt_processed_delete_table = cls.txt_create_processed_import_view(schema_name, raw_delete_import_view, processed_delete_import_view, keys=[])
        verbose and print(txt_processed_delete_table)
        db.engine.execute(txt_processed_delete_table)

        txt_delete = f"""
DELETE FROM {cor_table} t
    USING {processed_delete_import_view} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()}
    """
        db.engine.execute(txt_delete)

        # - insert
        txt_insert = cls.txt_import_view_to_insert(
            schema_name,
            processed_import_view,
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table
        )
        verbose and print(txt_insert)
        db.engine.execute(txt_insert)

        # 0) clean
        # db.engine.execute(f'DROP VIEW IF EXISTS {processed_import_view}')
        # db.engine.execute(f'DROP VIEW IF EXISTS {raw_import_view}')
        # db.engine.execute(f'DROP VIEW IF EXISTS {processed_delete_import_view}')
        # db.engine.execute(f'DROP VIEW IF EXISTS {raw_delete_import_view}')


    @classmethod
    def bulk_import_process_csv(cls, schema_name, file_path, raw_import_table):
        '''
            cree une vue a partir d'un fichier csv pour pouvoir traiter les données ensuite

            le fichier csv
                separateurs : tabs
                pas de quote
            créé
                - une table temporaire pour avoir les données du csv en varchar
                - une vue pour passer les champs en '' à NULL
        '''

        sm = cls(schema_name)

        with open(file_path, 'r') as f:

            # on récupère la premiere ligne du csv pour avoir le nom des colonnes
            first_line = f.readline()

            # creation de la table temporaire
            txt_create_temporary_table_for_csv_import = (
                cls.txt_create_temporary_table_for_csv_import(raw_import_table, first_line)
            )
            db.engine.execute(txt_create_temporary_table_for_csv_import)

            # on copie les données dans la table temporaire
            txt_copy_from_csv = cls.txt_copy_from_csv(raw_import_table, first_line)
            db.session.connection().connection.cursor().copy_expert(txt_copy_from_csv, f)
            db.session.commit()

        return