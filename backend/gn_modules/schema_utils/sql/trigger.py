'''
    SchemaSqlTrigger
'''


class SchemaSqlTrigger():
    '''
        methods pour gerer les trigger
    '''

    def sql_txt_process_triggers(self):
        '''
            methode pour gerer les triggers associés à un schema
        '''

        txt = ''
        for property_key, property_def in self.properties().items():
            txt += self.sql_txt_process_trigger(property_key, property_def)

        if txt:
            txt = '\n-- Triggers\n\n\n' + txt
        return txt

    def sql_txt_process_trigger(self, property_key, property_def):
        '''
            fonction qui cree les trigger associé à un élément d'un schema
        '''

        trigger_name = property_def.get('trigger', {}).get('name')
        if not trigger_name:
            return ''

        if trigger_name == 'intersect_ref_geo':
            return self.sql_txt_trigger_intersect_ref_geo(property_key, property_def)

        if trigger_name == 'd_within':
            return self.sql_txt_trigger_d_within(property_key, property_def)

    def sql_txt_trigger_intersect_ref_geo(self, property_key, property_def):
        '''
        '''

        area_types = property_def.get('area_types', [])
        area_types_txt = (
            ' pour les types {}'.format(', '.join(area_types)) if area_types
            else ''
        )

        txt = ''

        cor_schema_name = property_def['schema_dot_table'].split('.')[0]
        cor_table_name = property_def['schema_dot_table'].split('.')[1]

        txt_data = {
            'sql_schema_name': self.sql_schema_name(),
            'sql_table_name': self.sql_table_name(),
            'cor_schema_name':cor_schema_name,
            'cor_table_name': cor_table_name,
            'local_key': self.pk_field_name(),
            'trigger_function_insert_name': (
                '{}.fct_trig_insert_{}_on_each_statement'
                .format(cor_schema_name, cor_table_name)
            ),
            'trigger_function_update_name': (
                '{}.fct_trig_update_{}_on_row'
                .format(cor_schema_name, cor_table_name)
            ),

            'area_types': area_types,
            'geometry_field_name': self.geometry_field_name(),
            'area_types_txt': area_types_txt
        }

        txt += (
            '---- Trigger intersection {sql_schema_name}.{sql_table_name}.{geometry_field_name} avec le ref_geo{area_types_txt}\n\n'
            .format(**txt_data)
        )

        txt += '''CREATE OR REPLACE FUNCTION {trigger_function_insert_name}()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                WITH geom_test AS (
                    SELECT ST_TRANSFORM(t.{geometry_field_name}, 2154) as geom,
                    t.{local_key}
                    FROM NEW as t
                )
                INSERT INTO {cor_schema_name}.{cor_table_name} (
                    id_area,
                    {local_key}
                )
                SELECT
                    a.id_area,
                    t.{local_key}
                    FROM geom_test t
                    JOIN ref_geo.l_areas a
                        ON public.ST_INTERSECTS(t.{geometry_field_name}, a.geom)
                        WHERE
                            a.enable IS TRUE
                            AND (
                                ST_GeometryType(t.{geometry_field_name}) = 'ST_Point'
                                OR
                                NOT public.ST_TOUCHES(t.{geometry_field_name},a.geom)
                            );
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

'''.format(**txt_data)

        txt += '''CREATE OR REPLACE FUNCTION {trigger_function_update_name}()
    RETURNS trigger AS
        $BODY$
            BEGIN
                DELETE FROM {cor_schema_name}.{cor_table_name} WHERE {local_key} = NEW.{local_key};
                INSERT INTO {cor_schema_name}.{cor_table_name} (
                    id_area,
                    {local_key}
                )
                SELECT
                    a.id_area,
                    t.{local_key}
                FROM ref_geo.l_areas a
                JOIN {sql_schema_name}.{sql_table_name} t
                    ON public.ST_INTERSECTS(ST_TRANSFORM(t.{geometry_field_name}, 2154), a.geom)
                WHERE
                    a.enable IS TRUE
                    AND t.{local_key} = NEW.{local_key}
                    AND (
                        ST_GeometryType(t.{geometry_field_name}) = 'ST_Point'
                        OR NOT public.ST_TOUCHES(ST_TRANSFORM(t.{geometry_field_name}, 2154), a.geom)
                    )
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

'''.format(**txt_data)

        txt += '''CREATE TRIGGER trg_insert_{cor_schema_name}_{cor_table_name}
    AFTER INSERT ON {sql_schema_name}.{sql_table_name}
    REFERENCING NEW TABLE AS NEW
    FOR EACH STATEMENT
        EXECUTE PROCEDURE {trigger_function_insert_name}();

'''.format(**txt_data)

        txt += '''CREATE TRIGGER trg_update_{cor_schema_name}_{cor_table_name}
    AFTER UPDATE OF {geometry_field_name} ON {sql_schema_name}.{sql_table_name}
    FOR EACH ROW
        EXECUTE PROCEDURE {trigger_function_update_name}();

'''.format(**txt_data)

        return txt

    def sql_txt_trigger_d_within(self, property_key, property_def):
        """

        """

        cor_schema_name = property_def['schema_dot_table'].split('.')[0]
        cor_table_name = property_def['schema_dot_table'].split('.')[1]
        relation = self.cls()(property_def['schema_name'])

        txt_data = {
            'distance': property_def['trigger']['distance'],
            'sql_schema_name': self.sql_schema_name(),
            'sql_table_name': self.sql_table_name(),
            'relation_schema_name': relation.sql_schema_name(),
            'relation_table_name': relation.sql_table_name(),
            'relation_geometry_field_name': relation.geometry_field_name(),
            'cor_schema_name': cor_schema_name,
            'cor_table_name': cor_table_name,
            'local_key': self.pk_field_name(),
            'foreign_key': relation.pk_field_name(),
            'trigger_function_insert_name': (
                '{}.fct_trig_insert_{}_on_each_statement'
                .format(cor_schema_name, cor_table_name)
            ),
            'trigger_function_update_name': (
                '{}.fct_trig_update_{}_on_row'
                .format(cor_schema_name, cor_table_name)
            ),
            'geometry_field_name': self.geometry_field_name(),
        }

        txt = ''
        txt += (
            '---- Trigger {sql_schema_name}.{sql_table_name}.{geometry_field_name} avec une distance de {distance} avec {relation_schema_name}.{relation_table_name}.{foreign_key}\n\n'
            .format(**txt_data)
        )

        txt += '''CREATE OR REPLACE FUNCTION {trigger_function_insert_name}()
    RETURNS trigger AS
        $BODY$
            DECLARE
            BEGIN
                INSERT INTO {cor_schema_name}.{cor_table_name} (
                    {foreign_key},
                    {local_key}
                )
                SELECT
                    a.{foreign_key},
                    t.{local_key}
                    FROM {sql_schema_name}.{sql_table_name} t
                    JOIN {relation_schema_name}.{relation_table_name} a
                        ON ST_DWITHIN(t.{geometry_field_name}, a.{relation_geometry_field_name}, {distance})
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

'''.format(**txt_data)

        txt += '''CREATE OR REPLACE FUNCTION {trigger_function_update_name}()
    RETURNS trigger AS
        $BODY$
            BEGIN
                DELETE FROM {cor_schema_name}.{cor_table_name} WHERE {local_key} = NEW.{local_key};
                INSERT INTO {cor_schema_name}.{cor_table_name} (
                    a.{foreign_key},
                    t.{local_key}
                )
                SELECT
                    a.{foreign_key},
                    t.{local_key}
                FROM {relation_schema_name}.{relation_table_name} a
                JOIN {sql_schema_name}.{sql_table_name} t
                    ON ST_DWITHIN(t.{geometry_field_name}, a.{relation_geometry_field_name}, {distance})
                WHERE
                    t.{local_key} = NEW.{local_key}
                ;
                RETURN NULL;
            END;
        $BODY$
    LANGUAGE plpgsql VOLATILE
    COST 100;

'''.format(**txt_data)

        txt += '''CREATE TRIGGER trg_insert_{cor_schema_name}_{cor_table_name}
    AFTER INSERT ON {sql_schema_name}.{sql_table_name}
    REFERENCING NEW TABLE AS NEW
    FOR EACH STATEMENT
        EXECUTE PROCEDURE {trigger_function_insert_name}();

'''.format(**txt_data)

        txt += '''CREATE TRIGGER trg_update_{cor_schema_name}_{cor_table_name}
    AFTER UPDATE OF {geometry_field_name} ON {sql_schema_name}.{sql_table_name}
    FOR EACH ROW
        EXECUTE PROCEDURE {trigger_function_update_name}();

'''.format(**txt_data)

        return txt
