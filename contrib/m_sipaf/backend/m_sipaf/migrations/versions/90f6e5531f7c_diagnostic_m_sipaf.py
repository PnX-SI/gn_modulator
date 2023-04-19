"""Diagnostics passage faune

Revision ID: 90f6e5531f7c
Revises: ec6ebeb214b1
Create Date: 2023-03-21 22:36:24.415201

"""
from alembic import op
import sqlalchemy as sa
import pkg_resources
from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "90f6e5531f7c"
down_revision = "ec6ebeb214b1"
branch_labels = None
depends_on = None


def upgrade():
    operations = pkg_resources.resource_string(
        "m_sipaf.migrations", "data/schema_diagnostic.sql"
    ).decode("utf-8")
    op.get_bind().execute(text(operations))
    pass


def downgrade():
    if_exists = ""
    # if_exists = "IF EXISTS"
    op.execute(
        f"""
    DROP TABLE {if_exists} pr_sipaf.cor_diag_nomenclature_obstacle;
    DROP TABLE {if_exists} pr_sipaf.cor_diag_nomenclature_perturbation;
    DROP TABLE {if_exists} pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_etat_berge;
    DROP TABLE {if_exists} pr_sipaf.cor_diag_nomenclature_ouvrage_hydrau_dim;
    DROP TABLE {if_exists} pr_sipaf.cor_diag_nomenclature_amenagement_biodiv;
    DROP TABLE {if_exists} pr_sipaf.t_diagnostic_clotures;
    DROP TABLE {if_exists} pr_sipaf.t_diagnostics;
    """
    )
    pass
