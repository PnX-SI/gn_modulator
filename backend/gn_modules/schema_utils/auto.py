'''
    AutoSchemas
'''

from sqlalchemy.engine import reflection
from geonature.utils.env import DB
from .errors import SchemaAutoError

cor_type_db_schema = {
    'INTEGER': 'integer',
    'VARCHAR': 'string',
    'BOOLEAN': 'boolean',
    'FLOAT': 'number',
    'UUID': 'uuid',
    'DATETIME': 'datetime',
    'DATE': 'date',
}

insp = reflection.Inspector.from_engine(DB.engine)


class SchemaAuto():

    def autoschema(self):
        '''
            boolean pour savoir si on calcule le schema automatiquement
        '''
        return self.meta('autoschema')

    def get_autoschema(self):
        '''
            combine definition schema & autoschema
        '''
        schema_definition = self.schema()
        autoschema = self.cls().c_get_autoschema(self.schema_dot_table())

        for key, property in schema_definition.get('properties', {}).items():
            if key in autoschema['properties']:
                autoschema['properties'][key].update(property)
            else:
                autoschema['properties'][key] = property

        schema_definition['properties'] = autoschema['properties']

        return schema_definition

    @classmethod
    def c_get_autoschema(cls, schema_dot_table):
        '''
            depuis <schema>.<table>
            cree automatiquement un schema
            s'aide un peu du modèle existant
        '''

        if not cls.c_sql_schema_dot_table_exists(schema_dot_table):
            raise SchemaAutoError("La table {} n'existe pas".format(schema_dot_table))

        Model = cls.c_get_model_from_schema_dot_table(schema_dot_table)

        if Model is None:
            raise SchemaAutoError('Pas de modèles trouvé pour la table {}'.format(schema_dot_table))

        sql_table_name = Model.__tablename__
        sql_schema_name = Model.__table__.schema

        properties = cls.c_autoproperties(Model)



        return {
            '$meta': {
                "sql_table_name": sql_table_name,
                "sql_schema_name": sql_schema_name,
            },
            "properties": properties
        }

    @classmethod
    def c_autoproperties(cls, Model):

        properties = {}

        sql_table_name = Model.__tablename__
        sql_schema_name = Model.__table__.schema

        reflected_columns = insp.get_columns(sql_table_name, schema=sql_schema_name)

        for column in Model.__table__.columns:
            type = str(column.type)

            schema_type = cls.c_get_type(type, 'sql', 'definition')

            if not schema_type:
                raise SchemaAutoError(
                    "{}.{}.{} : Le type sql {} n'a pas de correspondance"
                    .format(
                        sql_schema_name,
                        sql_table_name,
                        column.key,
                        column.type
                    )
                )

            property = {
                'type': schema_type['type'],
                'label': column.key
            }

            if(schema_type['type'] == 'geometry'):
                property['srid']=schema_type['srid']
                property['geometry_type']=schema_type['geometry_type']

            # primary_key

            if column.primary_key:
                property['primary_key'] = True

            # foreign_keys

            for foreign_key in column.foreign_keys:
                key = foreign_key.target_fullname.split('.')[-1]
                schema_dot_table = ".".join(foreign_key._table_key().split('.'))
                schema_name = cls.c_get_schema_name_from_schema_dot_table(schema_dot_table)
                if not schema_name:
                    # TODO avec des schema non encore crées ??
                    continue
                property['foreign_key'] = '{}.{}'.format(schema_name.replace('.', '/'), key)

                if schema_name == 'schemas.utils.nomenclature':

                    # nomenclature_type
                    nomenclature_type = cls.reflect_nomenclature_type(sql_schema_name, sql_table_name, column.key)
                    property['nomenclature_type'] = nomenclature_type
                    property.pop('foreign_key')

            # commentaires
            reflected_column = next(x for x in reflected_columns if x['name'] == column.key)
            if reflected_column.get('comment'):
                property['description'] = reflected_column.get('comment')

            properties[column.key] = property

        return properties

    @classmethod
    def reflect_nomenclature_type(cls, sql_schema_name, sql_table_name, column_key):
        '''
            va chercher les type de nomenclature depuis les contraintes 'check_nomenclature_type'
        '''
        check_constraints = insp.get_check_constraints(sql_table_name, schema=sql_schema_name)
        for check_constraint in check_constraints:
            sqltext = check_constraint['sqltext']
            s_test1 = "ref_nomenclatures.check_nomenclature_type_by_mnemonique({}, '".format(column_key)
            s_test2 = "'::character varying)"
            if s_test1 in sqltext:
                nomenclature_type = sqltext.replace(s_test1, '').replace(s_test2, '')
                return nomenclature_type
