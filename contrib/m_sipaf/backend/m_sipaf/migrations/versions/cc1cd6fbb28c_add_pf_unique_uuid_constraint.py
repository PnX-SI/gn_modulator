"""add pf unique uuid constraint

Revision ID: cc1cd6fbb28c
Revises: 0f6b908cbe5e
Create Date: 2023-10-12 11:38:15.137738

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cc1cd6fbb28c"
down_revision = "0f6b908cbe5e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
ALTER TABLE pr_sipaf.t_passages_faune ADD CONSTRAINT unique_pr_sipaf_t_passages_faune_uuid_passage_faune UNIQUE (uuid_passage_faune);
    """
    )


def downgrade():
    op.execute(
        """
ALTER TABLE pr_sipaf.t_passages_faune DROP CONSTRAINT unique_pr_sipaf_t_passages_faune_uuid_passage_faune;
    """
    )
