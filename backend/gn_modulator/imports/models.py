# modeles d'import
from flask import g
from sqlalchemy.dialects.postgresql import JSONB
from geonature.utils.env import db
from .mixins import ImportMixin


class TImport(db.Model, ImportMixin):
    __tablename__ = "t_imports"
    __table_args__ = {"schema": "gn_modulator"}

    def __init__(
        self, schema_code=None, data_file_path=None, mapping_file_path=None, _insert_data=False
    ):
        self.id_digitiser = g.current_user.id_role if hasattr(g, "current_user") else None

        self.schema_code = schema_code
        self.data_file_path = data_file_path and str(data_file_path)
        self.mapping_file_path = mapping_file_path and str(mapping_file_path)

        self._insert = _insert_data

        self.res = {}
        self.errors = []
        self.sql = {}
        self.tables = {}

    _insert_data = False
    _columns = {}

    id_import = db.Column(db.Integer, primary_key=True)

    id_digitiser = db.Column(db.Integer, db.ForeignKey("utilisateurs.t_roles.id_role"))
    schema_code = db.Column(db.Unicode)

    data_file_path = db.Column(db.Unicode)
    mapping_file_path = db.Column(db.Unicode)

    csv_delimiter = db.Column(db.Unicode)
    data_type = db.Column(db.Unicode)

    res = db.Column(JSONB)
    tables = db.Column(JSONB)
    sql = db.Column(JSONB)
    errors = db.Column(JSONB)

    def as_dict(self):
        return {
            "id_import": self.id_import,
            "id_digitiser": self.id_digitiser,
            "data_type": self.data_type,
            "csv_delimiter": self.csv_delimiter,
            "res": self.res,
            "errors": self.errors,
        }
