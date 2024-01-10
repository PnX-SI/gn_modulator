"""
    SchemaMethods : base methods for schemas

    - setters, getters
    - utils - schema parser

"""

import copy
import json
from gn_modulator import MODULE_CODE
from gn_modulator.utils.cache import get_global_cache

column_types = [
    "integer",
    "number",
    "string",
    "geometry",
    "date",
    "datetime",
    "boolean",
    "uuid",
    "json",
]


class SchemaBase:
    """
    - cls           : self.__class__
    - log           : log message
    - pprint        : pretty print for dict
    - schema
    - set_schema
    """

    # getters, setters

    @classmethod
    def log(cls, msg):
        """
        Pour les log, print pour l'instant
        TODO
        """
        print(msg)

    @classmethod
    def pprint(cls, d, indent=2):
        print(json.dumps(d, indent=indent, sort_keys=True, ensure_ascii=False))

    def get_schema(self, columns_only=False):
        # import pdb; pdb.set_trace()
        schema = self.json_schema

        if columns_only:
            schema = copy.deepcopy(schema)
            schema["properties"] = {
                key: column_def
                for key, column_def in schema["properties"].items()
                if key in self.column_keys()
            }

        return schema

    # utils - schema parser

    def required(self):
        return self.attr("required", [])

    def is_required(self, key):
        return key in self.properties() and (
            self.properties()[key].get("required")
            or key in self.required()
            or (
                self.properties()[key].get("primary_key")
                and self.properties()[key].get("foreign_key")
            )
        )

    def attr(self, prop=None, default=None):
        """
        renvoie
        - $meta si prop est null
        - $meta['prop1']['prop2']['prop3'] si prop = 'prop1.prop2.prop3'

        ou $meta.prop
        """

        elem = self.definition

        if not prop:
            return elem

        for prop_path in prop.split("."):
            if not isinstance(elem, dict):
                return default
            elem = elem.get(prop_path, None)
            if elem is None:
                return default

        return elem or default

    def schema_code(self, letter_case=None):
        """
        return name
        """

        schema_code = self._schema_code

        if letter_case == "pascal_case":
            return schema_code.replace(".", " ").title().replace(" ", "")
        if letter_case in ["snake_case", "_"]:
            return schema_code.replace(".", "_")
        if letter_case == "/":
            return schema_code.replace(".", "/")
        else:
            return schema_code

    @classmethod
    def schema_codes(cls):
        """
        renvoie la liste des noms de schemas (depuis les données du cache)
        """
        return list(get_global_cache(["schema"], {}).keys())

    def object_code(self):
        return self.schema_code().split(".")[-1]

    def group_name(self):
        return self.schema_code().split(".")[-2]

    def code_field_name(self):
        return self.attr("meta.code_field_name", f"{self.object_code()}_code")

    def name_field_name(self):
        return self.attr("meta.name_field_name", f"{self.object_code()}_name")

    def is_column(self, key):
        return self.has_property(key) and self.property(key).get("type") in column_types

    def is_column_property(self, key):
        return (
            self.has_property(key)
            and (self.property(key).get("type") in column_types + ["relation"])
            and (self.property(key).get("column_property"))
        )

    def is_relationship(self, key):
        return self.has_property(key) and self.property(key)["type"] == "relation"

    def column_keys(self, sort=False):
        column_keys = [k for k, v in self.properties().items() if self.is_column(k)]
        if sort:
            column_keys.sort()
        return column_keys

    def column_properties_keys(self, sort=False):
        column_keys = [k for k, v in self.properties().items() if self.is_column_property(k)]
        if sort:
            column_keys.sort()
        return column_keys

    def relationship_keys(self):
        return [k for k, v in self.properties().items() if self.is_relationship(k)]

    def relationship_1_n_keys(self):
        return [k for k, v in self.properties().items() if self.is_relation_1_n(k)]

    def properties(self):
        return self.definition["properties"]

    def property(self, key):
        if "." in key:
            # on cherche la relation
            rel_key = key.split(".")[0]
            rel_prop = self.property(rel_key)
            if rel_prop["type"] == "json":
                return rel_prop
            rel = self.cls(rel_prop["schema_code"])
            return rel.property(".".join(key.split(".")[1:]))
        return self.properties().get(key)

    def has_property(self, key):
        if "." in key:
            # on cherche la relation
            rel_key = key.split(".")[0]
            if not self.has_property(rel_key):
                return False
            rel_prop = self.property(rel_key)
            if rel_prop["type"] == "json":
                return True
            rel = self.cls(rel_prop["schema_code"])
            return rel.has_property(".".join(key.split(".")[1:]))
        return self.properties().get(key) is not None

    def columns(self, sort=False):
        column = {}

        for key in self.column_keys(sort=sort):
            column[key] = self.property(key)

        return column

    def column_properties(self, sort=False):
        column = {}

        for key in self.column_properties_keys(sort=sort):
            column[key] = self.property(key)

        return column

    def relationships(self):
        relationship = {}
        for key in self.relationship_keys():
            relationship[key] = self.properties()[key]

        return relationship

    def column(self, key):
        return self.columns()[key]

    def relationship(self, key):
        return self.relationships()[key]

    def relation_type(self, relation_def):
        relation_type = (
            "n-1"
            if relation_def.get("local_key") and not relation_def.get("foreign_key")
            else "1-n"
            if relation_def.get("foreign_key") and not relation_def.get("local_key")
            else "n-n"
            if relation_def.get("foreign_key") and relation_def.get("local_key")
            else None
        )

        if relation_type is None:
            raise self.errors.SchemaRelationError(
                f"relation type is None for relation_def : {relation_def}"
            )
        return relation_type

    def columns_array(self, columns_only=False):
        """
        return properties as array

        store properties key as 'name'
        """

        properties_dict = copy.deepcopy(self.columns())
        columns_array = []

        for k, v in properties_dict.items():
            v.update({"name": k})
            columns_array.append(v)

        return columns_array

    def dependencies(self, exclude_deps=[]):
        deps = [self.schema_code()]
        for key, relation_def in self.relationships().items():
            schema_code = relation_def["schema_code"]

            if schema_code in deps + exclude_deps:
                continue

            deps.append(schema_code)
            deps += self.cls(relation_def["schema_code"]).dependencies(
                exclude_deps=deps + exclude_deps
            )

        if self.schema_code() in deps:
            deps.remove(self.schema_code())

        return list(dict.fromkeys(deps))

    def remove_field(self, field_name, schema):
        if isinstance(schema, dict):
            schema_out = {}
            for k, v in schema.items():
                if k == field_name:
                    continue
                schema_out[k] = self.remove_field(field_name, v)
            return schema_out

        if isinstance(schema, list):
            return [self.remove_field(field_name, v) for v in schema]

        return schema

    # A mettre ailleurs

    def process_csv_keys(self, keys):
        return [
            self.property(key.split(".")[0]).get("title", key)
            if self.has_property(key.split(".")[0])
            else key
            for key in keys
        ]

    def flat_keys(self, data, key=None):
        keys = []
        for k in data:
            keys.append(k)

            # if isinstance(data[k], list):
            #     keys.append(map("k."self.flat_keys(data[k], k)))

            # if isinstance(data[k], dict):
            # k_all =
            # if k not in keys:
            #     if
            #     keys.append(".".join([*keysParent, k])

        return keys

    def process_csv_data(self, key, data, options={}, process_label=True):
        """
        pour rendre les sorties des relations jolies pour l'export ??
        """

        if isinstance(data, list):
            return ", ".join(
                [str(self.process_csv_data(key, d, process_label=process_label)) for d in data]
            )

        if isinstance(data, dict):
            if not key:
                return "_".join(
                    [
                        self.process_csv_data(None, data[k], process_label=process_label)
                        for k in data.keys()
                    ]
                )

            if "." in key:
                key1 = key.split(".")[0]
                key2 = ".".join(key.split(".")[1:])

                return self.process_csv_data(key2, data[key1], process_label=process_label)

            options = self.has_property(key) and self.property(key) or {}
            return self.process_csv_data(
                None, data[key], options=options, process_label=process_label
            )

        labels = options.get("labels") and process_label
        if labels:
            if data is True:
                return labels[0] if len(labels) > 0 else True
            elif data is False:
                return labels[1] if len(labels) > 1 else False
            else:
                return labels[1] if len(labels) > 2 else None

        return data

    @classmethod
    def base_url(cls):
        """
        base url (may differ with apps (GN, UH, TH, ...))
        TODO process apps ?
        """
        from geonature.utils.config import config

        return f'{config["API_ENDPOINT"]}/{MODULE_CODE.lower()}'

    def url(self, post_url, full_url=False):
        """
        /{schema_code}{post_url}
        - full/url renvoie l'url complet
        TODO gérer par type d'url ?
        """

        url = self.attr("meta.url", f"/{self.schema_code()}{post_url}")

        if full_url:
            url = f"{self.cls.base_url()}{url}"

        return url

    def unique(self):
        return self.attr("meta.unique") or []

    def is_relation_n_n(self, key):
        return self.has_property(key) and self.property(key).get("relation_type") == "n-n"

    def is_relation_n_1(self, key):
        return self.has_property(key) and self.property(key).get("relation_type") == "n-1"

    def is_relation_1_n(self, key):
        return self.has_property(key) and self.property(key).get("relation_type") == "1-n"

    def is_primary_key(self, key):
        return self.has_property(key) and self.property(key).get("primary_key")

    def is_foreign_key(self, key):
        return self.has_property(key) and self.property(key).get("foreign_key")

    def default_fields(self, Model=None):
        if Model is None:
            Model = self.Model()
        return self.attr("meta.default_fields") or list(
            filter(
                lambda x: x is not None,
                [Model.pk_field_name(), self.label_field_name(), self.title_field_name()],
            )
        )

    def cut_to_json(self, key):
        """
        renvoie le champs json de la variable key
        """
        keys = key.split(".")
        for index, k in enumerate(keys):
            current_key = ".".join(keys[: index + 1])
            if self.property(current_key)["type"] == "json":
                return current_key
        return key
