"""import mapping

Revision ID: 5c1ec86a67ab
Revises: 823729f24bac
Create Date: 2023-12-15 14:20:55.639520

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c1ec86a67ab"
down_revision = "823729f24bac"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    ALTER TABLE gn_modulator.t_imports DROP COLUMN mapping_file_path;
    ALTER TABLE gn_modulator.t_imports DROP COLUMN mapping;

    CREATE TABLE gn_modulator.t_mapping_field(
        id_mapping_field SERIAL NOT NULL PRIMARY KEY,
        code VARCHAR NOT NULL,
        schema_code VARCHAR NOT NULL,
        value JSONB NOT NULL,

        UNIQUE(code)
    );
    ALTER TABLE gn_modulator.t_imports ADD COLUMN id_mapping_field INTEGER;
    ALTER TABLE gn_modulator.t_imports
        ADD CONSTRAINT fk_mod_t_impts_id_mapping_field FOREIGN KEY(id_mapping_field)
        REFERENCES gn_modulator.t_mapping_field(id_mapping_field)
        ON UPDATE CASCADE ON DELETE SET NULL;


    CREATE TABLE gn_modulator.t_mapping_value(
        id_mapping_value SERIAL NOT NULL PRIMARY KEY,
        code VARCHAR NOT NULL,
        schema_code VARCHAR NOT NULL,
        value JSONB NOT NULL,

        UNIQUE(code)
    );
    ALTER TABLE gn_modulator.t_imports ADD COLUMN id_mapping_value INTEGER;
    ALTER TABLE gn_modulator.t_imports
        ADD CONSTRAINT fk_mod_t_impts_id_mapping_value FOREIGN KEY(id_mapping_value)
        REFERENCES gn_modulator.t_mapping_value(id_mapping_value)
        ON UPDATE CASCADE ON DELETE SET NULL;

    CREATE TABLE gn_modulator.t_mappings(
        id_mapping SERIAL NOT NULL PRIMARY KEY,
        code VARCHAR NOT NULL,
        schema_code VARCHAR NOT NULL,
        value JSONB NOT NULL,

        UNIQUE(code)
    );
    ALTER TABLE gn_modulator.t_imports ADD COLUMN id_mapping INTEGER;
    ALTER TABLE gn_modulator.t_imports
        ADD CONSTRAINT fk_mod_t_impts_id_mapping FOREIGN KEY(id_mapping)
        REFERENCES gn_modulator.t_mappings(id_mapping)
        ON UPDATE CASCADE ON DELETE SET NULL;

   """
    )


def downgrade():
    op.execute(
        """
    ALTER TABLE gn_modulator.t_imports ADD COLUMN mapping_file_path VARCHAR;
    ALTER TABLE gn_modulator.t_imports ADD COLUMN mapping VARCHAR;

    ALTER TABLE gn_modulator.t_imports DROP COLUMN id_mapping_value;
    ALTER TABLE gn_modulator.t_imports DROP COLUMN id_mapping_field;
    ALTER TABLE gn_modulator.t_imports DROP COLUMN id_mapping;

    DROP TABLE gn_modulator.t_mapping_field;
    DROP TABLE gn_modulator.t_mapping_value;
    DROP TABLE gn_modulator.t_mappings;
    """
    )
