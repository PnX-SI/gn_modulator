# modeles d'import
from geonature.utils.env import db
from sqlalchemy.dialects.postgresql import JSONB
from .mixins import ImportMixin


class TImport(db.Model, ImportMixin):
    __tablename__ = "t_imports"
    __table_args__ = {"schema": "gn_modulator"}

    def __init__(self, schema_code=None, data_file_path=None, mapping_file_path=None, _insert=False):
        self.schema_code = schema_code
        self.data_file_path = data_file_path and str(data_file_path)
        self.mapping_file_path = mapping_file_path and str(mapping_file_path)
        self._insert = _insert
        self.res = {}
        self.errors = []
        self.sql = {}
        self.tables = {}

    _insert = False

    id_import = db.Column(db.Integer, primary_key=True)

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
            "data_type": self.data_type,
            "csv_delimiter": self.csv_delimiter,
            "res": self.res,
            "errors": self.errors,
        }
