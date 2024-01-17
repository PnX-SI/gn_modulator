"""
    SchemaMethods : sqlalchemy queries processing
"""

import math
import re
import copy
import sqlalchemy as sa
from geonature.utils.env import db

from gn_modulator import MODULE_CODE
from gn_modulator.query.repository import query_list
from gn_modulator.query.utils import pretty_sql
from . import errors


class SchemaRepositories:
    """
    class for sqlalchemy query processing
    """

    def value_filters(self, value, field_name=None):
        if not field_name:
            field_name = self.Model().pk_field_name()

        # value et field_name peuvent être des listes
        # pour la suite nous traitons tout comme des listes
        values = value if isinstance(value, list) else [value]
        field_names = field_name if isinstance(field_name, list) else [field_name]

        if len(values) != len(field_names):
            raise errors.SchemaRepositoryError(
                "get_row : les input value et field_name n" "ont pas la même taille"
            )

        value_filters = []
        # ici jouer sur filters avant le one
        for index, val in enumerate(values):
            f_name = field_names[index]
            value_filters.append({"field": f_name, "type": "=", "value": val})

        return value_filters

    def get_row(
        self,
        value,
        field_name=None,
        module_code=MODULE_CODE,
        action="R",
        params={},
        query_type="all",
    ):
        """
        return query get one row (Model.<field_name> == value)

        - value
        - field_name:
          - filter by <field_name>==value
          - if field_name is None, use primary key field name

        - value and field name can be arrays, they must be of same size


        db.session.query(Model).filter(<field_name> == value).one()
        """

        value_filters = self.value_filters(value, field_name)

        # patch pour ne pas se traîner le params précédent en param par defaut ??
        params_query = copy.deepcopy(params)
        params_query["filters"] = params_query.get("filters", []) + value_filters

        query = query_list(
            self.Model(),
            module_code=module_code,
            action=action,
            params=params_query,
            query_type=query_type,
        )

        return query

    def insert_row(self, data, authorized_write_fields=None, commit=True):
        """
        insert new row with data
        """

        if self.Model().pk_field_name() in data and data[self.Model().pk_field_name()] is None:
            data.pop(self.Model().pk_field_name())

        self.validate_data(data)
        m = self.Model()()
        self.unserialize(m, data, authorized_write_fields)
        db.session.add(m)
        db.session.flush()

        if commit:
            db.session.commit()

        return m

    def is_new_data(self, model, data):
        """
        for update_row
        test if data different from model
        """

        if model is None and data is not None:
            return True

        # data_fields = self.get_data_fields(data)
        # data_db = m = self.serialize(model, fields=fields)[key]

        if isinstance(data, dict) and not isinstance(model, dict):
            for key, data_value in data.items():
                if not hasattr(model, key):
                    continue
                fields = []
                if self.is_relation_1_n(key) or self.is_relation_n_n(key):
                    for item in data_value:
                        for k in item:
                            kk = f"{key}.{k}"
                            if kk not in fields and self.has_property(kk):
                                fields.append(kk)
                if len(fields) == 0:
                    fields = [key]

                m_ = self.serialize(model, fields=fields)
                m = m_[key]
                if self.is_new_data(m, data_value):
                    return True
            return False

        if isinstance(data, list):
            # test list
            if not isinstance(model, list):
                # raise error ?
                raise Exception("error list")

            # test taille
            if len(data) != len(model):
                return True

            # test s'il y a une correspondance pour chaque element
            for data_elem in data:
                is_new_data = True
                for model_elem in model:
                    if not is_new_data:
                        break
                    is_new_data = is_new_data and self.is_new_data(model_elem, data_elem)

                if is_new_data:
                    return True

            return False

        # element à element
        # pour les uuid la comparaison directe donne non egal en cas d'égalité
        # (pourquoi??) d'ou transformation en string pour la comparaison
        if isinstance(data, dict):
            model = {key: model[key] for key in data if key in model}
        if not (model == data or str(model) == str(data)):
            return True

        return False

    def update_row(
        self,
        value,
        data,
        field_name=None,
        module_code=MODULE_CODE,
        params={},
        authorized_write_fields=None,
        commit=True,
    ):
        """
        update row (Model.<field_name> == value) with data

        # TODO deserialiser
        """
        self.validate_data(data, check_required=False)

        q = self.get_row(
            value,
            field_name=field_name,
            module_code=module_code,
            action="U",
            params=params,
            query_type="update",
        )

        m = db.session.execute(q).unique().scalar_one()

        if not self.is_new_data(m, data):
            return m, False

        db.session.flush()
        self.unserialize(m, data, authorized_write_fields)

        if commit:
            db.session.commit()

        return m, True

    def delete_row(
        self,
        value,
        field_name=None,
        module_code=MODULE_CODE,
        params={},
        commit=True,
        multiple=False,
    ):
        """
        delete row (Model.<field_name> == value)
        """
        subquery_delete = self.get_row(
            value,
            field_name=field_name,
            module_code=module_code,
            action="D",
            params=params,
            query_type="delete",
        ).cte("pre_delete")

        Model = self.Model()
        table = Model.__table__
        q_delete = sa.delete(table).where(
            sa.and_(
                *map(
                    lambda x: getattr(table.c, x) == getattr(subquery_delete.c, x),
                    Model.pk_field_names(),
                )
            )
        )

        # patch pourris pourquoi sql ne met pas USING PDBDMSRMLGP???
        propper_sql_delete = str(q_delete.compile(compile_kwargs={"literal_binds": True})).replace(
            ", pre_delete", "USING pre_delete"
        )

        db.session.execute(
            sa.text(propper_sql_delete), execution_options={"synchronize_session": False}
        )
        # https://stackoverflow.com/questions/49794899/flask-sqlalchemy-delete-query-failing-with-could-not-evaluate-current-criteria?noredirect=1&lq=1
        # db.session.execute(q)
        # m.delete(synchronize_session=False)
        # db.session.flush()

        if commit:
            db.session.commit()
        return None

    def get_query_infos(self, module_code=MODULE_CODE, action="R", params={}, url=None):
        subquery_count_total = query_list(
            self.Model(),
            module_code=module_code,
            action=action,
            params=params,
            query_type="total",
        ).cte("count_total")
        count_total = db.session.execute(
            sa.select(sa.func.count()).select_from(subquery_count_total)
        ).scalar_one()

        if params.get("filters"):
            subquery_count_filtered = query_list(
                self.Model(),
                module_code=module_code,
                action=action,
                params=params,
                query_type="filtered",
            ).cte("count_filtered")

            count_filtered = db.session.execute(
                sa.select(sa.func.count()).select_from(subquery_count_filtered)
            ).scalar_one()
        else:
            count_filtered = count_total

        page = 1
        page_size = params.get("page_size")
        last_page = math.ceil(count_total / page_size) if page_size else 1
        url_next = ""
        url_previous = ""
        url_first = ""
        url_last = ""
        if params.get("page"):
            page = params.get("page") or 1

        if url:
            # supprimer
            url_base = re.sub("page=[0-9]&?", "", url)

            if "?" not in url_base:
                url_base += "?"

            url = url_base + "&page={page}"

            # if f"page={page}" not in url:
            #     preff = "&" if "?" in url else "?"
            #     url += f"{preff}page={page}"

            if page != 1:
                url_previous = url_base + f"&page={page -1}"

            if page != last_page:
                url_next = url_base + f"&page={page -1}"
            url_first = url_base + "&page=1"
            url_last = url_base + f"&page={last_page}"

        query_infos = {
            "page": page,
            "next": url_next,
            "previous": url_previous,
            "first": url_first,
            "last": url_last,
            "page_size": page_size,
            "total": count_total,
            "filtered": count_filtered,
            "last_page": last_page,
        }

        return query_infos

    def get_page_number(self, value, module_code, action, params):
        params["fields"] = ["row_number"]

        sub_query_list = query_list(
            self.Model(), module_code, action, params, "page_number"
        ).subquery()

        row_number = db.session.execute(
            sa.select(sub_query_list.c.row_number).where(
                getattr(sub_query_list.c, self.Model().pk_field_name()) == value
            )
        ).scalar_one()

        page_number = math.ceil(row_number / params.get("page_size"))

        return page_number
