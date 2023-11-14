"""m_sipaf_actor_required_id_organism

Revision ID: 2c85080e9b8b
Revises: 0f6b908cbe5e
Create Date: 2023-10-19 14:02:45.162974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c85080e9b8b"
down_revision = "cc1cd6fbb28c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        f"""
    DELETE FROM pr_sipaf.cor_actor_pf WHERE id_organism IS NULL;
    ALTER TABLE pr_sipaf.cor_actor_pf ALTER id_organism SET NOT NULL;
    ALTER TABLE pr_sipaf.cor_actor_pf DROP COLUMN id_role CASCADE; // dependance avec les imports ???
    """
    )


def downgrade():
    pass
    op.execute(
        f"""
    ALTER TABLE pr_sipaf.cor_actor_pf ALTER id_organism DROP NOT NULL;
    ALTER TABLE pr_sipaf.cor_actor_pf ADD COLUMN id_role INTEGER;
    ALTER TABLE pr_sipaf.cor_actor_pf
    ADD CONSTRAINT fk_pr_sipaf_cor_a_t_rol_id_role FOREIGN KEY (id_role)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;
    """
    )
