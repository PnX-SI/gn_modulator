"""concept usage objectif

Revision ID: 0f6b908cbe5e
Revises: ea2da3785c06
Create Date: 2023-08-04 16:05:35.209204

"""
from alembic import op
import sqlalchemy as sa
import pkg_resources

# revision identifiers, used by Alembic.
revision = "0f6b908cbe5e"
down_revision = "ea2da3785c06"
branch_labels = None
depends_on = None


def upgrade():
    operations = pkg_resources.resource_string(
        "m_sipaf.migrations", "data/schema_usage_objectifs.sql"
    ).decode("utf-8")
    op.get_bind().execute(sa.sql.text(operations))
    pass


def downgrade():
    op.execute(
        """
        DROP TABLE pr_sipaf.t_usages;
        DROP TABLE pr_sipaf.cor_pf_nomenclature_ouvrage_categorie;
    """
    )
    pass
