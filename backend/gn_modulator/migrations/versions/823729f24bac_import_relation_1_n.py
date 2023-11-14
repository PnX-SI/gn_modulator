"""import relation 1 n

Revision ID: 823729f24bac
Revises: b78eaab0a6e3
Create Date: 2023-10-09 15:55:41.769219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "823729f24bac"
down_revision = "b78eaab0a6e3"
branch_labels = None
depends_on = None


def upgrade():
    # ajout de variables à la table gn_modulator.t_imports
    # pour les import des relations 1-n
    # - id_import_parent
    # - relation_key
    # - task_id pour l'api import asynchrone
    op.execute(
        """
        ALTER TABLE gn_modulator.t_imports ADD COLUMN relation_key VARCHAR;
        ALTER TABLE gn_modulator.t_imports ADD COLUMN id_import_parent INTEGER;
        ALTER TABLE gn_modulator.t_imports ADD COLUMN steps JSONB;
        ALTER TABLE gn_modulator.t_imports ADD COLUMN task_id VARCHAR;
        ALTER TABLE gn_modulator.t_imports
            ADD CONSTRAINT fk_gn_modulator_t_imports_id_import_parent FOREIGN KEY (id_import_parent)
            REFERENCES gn_modulator.t_imports (id_import)
            ON UPDATE CASCADE ON DELETE CASCADE;
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE gn_modulator.t_imports DROP COLUMN relation_key;
        ALTER TABLE gn_modulator.t_imports DROP COLUMN id_import_parent;
        ALTER TABLE gn_modulator.t_imports DROP COLUMN steps;
    """
    )
