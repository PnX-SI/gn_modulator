"""ajout commentaire passage faune

Revision ID: 7664e8f989f1
Revises: b7eb2e900bf1
Create Date: 2024-01-09 18:22:22.097781

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7664e8f989f1"
down_revision = "b7eb2e900bf1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        f"""
    ALTER TABLE pr_sipaf.t_passages_faune ADD COLUMN commentaires VARCHAR;
    """
    )


def downgrade():
    op.execute(
        f"""
    ALTER TABLE pr_sipaf.t_passages_faune DROP COLUMN commentaires;
    """
    )
