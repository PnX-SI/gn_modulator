from sqlalchemy.orm import column_property
from sqlalchemy import (
    func,
    literal,
    select,
    exists,
    and_,
    literal_column,
    cast,
)
from geonature.utils.env import db
from .. import errors


class SchemaModelColumnProperties:
    """ """

    def column_property_relation_x_n(self, key, column_property_def, Model):
        # a passer en argument

        cp_query = cp_select = self.cp_select(key, column_property_def, Model)
        if column_property_def.get("relation_key"):
            cp_where_conditions = self.column_property_util_relation_where_conditions(
                key, column_property_def, Model
            )
            cp_query = cp_select.where(cp_where_conditions)

        return column_property(cp_query)

    def cp_select(self, key, column_property_def, Model):

        column_property_type = column_property_def.get("column_property")
        if column_property_type == "nb":
            return select([func.count("*")])

        if column_property_type == "has":
            return exists()

        if column_property_type == "label":
            # TODO communes <area_name> (<area_code[:2]>) ??
            # relation = getattr(Model, column_property_def['relation_key'])
            # relation_entity = relation.mapper.entity
            label_key = ".".join(
                [column_property_def["relation_key"], column_property_def["label_key"]]
            )
            relation_label, _ = self.custom_getattr(Model, label_key)
            return select(
                [func.string_agg(cast(relation_label, db.String), literal_column("', '"))]
            )

        if column_property_type in ["st_x", "st_y"]:
            return getattr(func, column_property_type)(
                func.st_centroid(getattr(Model, column_property_def["key"]))
            )

        if column_property_type == "concat":
            # label = '<area_code> <area_name>'
            # 1 => ['<area_code>', '', '<area_name>']
            # 2 => map getattr
            # 3 *dans concat
            label = column_property_def["label"]
            index = 0
            items = []
            items2 = []
            txt = ""
            while index <= len(label):
                if index == len(label) or label[index] == "<":
                    if txt:
                        items.append(literal(txt))
                        items2.append(txt)
                        txt = ""
                elif label[index] == ">":
                    model_attribute, _ = self.custom_getattr(Model, txt)
                    items2.append(txt)
                    items.append(model_attribute)
                    txt = ""
                else:
                    txt += label[index]
                index += 1
            return func.concat(*items)

        if column_property_type in ["st_astext"]:
            return func.st_astext(getattr(Model, column_property_def["key"]))

        if column_property_type in ["min", "max"]:
            field_key = ".".join([column_property_def["relation_key"], column_property_def["key"]])
            relation_field, _ = self.custom_getattr(Model, field_key)
            func_min_max = getattr(func, column_property_type)
            return select([func_min_max(relation_field)])

        raise errors.SchemaModelColumnPropertyError(
            "La column_property {} {} est mal définie".format(self.schema_code(), key)
        )

    def column_property_util_relation_where_conditions(self, key, column_property_def, Model):

        relation, _ = self.custom_getattr(Model, column_property_def["relation_key"])
        rel = self.cls(self.property(column_property_def["relation_key"])["schema_code"])
        conditions = relation
        if column_property_def.get("filters") is not None:
            condition_filters, conditions = rel.process_filter_array(
                relation.mapper.entity,
                self.parse_filters(column_property_def.get("filters")),
                query=conditions,
                condition=True,
            )
            conditions = and_(conditions, condition_filters)

        return conditions

    def process_column_property_model(self, key, column_property_def, Model):
        return self.column_property_relation_x_n(key, column_property_def, Model)
