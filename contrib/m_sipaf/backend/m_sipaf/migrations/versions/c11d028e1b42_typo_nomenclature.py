"""typo_nomenclature

Revision ID: c11d028e1b42
Revises: b7eb2e900bf1
Create Date: 2024-01-09 20:29:26.613697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c11d028e1b42"
down_revision = "7664e8f989f1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """

    ALTER TABLE pr_sipaf.t_diagnostics
        DROP CONSTRAINT check_nom_type_diag_amenagement_entretient;

    ALTER TABLE pr_sipaf.t_diagnostics
        RENAME COLUMN id_nomenclature_amenagement_entretient
         TO id_nomenclature_amenagement_entretien;

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT check_nom_type_diag_amenagement_entretien CHECK (
            ref_nomenclatures.check_nomenclature_type_by_mnemonique(
                id_nomenclature_amenagement_entretien,
                'PF_DIAG_AMENAGEMENT_ENTRETIEN'
            )
        ) NOT VALID;

    """
    )


def downgrade():
    op.execute(
        """

    ALTER TABLE pr_sipaf.t_diagnostics
        DROP CONSTRAINT check_nom_type_diag_amenagement_entretien;

    ALTER TABLE pr_sipaf.t_diagnostics
        RENAME COLUMN id_nomenclature_amenagement_entretien
         TO id_nomenclature_amenagement_entretient;

    ALTER TABLE pr_sipaf.t_diagnostics
        ADD CONSTRAINT check_nom_type_diag_amenagement_entretient CHECK (
            ref_nomenclatures.check_nomenclature_type_by_mnemonique(
                id_nomenclature_amenagement_entretient,
                'PF_DIAG_AMENAGEMENT_ENTRETIENT'
            )
        ) NOT VALID;

    """
    )
