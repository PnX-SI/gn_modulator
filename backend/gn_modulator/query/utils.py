import re
from flask import g
from .base import BaseSchemaQuery
import sqlalchemy as sa


class SchemaQueryUtils(BaseSchemaQuery):
    """
    sorter
    page/size
    cruved?
    """

    def get_sorters(self, sort):
        order_bys = []

        for s in sort:
            sorters, self = self.get_sorter(s)
            order_bys.extend(sorters)

        return order_bys, self

    def get_sorter(self, sorter):
        orders_by = []
        sort_dir = "-" if "-" in sorter else "+"
        sort_spe = "str_num" if "*" in sorter else "num_str" if "%" in sorter else None
        sort_field = re.sub(r"[+-\\*%]", "", sorter)

        model_attribute, self = self.getModelAttr(self.Model(), sort_field, self)

        if model_attribute is None:
            raise Exception(f"Pb avec le tri {self.schema_code()}, field: {sort_field}")

        if sort_spe is not None:
            sort_string = sa.func.substring(model_attribute, "[a-zA-Z]+")
            sort_number = sa.cast(sa.func.substring(model_attribute, "[0-9]+"), sa.Numeric)

            if sort_spe == "str_num":
                orders_by.extend([sort_string, sort_number])
            else:
                orders_by.extend([sort_number, sort_string])

        orders_by.append(model_attribute)

        orders_by = [
            sa.nullslast(order_by.desc() if sort_dir == "-" else order_by.asc())
            for order_by in orders_by
        ]

        return orders_by, self

    def process_page_size(self, page, page_size):
        """
        LIMIT et OFFSET
        """

        if page_size and int(page_size) > 0:
            self = self.limit(page_size)

            if page and int(page) > 1:
                offset = (int(page) - 1) * int(page_size)
                self = self.offset(offset)

        return self

    def process_query_columns(self, params, order_by, id_role):
        """
        permet d'ajouter de colonnes selon les besoin
        - scope pour cruved (toujours?)
        - row_number (si dans fields)
        """

        fields = params.get("fields") or []

        # cruved
        if "scope" in fields:
            self = self.add_column_scope(id_role)

        # row_number
        if "row_number" in fields:
            self = self.add_column(
                sa.func.row_number().over(order_by=order_by).label("row_number")
            )

        return self
