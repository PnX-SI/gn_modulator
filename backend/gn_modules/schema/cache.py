import copy

from numpy import outer

'''
cache schema
  - <schema_name>
        - definition
        - marshmallow
        - cor_table
        - model
        TODO !!
        - validation
        - schema ou form ??
'''
cache_schemas = {}


'''
    - references
    - sql_table
    - etc...
'''
cache_global = {}

def clear_dict(d):
    if not d:
        return

    d_keys = copy.copy(list(d.keys()))
    for key in d_keys:
        del d[key]

class SchemaCache():

    @classmethod
    def clear_global_cache(cls, object_type=None):
        '''
            TODO recursif ??
        '''
        d = (
            cache_global.get(object_type) if object_type
            else cache_global
        )

        clear_dict(d)

    @classmethod
    def get_global_cache(cls, object_type, key=None):

        out = cache_global.get(object_type, {})
        return (
            out.get(key) if key
            else out
        )

    @classmethod
    def set_global_cache(cls, object_type, key, value):
        cache_global[object_type] = cache_global.get(object_type, {})
        cache_global[object_type][key] = value

    @classmethod
    def clear_schema_cache(cls):
        '''
            TODO recursif ??
        '''
        clear_dict(cache_schemas)

    @classmethod
    def get_schema_cache(cls, schema_name, object_type=None):

        if schema_name == '*':
            return {
                k: (
                    v.get(object_type) if object_type
                    else v
                )
                for k, v in cache_schemas.items()
            }

        out = cache_schemas.get(schema_name, {})

        out = (
            out.get(object_type) if object_type
            else out
        )

        return out

    @classmethod
    def set_schema_cache(cls, schema_name, object_type, value):
        cache_schemas[schema_name] = cache_schemas.get(schema_name, {})
        cache_schemas[schema_name][object_type] = value

    @classmethod
    def schema_names_from_cache(cls):
        return list(cache_schemas.keys())
