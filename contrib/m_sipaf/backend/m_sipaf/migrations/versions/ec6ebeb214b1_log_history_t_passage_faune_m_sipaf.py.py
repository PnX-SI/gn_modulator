"""log pr_sipaf.t_passage_faunes history and meta dates

Revision ID: ec6ebeb214b1
Revises: ecde20d34f25
Create Date: 2023-03-08 18:21:26.724733

"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ec6ebeb214b1"
down_revision = "ecde20d34f25"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE TRIGGER tri_log_changes_t_passages_faune
    AFTER INSERT OR UPDATE OR DELETE
    ON pr_sipaf.t_passages_faune
    FOR EACH ROW
    EXECUTE PROCEDURE gn_commons.fct_trg_log_changes();

    ALTER TABLE pr_sipaf.t_passages_faune ADD COLUMN meta_create_date timestamp without time zone DEFAULT now();
    ALTER TABLE pr_sipaf.t_passages_faune ADD COLUMN meta_update_date timestamp without time zone DEFAULT now();

    CREATE TRIGGER tri_meta_dates_change_t_passages_faune
        BEFORE INSERT OR UPDATE
        ON pr_sipaf.t_passages_faune
        FOR EACH ROW
        EXECUTE PROCEDURE public.fct_trg_meta_dates_change();

"""
    )
    pass


def downgrade():
    op.execute(
        """
    DROP TRIGGER IF EXISTS tri_log_changes_t_passages_faune
        ON pr_sipaf.t_passages_faune;

    ALTER TABLE pr_sipaf.t_passages_faune DROP COLUMN meta_create_date;
    ALTER TABLE pr_sipaf.t_passages_faune DROP COLUMN meta_update_date;

    DROP TRIGGER IF EXISTS tri_meta_dates_change_t_passages_faune ON pr_sipaf.t_passages_faune;
    """
    )
    pass
