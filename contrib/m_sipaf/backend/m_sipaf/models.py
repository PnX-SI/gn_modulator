import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import column_property, backref
from sqlalchemy import (
    func,
    literal,
    select,
    exists,
    and_,
    literal_column,
    cast,
)
from geoalchemy2 import Geometry

from geonature.utils.env import db

from geonature.core.gn_commons.models import TMedias
from pypnusershub.db.models import User, Organisme
from pypnnomenclature.models import TNomenclatures
from ref_geo.models import LAreas, LLinears, BibAreasTypes, BibLinearsTypes


class CorPfNomenclatureOuvrageType(db.Model):
    __tablename__ = "cor_pf_nomenclature_ouvrage_type"
    __table_args__ = {"schema": "pr_sipaf"}

    id_passage_faune = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_passages_faune.id_passage_faune"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorPfNomenclatureOuvrageMateriaux(db.Model):
    __tablename__ = "cor_pf_nomenclature_ouvrage_materiaux"
    __table_args__ = {"schema": "pr_sipaf"}

    id_passage_faune = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_passages_faune.id_passage_faune"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorPfNomenclatureOuvrageCategorie(db.Model):
    __tablename__ = "cor_pf_nomenclature_ouvrage_categorie"
    __table_args__ = {"schema": "pr_sipaf"}

    id_passage_faune = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_passages_faune.id_passage_faune"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorPfArea(db.Model):
    __tablename__ = "cor_area_pf"
    __table_args__ = {"schema": "pr_sipaf"}

    id_passage_faune = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_passages_faune.id_passage_faune"), primary_key=True
    )
    id_area = db.Column(db.Integer, db.ForeignKey("ref_geo.l_areas.id_area"), primary_key=True)


class CorPfLinear(db.Model):
    __tablename__ = "cor_linear_pf"
    __table_args__ = {"schema": "pr_sipaf"}

    id_passage_faune = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_passages_faune.id_passage_faune"), primary_key=True
    )
    id_linear = db.Column(
        db.Integer, db.ForeignKey("ref_geo.l_linears.id_linear"), primary_key=True
    )


class PassageFaune(db.Model):
    __tablename__ = "t_passages_faune"
    __table_args__ = {"schema": "pr_sipaf"}

    id_passage_faune = db.Column(db.Integer, primary_key=True)

    uuid_passage_faune = db.Column(UUID(as_uuid=True), default=uuid.uuid4)

    id_digitiser = db.Column(db.Integer, db.ForeignKey("utilisateurs.t_roles.id_role"))
    digitiser = db.relationship(User)

    pi_ou_ps = db.Column(db.Boolean)

    geom = db.Column(Geometry("GEOMETRY", 4326), nullable=False)
    geom_local = db.Column(Geometry("GEOMETRY"))

    pk = db.Column(db.Float)
    pr = db.Column(db.Float)
    pr_abs = db.Column(db.Integer)

    code_ouvrage_gestionnaire = db.Column(db.Unicode)

    nom_usuel_passage_faune = db.Column(db.Unicode)

    issu_requalification = db.Column(db.Boolean)

    date_creation_ouvrage = db.Column(db.Date)
    date_requalification_ouvrage = db.Column(db.Date)

    largeur_ouvrage = db.Column(db.Float)
    hauteur_ouvrage = db.Column(db.Float)
    longueur_franchissement = db.Column(db.Float)
    diametre = db.Column(db.Float)
    largeur_dispo_faune = db.Column(db.Float)
    hauteur_dispo_faune = db.Column(db.Float)

    id_nomenclature_ouvrage_specificite = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_ouvrage_specificite = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_ouvrage_specificite]
    )

    nomenclatures_ouvrage_type = db.relationship(
        TNomenclatures, secondary=CorPfNomenclatureOuvrageType.__table__
    )
    ouvrage_type_autre = db.Column(db.Unicode)

    nomenclatures_ouvrage_materiaux = db.relationship(
        TNomenclatures, secondary=CorPfNomenclatureOuvrageMateriaux.__table__
    )

    nomenclatures_ouvrage_categorie = db.relationship(
        TNomenclatures, secondary=CorPfNomenclatureOuvrageCategorie.__table__
    )

    ouvrage_hydrau = db.Column(db.Boolean)

    id_nomenclature_ouvrage_hydrau_position = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_ouvrage_hydrau_position = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_ouvrage_hydrau_position]
    )

    id_nomenclature_ouvrage_hydrau_banq_caract = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_ouvrage_hydrau_banq_caract = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_ouvrage_hydrau_banq_caract]
    )

    id_nomenclature_ouvrage_hydrau_banq_type = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_ouvrage_hydrau_banq_type = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_ouvrage_hydrau_banq_type]
    )

    ouvrag_hydrau_tirant_air = db.Column(db.Float)

    source = db.Column(db.Unicode)

    meta_create_date = db.Column(
        db.DateTime,
    )
    meta_update_date = db.Column(db.DateTime)

    areas = db.relationship(LAreas, secondary=CorPfArea.__table__)
    linears = db.relationship(LLinears, secondary=CorPfLinear.__table__)

    medias = db.relationship(
        TMedias,
        primaryjoin=TMedias.uuid_attached_row == uuid_passage_faune,
        foreign_keys=[TMedias.uuid_attached_row],
        cascade="all",
        lazy="select",
    )

    # actors
    actors = db.relationship("Actor", cascade="all,delete,delete-orphan")

    # columns properties
    geom_x = column_property(func.st_x(func.st_centroid(geom)))
    geom_y = column_property(func.st_y(func.st_centroid(geom)))
    geom_text = column_property(func.st_astext(geom))

    label_infrastructures = column_property(
        select([func.string_agg(LLinears.linear_name, literal_column("', '"))]).where(
            and_(
                CorPfLinear.id_passage_faune == id_passage_faune,
                CorPfLinear.id_linear == LLinears.id_linear,
            )
        )
    )

    label_communes = column_property(
        select([func.string_agg(LAreas.area_name, literal_column("', '"))]).where(
            and_(
                CorPfArea.id_passage_faune == id_passage_faune,
                CorPfArea.id_area == LAreas.id_area,
                BibAreasTypes.id_type == LAreas.id_type,
                BibAreasTypes.type_code == "COM",
            )
        )
    )

    label_departements = column_property(
        select([func.string_agg(LAreas.area_name, literal_column("', '"))]).where(
            and_(
                CorPfArea.id_passage_faune == id_passage_faune,
                CorPfArea.id_area == LAreas.id_area,
                BibAreasTypes.id_type == LAreas.id_type,
                BibAreasTypes.type_code == "DEP",
            )
        )
    )

    label_regions = column_property(
        select([func.string_agg(LAreas.area_name, literal_column("', '"))]).where(
            and_(
                CorPfArea.id_passage_faune == id_passage_faune,
                CorPfArea.id_area == LAreas.id_area,
                BibAreasTypes.id_type == LAreas.id_type,
                BibAreasTypes.type_code == "REG",
            )
        )
    )


class Actor(db.Model):
    __tablename__ = "cor_actor_pf"
    __table_args__ = {"schema": "pr_sipaf"}

    id_actor = db.Column(db.Integer, primary_key=True)

    id_passage_faune = db.Column(
        db.Integer,
        db.ForeignKey(
            "pr_sipaf.t_passages_faune.id_passage_faune",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    passage_faune = db.relationship(PassageFaune)

    id_role = db.Column(db.Integer, db.ForeignKey("utilisateurs.t_roles.id_role"))
    role = db.relationship(User)

    id_organism = db.Column(db.Integer, db.ForeignKey("utilisateurs.bib_organismes.id_organisme"))
    organisme = db.relationship(Organisme)

    id_nomenclature_type_actor = db.Column(
        db.Integer,
        db.ForeignKey(
            "ref_nomenclatures.t_nomenclatures.id_nomenclature",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    nomenclature_type_actor = db.relationship(TNomenclatures)


class CorDiagObstacle(db.Model):
    __tablename__ = "cor_diag_nomenclature_obstacle"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorDiagPerturbation(db.Model):
    __tablename__ = "cor_diag_nomenclature_perturbation"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorDiagOuvrageHydrauEtatBerge(db.Model):
    __tablename__ = "cor_diag_nomenclature_ouvrage_hydrau_etat_berge"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorDiagOuvrageHydrauDim(db.Model):
    __tablename__ = "cor_diag_nomenclature_ouvrage_hydrau_dim"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class CorDiagAmenagementBiodiv(db.Model):
    __tablename__ = "cor_diag_nomenclature_amenagement_biodiv"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )


class Diagnostic(db.Model):
    __tablename__ = "t_diagnostics"
    __table_args__ = {"schema": "pr_sipaf"}

    # communs
    id_diagnostic = db.Column(db.Integer, primary_key=True)
    date_diagnostic = db.Column(db.Date, nullable=False)
    commentaire_diagnostic = db.Column(db.Unicode)

    id_passage_faune = db.Column(
        db.Integer,
        db.ForeignKey(
            "pr_sipaf.t_passages_faune.id_passage_faune",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    passage_faune = db.relationship(
        PassageFaune, backref=backref("diagnostics", cascade="all,delete,delete-orphan")
    )

    id_role = db.Column(db.Integer, db.ForeignKey("utilisateurs.t_roles.id_role"))
    role = db.relationship(User)

    id_organisme = db.Column(db.Integer, db.ForeignKey("utilisateurs.bib_organismes.id_organisme"))
    organisme = db.relationship(Organisme)

    # perturbation / obstacle

    commentaire_perturbation_obstacle = db.Column(db.Unicode)
    obstacle_autre = db.Column(db.Unicode)
    perturbation_autre = db.Column(db.Unicode)

    id_nomenclature_ouvrage_hydrau_racc_banq = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_ouvrage_hydrau_racc_banq = db.relationship(
        TNomenclatures,
        foreign_keys=[id_nomenclature_ouvrage_hydrau_racc_banq],
    )

    nomenclatures_diagnostic_obstacle = db.relationship(
        TNomenclatures, secondary=CorDiagObstacle.__table__
    )

    nomenclatures_diagnostic_perturbation = db.relationship(
        TNomenclatures, secondary=CorDiagPerturbation.__table__
    )

    nomenclatures_diagnostic_ouvrage_hydrau_etat_berge = db.relationship(
        TNomenclatures, secondary=CorDiagOuvrageHydrauEtatBerge.__table__
    )

    nomenclatures_diagnostic_ouvrage_hydrau_dim = db.relationship(
        TNomenclatures, secondary=CorDiagOuvrageHydrauDim.__table__
    )

    # Amenagements
    amenagement_biodiv_autre = db.Column(db.Unicode)

    nomenclatures_diagnostic_amenagement_biodiv = db.relationship(
        TNomenclatures, secondary=CorDiagAmenagementBiodiv.__table__
    )

    id_nomenclature_amenagement_entretient = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_amenagement_entretient = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_amenagement_entretient]
    )

    commentaire_amenagement = db.Column(db.Unicode)

    # synthese
    id_nomenclature_interet_petite_faune = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_interet_petite_faune = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_interet_petite_faune]
    )

    id_nomenclature_interet_grande_faune = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_interet_grande_faune = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_interet_grande_faune]
    )

    id_nomenclature_franchissabilite = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    nomenclature_franchissabilite = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_franchissabilite]
    )

    amenagement_faire = db.Column(db.Unicode)
    commentaire_synthese = db.Column(db.Unicode)


class DiagnosticCloture(db.Model):
    __tablename__ = "t_diagnostic_clotures"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature_clotures_guidage_type = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
        nullable=False,
    )
    id_nomenclature_clotures_guidage_etat = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        nullable=False,
    )

    clotures_guidage_type_autre = db.Column(db.Unicode)
    clotures_guidage_etat_autre = db.Column(db.Unicode)

    diagnostic = db.relationship(
        Diagnostic, backref=backref("clotures", cascade="all,delete,delete-orphan")
    )

    nomenclature_clotures_guidage_etat = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_clotures_guidage_etat]
    )
    nomenclature_clotures_guidage_type = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_clotures_guidage_type]
    )


class DiagnosticVegetationTablier(db.Model):
    __tablename__ = "t_diagnostic_vegetation_presente_tablier"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature_vegetation_type = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
        nullable=False,
    )
    id_nomenclature_vegetation_couvert = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        nullable=False,
    )

    diagnostic = db.relationship(
        Diagnostic, backref=backref("vegetation_tablier", cascade="all,delete,delete-orphan")
    )

    nomenclature_vegetation_type = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_vegetation_type]
    )

    nomenclature_vegetation_couvert = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_vegetation_couvert]
    )


class DiagnosticVegetationDebouche(db.Model):
    __tablename__ = "t_diagnostic_vegetation_presente_debouche"
    __table_args__ = {"schema": "pr_sipaf"}

    id_diagnostic = db.Column(
        db.Integer, db.ForeignKey("pr_sipaf.t_diagnostics.id_diagnostic"), primary_key=True
    )
    id_nomenclature_vegetation_type = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
        nullable=False,
    )
    id_nomenclature_vegetation_couvert = db.Column(
        db.Integer,
        db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        nullable=False,
    )

    diagnostic = db.relationship(
        Diagnostic, backref=backref("vegetation_debouche", cascade="all,delete,delete-orphan")
    )

    nomenclature_vegetation_type = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_vegetation_type]
    )

    nomenclature_vegetation_couvert = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_vegetation_couvert]
    )


class Usage(db.Model):
    __tablename__ = "t_usages"
    __table_args__ = {"schema": "pr_sipaf"}

    id_usage = db.Column(db.Integer, primary_key=True)

    detail_usage = db.Column(db.Unicode)

    commentaire = db.Column(db.Unicode)

    id_passage_faune = db.Column(
        db.Integer,
        db.ForeignKey(
            "pr_sipaf.t_passages_faune.id_passage_faune",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )

    passage_faune = db.relationship(
        PassageFaune, backref=backref("usages", cascade="all,delete,delete-orphan")
    )

    id_nomenclature_usage_type = db.Column(
        db.Integer, db.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )

    nomenclature_usage_type = db.relationship(
        TNomenclatures, foreign_keys=[id_nomenclature_usage_type]
    )
