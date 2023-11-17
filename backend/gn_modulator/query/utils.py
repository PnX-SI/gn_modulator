import re
from flask import g
from .base import BaseSchemaQuery
import sqlalchemy as sa
from geonature.core.gn_permissions.tools import get_scopes_by_action
import sqlparse


class SchemaQueryUtils(BaseSchemaQuery):
    """
    sorter
    page/size
    cruved?
    """

    def sql_txt(self):
        txt = str(self.statement.compile(compile_kwargs={"literal_binds": True}))
        txt = txt.replace("%%", "%")
        txt = sqlparse.format(txt, reindent=True, keywordcase="upper")
        return txt

    def get_sorters(self, sort):
        order_bys = []

        for s in sort:
            self, sorters = self.get_sorter(s)
            order_bys.extend(sorters)

        return order_bys, self

    def get_sorter(self, sorter):
        orders_by = []
        sort_dir = "-" if "-" in sorter else "+"
        sort_spe = "str_num" if "*" in sorter else "num_str" if "%" in sorter else None
        sort_field = re.sub(r"[+-\\*%]", "", sorter)

        model_attribute, self = self.Model().getModelAttr(sort_field, self)

        if model_attribute is None:
            raise Exception(f"Pb avec le tri {self.schema_code()}, field: {sort_field}")

        if sort_spe is not None:
            sort_string = sa.func.substring(model_attribute, "[a-zA-Z]+")
            sort_number = sa.cast(sa.unc.substring(model_attribute, "[0-9]+"), sa.Numeric)

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

    def process_query_columns(self, params, order_by):
        """
        permet d'ajouter de colonnes selon les besoin
        - scope pour cruved (toujours?)
        - row_number (si dans fields)
        """

        fields = params.get("fields") or []

        # cruved
        if "scope" in fields:
            self = self.add_column_scope()

        # row_number
        if "row_number" in fields:
            self = self.add_columns(
                sa.func.row_number().over(order_by=order_by).label("row_number")
            )

        return self

    def expression_scope(self):
        Model = self.Model()

        if self.attr("meta.check_cruved") is None:
            return sa.literal(0)
        else:
            return sa.case(
                [
                    (
                        sa.or_(
                            Model.actors.any(id_role=g.current_user.id_role),
                            Model.id_digitiser == g.current_user.id_role,
                        ),
                        1,
                    ),
                    (Model.actors.any(id_organism=g.current_user.id_organisme), 2),
                ],
                else_=3,
            )

    def add_column_scope(self, query):
        """
        ajout d'une colonne 'scope' à la requête
        afin de
            - filter dans la requete de liste
            - verifier les droit sur un donnée pour les action unitaire (post update delete)
            - le rendre accessible pour le frontend
                - affichage de boutton, vérification d'accès aux pages etc ....
        """

        query = query.add_columns(self.expression_scope().label("scope"))

        return query

    def process_cruved_filter(self, cruved_type, module_code):
        """ """

        if self.attr("meta.check_cruved") is None:
            return self

        if not hasattr(g, "current_user"):
            return self

        user_cruved = get_scopes_by_action(module_code=module_code)

        cruved_for_type = user_cruved.get(cruved_type)

        if cruved_for_type < 3:
            self = self.filter(self.expression_scope() <= cruved_for_type)

        return self
