"""remove objectifs taxons

Revision ID: b7eb2e900bf1
Revises: 2c85080e9b8b
Create Date: 2023-11-14 16:50:11.560175

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7eb2e900bf1"
down_revision = "2c85080e9b8b"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP TABLE pr_sipaf.cor_pf_taxref;
    """
    )


def downgrade():
    op.execute(
        """
    -- passage faune taxref


    CREATE TABLE IF NOT EXISTS pr_sipaf.cor_pf_taxref (
    id_passage_faune INTEGER NOT NULL NOT NULL,
    cd_nom INTEGER NOT NULL NOT NULL
);

    ---- pr_sipaf.cor_pf_taxref primary keys contraints

    ALTER TABLE pr_sipaf.cor_pf_taxref
        ADD CONSTRAINT pk_pr_sipaf_cor_pf_taxref_id_pf_id_nom PRIMARY KEY (id_passage_faune, cd_nom);

    ---- pr_sipaf.cor_pf_taxref foreign keys contraints

    ALTER TABLE pr_sipaf.cor_pf_taxref
        ADD CONSTRAINT fk_pr_sipaf_cor_pf_taxref_id_passage_faune FOREIGN KEY (id_passage_faune)
        REFERENCES pr_sipaf.t_passages_faune (id_passage_faune)
        ON UPDATE CASCADE ON DELETE CASCADE;

    ALTER TABLE pr_sipaf.cor_pf_taxref
        ADD CONSTRAINT fk_pr_sipaf_cor_pf_taxref_cd_nom FOREIGN KEY (cd_nom)
        REFERENCES taxonomie.taxref (cd_nom)
        ON UPDATE CASCADE ON DELETE CASCADE;
    """
    )
