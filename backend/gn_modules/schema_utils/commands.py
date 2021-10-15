'''
    SchemaMethods : static methods for cmd
'''

class SchemaCommands:
    '''
        static methods for cmd
    '''

    @classmethod
    def create_schema(cls, group_name, object_name, label=None, genre='M', write_file=False, force_write_file=False):
        '''
            return schema_template for group_name and object_name
            
            - write schema file if:
              - <write_file> is True and file not exists already
              - or force_write_file is True

            TODO ajout argument fields = ['id', 'name', 'code', ('uuid', 'create', 'update')] 
              - pour choisir les proprietes de base (+ uuid, date creation/modification)
              - template depuis fichier '/schema/templates/<template_name>.json.template'
                - base : id code name
                - full : id code name uuid meta_create_date, meta_update_date
                - base_geom : base + geom
                - full_geom : full + geom
              - decouper fonction 
                - lecture schema
                - creation schema
                - ecriture fichier
        '''

        label = label or object_name

        txt_schema_template = (
'''{{
    "$id": "/schemas/{group_name}/{object_name}",
    "type": "object",
    "$meta": {{
        "object_name": "{object_name}",
        "group_name": "{group_name}",
        "genre": "{genre}",
        "label": "{label}"
    }},
    "properties": {{
        "{object_name}_id": {{ 
            "type": "integer",
            "label": "ID {label}",
            "primary_key": true 
        }},
        "{object_name}_name":
            {{ 
                "type": "string",
                "label": "Nom {label}"
            }},
        "{object_name}_code": 
            {{
                "type": "string",
                "label": "Code {label}"
            }}
    }}
}}
'''
        ).format(
            group_name=group_name,
            object_name=object_name,
            label=label,
            genre=genre
        )

        if not (write_file or force_write_file):
            return txt_schema_template

        jsonschema_file_path = cls.cls_schema_file_path(group_name, object_name)

        # test if file exists
        if jsonschema_file_path.is_file() and not force_write_file:
            print(
                "\nle fichier du schema {}.{} : {} existe déjà\n\n\t- utiliser l'option -f, --force-write-file pour forcer l'écriture du fichier\n"
                .format(group_name, object_name, jsonschema_file_path)
            )
            return txt_schema_template

        # mkdir -p
        jsonschema_file_path.parents[0].mkdir(parents=True, exist_ok=True)

        print(
            '\n{}écriture du schema {}.{} dans le fichier {}\n'
            .format(
                'ré' if jsonschema_file_path.is_file() else '',
                group_name,
                object_name,
                jsonschema_file_path
            )
        )

        with open(jsonschema_file_path, 'w') as f:
            f.write(txt_schema_template)

        sample_file_path = cls.cls_schema_file_path(group_name, object_name, 'sample')

        sample = cls(group_name, object_name).random_sample()

        with open(sample_file_path, 'w') as f:
            f.write(txt_schema_template)

        return txt_schema_template