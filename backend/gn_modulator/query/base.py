from sqlalchemy import orm
from flask_sqlalchemy import BaseQuery
from gn_modulator import MODULE_CODE


class BaseSchemaQuery(BaseQuery):
    def Model(self):
        return self._primary_entity.mapper.entity
