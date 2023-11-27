from sqlalchemy import orm
from flask_sqlalchemy import BaseQuery
from .getattr import _getModelAttr, _clear_query_cache, _get_query_cache
import sqlparse


class BaseSchemaQuery(BaseQuery):
    def Model(self):
        return self._primary_entity.mapper.entity

    def getModelAttr(
        self,
        Model,
        field_name,
        only_fields="",
        index=0,
    ):
        return _getModelAttr(self, Model, field_name, only_fields=only_fields, index=index)

    def clear_query_cache(self):
        return _clear_query_cache(self)

    def get_query_cache(self, key):
        return _get_query_cache(self, key)

    def sql_txt(self):
        txt = str(self.statement.compile(compile_kwargs={"literal_binds": True}))
        txt = txt.replace("%%", "%")
        txt = sqlparse.format(txt, reindent=True, keywordcase="upper")
        return txt
