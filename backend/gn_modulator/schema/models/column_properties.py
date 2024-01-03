from sqlalchemy.orm import column_property
from sqlalchemy import func, literal, select, exists, and_, literal_column, cast
from geonature.utils.env import db
from gn_modulator.utils.filters import parse_filters
from gn_modulator.query.getattr import getModelAttr
from .. import errors


class SchemaModelColumnProperties:
    """ """

    def process_column_property_model(self, key, column_property_def):
        return column_property(self.cp_select(key, column_property_def))

    def cp_select(self, key, column_property_def):
        column_property_type = column_property_def.get("column_property")

        if column_property_type == "concat":
            # label = '<area_code> <area_name>'
            # 1 => ['<area_code>', ' ', '<area_name>']
            # 2 => map getattr
            # 3 *dans concat
            conditions = []
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
                    condition = "." in txt or None
                    model_attribute, condition = getModelAttr(
                        self.Model(), None, txt, condition=condition
                    )
                    if condition is not None:
                        conditions.append(condition)
                    items2.append(txt)
                    items.append(model_attribute)
                    txt = ""
                else:
                    txt += label[index]
                index += 1
            cp = func.concat(*items)
            if conditions:
                cp = select([cp]).where(and_(*conditions))
            return cp

        raise errors.SchemaModelColumnPropertyError(
            f"La column_property {self.schema_code()} {key} est mal définie"
        )
