from geonature.utils.env import db
from geonature.core.gn_commons.models import TModules


cor_module_groups = db.Table(
    "cor_module_groupe",
    db.Column(
        "id_module",
        db.Integer,
        db.ForeignKey("gn_commons.t_modules.id_module"),
        primary_key=True,
    ),
    db.Column(
        "id_module_group",
        db.Integer,
        db.ForeignKey("gn_modulator.t_module_groups.id_module_group"),
        primary_key=True,
    ),
    schema="gn_modulator",
)

cor_module_tags = db.Table(
    "cor_module_tag",
    db.Column(
        "id_module",
        db.Integer,
        db.ForeignKey("gn_commons.t_modules.id_module"),
        primary_key=True,
    ),
    db.Column(
        "id_module_tag",
        db.Integer,
        db.ForeignKey("gn_modulator.t_module_tags.id_module_tag"),
        primary_key=True,
    ),
    schema="gn_modulator",
)


class ModuleGroups(db.Model):
    __tablename__ = "t_module_groups"
    __table_args__ = {"schema": "gn_modulator"}

    id_module_group = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    modules = db.relationship(TModules, secondary=cor_module_groups, backref="groups")


class ModuleTags(db.Model):
    __tablename__ = "t_module_tags"
    __table_args__ = {"schema": "gn_modulator"}

    id_module_tag = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    modules = db.relationship(TModules, secondary=cor_module_tags, backref="tags")
