# modeles d'import
from flask import g
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from geonature.utils.env import db
from .mixins import ImportMixin
from sqlalchemy.ext.mutable import MutableDict, MutableList


class TMappingField(db.Model):
    __tablename__ = "t_mapping_field"
    __table_args__ = {"schema": "gn_modulator"}

    id_mapping_field = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, nullable=False)
    schema_code = db.Column(db.Unicode, nullable=False)
    value = db.Column(MutableDict.as_mutable(JSONB), nullable=False)


class TMappingValue(db.Model):
    __tablename__ = "t_mapping_value"
    __table_args__ = {"schema": "gn_modulator"}

    id_mapping_value = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, nullable=False)
    schema_code = db.Column(db.Unicode, nullable=False)
    value = db.Column(MutableDict.as_mutable(JSONB), nullable=False)


class TMapping(db.Model):
    __tablename__ = "t_mappings"
    __table_args__ = {"schema": "gn_modulator"}

    id_mapping = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, nullable=False)
    value = db.Column(db.Unicode, nullable=False)


class TImport(db.Model, ImportMixin):
    __tablename__ = "t_imports"
    __table_args__ = {"schema": "gn_modulator"}

    _columns = {}

    id_import = db.Column(db.Integer, primary_key=True)

    id_import_parent = db.Column(db.Integer, db.ForeignKey("gn_modulator.t_imports.id_import"))
    parent = db.relationship(
        "TImport", remote_side=[id_import], foreign_keys=[id_import_parent], backref="imports_1_n"
    )

    relation_key = db.Column(db.Unicode)

    id_digitiser = db.Column(db.Integer, db.ForeignKey("utilisateurs.t_roles.id_role"))

    id_mapping_field = db.Column(
        db.Integer, db.ForeignKey("gn_modulator.t_mapping_field.id_mapping_field")
    )
    mapping_field = db.relationship(TMappingField)

    id_mapping_value = db.Column(
        db.Integer, db.ForeignKey("gn_modulator.t_mapping_value.id_mapping_value")
    )
    mapping_value = db.relationship(TMappingValue)

    id_mapping = db.Column(db.Integer, db.ForeignKey("gn_modulator.t_mappings.id_mapping"))
    mapping = db.relationship(TMapping)

    module_code = db.Column(db.Unicode)
    object_code = db.Column(db.Unicode)
    schema_code = db.Column(db.Unicode)

    status = db.Column(db.Unicode)

    data_file_path = db.Column(db.Unicode)

    csv_delimiter = db.Column(db.Unicode)
    data_type = db.Column(db.Unicode)

    res = db.Column(MutableDict.as_mutable(JSONB), default=sa.text("'{}'"))
    tables = db.Column(MutableDict.as_mutable(JSONB), default=sa.text("'{}'"))
    sql = db.Column(MutableDict.as_mutable(JSONB), default=sa.text("'{}'"))
    errors = db.Column(MutableList.as_mutable(JSONB), default=[])
    options = db.Column(MutableDict.as_mutable(JSONB), default=sa.text("'{}'"))
    steps = db.Column(MutableDict.as_mutable(JSONB), default=sa.text("'{}'"))

    task_id = db.Column(db.Unicode)
