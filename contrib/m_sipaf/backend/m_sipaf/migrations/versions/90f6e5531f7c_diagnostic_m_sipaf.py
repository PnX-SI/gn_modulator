"""Diagnostics passage faune

Revision ID: 90f6e5531f7c
Revises: ec6ebeb214b1
Create Date: 2023-03-21 22:36:24.415201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "90f6e5531f7c"
down_revision = "ec6ebeb214b1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE TABLE pr_sipaf.t_diagnostics (
        id_diagnostic SERIAL NOT NULL,
        id_passage_faune INTEGER NOT NULL,
        id_role INTEGER,
        id_organisme INTEGER,
        date_diagnostic DATE
    );

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT pk_sipaf_t_diagnostic_id_diagnostic PRIMARY KEY (id_diagnostic);

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT fk_sipaf_t_diag_t_pf_id_passage_faune FOREIGN KEY (id_passage_faune)
        REFERENCES pr_sipaf.t_passages_faune(id_passage_faune)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT fk_sipaf_t_diag_t_rol_id_role FOREIGN KEY (id_role)
        REFERENCES utilisateurs.t_roles(id_role)
        ON UPDATE CASCADE ON DELETE SET NULL;

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT fk_sipaf_t_diag_b_org_id_organisme FOREIGN KEY (id_organisme)
        REFERENCES utilisateurs.bib_organismes(id_organisme)
        ON UPDATE CASCADE ON DELETE SET NULL;

    """
    )
    pass


def downgrade():
    op.execute(
        """
    DROP TABLE pr_sipaf.t_diagnostics CASCADE;
    """
    )
    pass
