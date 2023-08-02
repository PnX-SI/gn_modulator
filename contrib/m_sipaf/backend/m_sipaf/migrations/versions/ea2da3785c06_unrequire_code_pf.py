"""unrequire code pf pr_sipaf.t_passages_faune.code_passage_faune

Revision ID: ea2da3785c06
Revises: 90f6e5531f7c
Create Date: 2023-06-27 16:18:12.462599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ea2da3785c06"
down_revision = "90f6e5531f7c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE pr_sipaf.t_passages_faune ALTER COLUMN code_passage_faune DROP NOT NULL;
        ALTER TABLE pr_sipaf.t_passages_faune DROP CONSTRAINT unique_pr_sipaf_t_passages_faune_code_passage_faune;
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE pr_sipaf.t_passages_faune ALTER COLUMN code_passage_faune SET NOT NULL;
        ALTER TABLE pr_sipaf.t_passages_faune ADD CONSTRAINT unique_pr_sipaf_t_passages_faune_code_passage_faune UNIQUE(code_passage_faune);
        """
    )
