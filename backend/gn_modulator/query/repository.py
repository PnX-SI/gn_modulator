from sqlalchemy import orm
from gn_modulator import MODULE_CODE
from .base import BaseSchemaQuery
from .field import FieldSchemaQuery
from .utils import SchemaQueryUtils
from .filters import SchemaQueryFilters
from .permission import SchemaQueryPermission


class RepositorySchemaQuery(
    SchemaQueryPermission, SchemaQueryFilters, SchemaQueryUtils, FieldSchemaQuery, BaseSchemaQuery
):
    def query_list(self, module_code, action, params, query_type, id_role=None):
        Model = self.Model()
        model_pk_fields = [
            getattr(Model, pk_field_name) for pk_field_name in Model.pk_field_names()
        ]

        self = self.options(orm.load_only(*model_pk_fields))

        if query_type not in ["update", "delete"]:
            self = self.distinct()

        self = self.process_fields(params.get("fields") or [])

        # clear_query_cache
        self.clear_query_cache()

        order_bys, self = self.get_sorters(params.get("sort", []))

        # ajout colonnes row_number, scope (cruved)
        self = self.process_query_columns(params, order_bys, id_role)

        # - prefiltrage permissions (CRUVED sensibilité etc)
        self = self.process_filter_permission(id_role, action, module_code)

        # - prefiltrage params
        self = self.process_filters(params.get("prefilters", []))

        if query_type == "total":
            return self.with_entities(*model_pk_fields).group_by(*model_pk_fields)

        # filtrage
        self = self.process_filters(params.get("filters", []))

        # requete pour count 'filtered'
        if query_type == "filtered":
            return self.with_entities(*model_pk_fields).group_by(*model_pk_fields)

        if query_type in ["update", "delete", "page_number"]:
            return self

        # raise load
        self = self.options(orm.raiseload("*"))

        # sort
        self = self.order_by(*(tuple(order_bys)))

        # limit offset
        self = self.process_page_size(params.get("page"), params.get("page_size"))

        return self
