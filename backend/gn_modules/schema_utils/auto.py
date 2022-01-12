'''
    AutoSchemas
'''
from sqlalchemy.inspection import inspect
from sqlalchemy.engine import reflection
from flask_sqlalchemy import model
from geonature.utils.env import DB
from sqlalchemy.sql.schema import Column
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

        schema_dot_table = self.schema_dot_table()

        if not self.cls().c_sql_schema_dot_table_exists(schema_dot_table):
            raise SchemaAutoError("La table {} n'existe pas".format(schema_dot_table))

        Model = self.cls().c_get_model_from_schema_dot_table(schema_dot_table)

        if Model is None:
            raise SchemaAutoError('Pas de modèles trouvé pour la table {}'.format(schema_dot_table))

        sql_table_name = Model.__tablename__
        sql_schema_name = Model.__table__.schema

        properties = self.autoproperties(Model)

        autoschema = {
            '$meta': {
                "sql_table_name": sql_table_name,
                "sql_schema_name": sql_schema_name,
            },
            "properties": properties
        }

        for key, property in schema_definition.get('properties', {}).items():

            if key in autoschema['properties']:
                autoschema['properties'][key].update(property)
            else:
                autoschema['properties'][key] = property

        schema_definition['properties'] = autoschema['properties']

        return schema_definition

    def autoproperties(self, Model):
        properties = {}

        sql_table_name = Model.__tablename__
        sql_schema_name = Model.__table__.schema

        reflected_columns = insp.get_columns(sql_table_name, schema=sql_schema_name)

        for column in Model.__table__.columns:
            if not hasattr(Model, column.key):
                continue
            properties[column.key] = self.process_column_auto(column, reflected_columns, sql_schema_name, sql_table_name)

        for relation_key, relation in inspect(Model).relationships.items():
            if relation_key not in self.meta('relation', []):
                continue
            property = self.process_relation_auto(relation_key, relation)
            if property:
                properties[relation_key] = property

        return properties

    def process_relation_auto(self, relation_key, relation):
        # return
        if not relation.target.schema:
            return
        property = {
            "type": "relation",
            "relation_type": (
                'n-1' if relation.direction.name == "MANYTOONE"
                else '1-n' if relation.direction.name == "ONETOMANY"
                else 'n-n'
            ),
            "schema_name": self.cls().c_get_schema_name_from_schema_dot_table(relation.target.schema + '.' + relation.target.name),
            "title": relation_key
        }

        if property['relation_type'] == 'n-n':
            property['schema_dot_table'] = '{}.{}'.format(relation.secondary.schema, relation.secondary.name)

        if not property['schema_name']:
            return

        return property

    def process_column_auto(self, column, reflected_columns, sql_schema_name, sql_table_name):
        type = str(column.type)

        schema_type = self.cls().c_get_type(type, 'sql', 'definition')

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
            'title': column.key
        }

        if(schema_type['type'] == 'geometry'):
            property['srid'] = schema_type['srid']
            property['geometry_type'] = schema_type['geometry_type']

        # primary_key

        if column.primary_key:
            property['primary_key'] = True

        # foreign_keys

        for foreign_key in column.foreign_keys:
            key = foreign_key.target_fullname.split('.')[-1]
            schema_dot_table = ".".join(foreign_key._table_key().split('.'))
            schema_name = self.cls().c_get_schema_name_from_schema_dot_table(schema_dot_table)
            if not schema_name:
                # TODO avec des schema non encore crées ??
                continue
            property['foreign_key'] = True
            property['schema_name'] = schema_name

            if schema_name == 'schemas.utils.nomenclature.nomenclature':

                # nomenclature_type
                nomenclature_type = self.reflect_nomenclature_type(sql_schema_name, sql_table_name, column.key)
                property['nomenclature_type'] = nomenclature_type
                # property.pop('foreign_key')

        # commentaires
        reflected_column = next(x for x in reflected_columns if x['name'] == column.key)
        if reflected_column.get('comment'):
            property['description'] = reflected_column.get('comment')

        return property

    def reflect_nomenclature_type(self, sql_schema_name, sql_table_name, column_key):
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
