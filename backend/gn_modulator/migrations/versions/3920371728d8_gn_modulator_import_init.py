"""gn_modulator import init

Revision ID: 3920371728d8
Revises: d3f266c7b1b6
Create Date: 2023-03-03 14:31:35.339631

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3920371728d8"
down_revision = "d3f266c7b1b6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """

CREATE TABLE gn_modulator.t_imports(
    id_import SERIAL NOT NULL,
    id_digitiser INTEGER, -- qui a fait l'import
    module_code VARCHAR, --
    object_code VARCHAR, --
    schema_code VARCHAR, --
    data_file_path VARCHAR, -- stocker dans un blob ??
    mapping_file_path VARCHAR, -- varchar ou table mapping
    mapping VARCHAR, -- varchar ou table mapping
    csv_delimiter VARCHAR, --
    data_type VARCHAR,
    status VARCHAR,
    res JSONB,
    tables JSONB,
    errors JSONB,
    sql JSONB,
    options JSONB,
    meta_create_date timestamp without time zone DEFAULT now(),
    meta_update_date timestamp without time zone DEFAULT now()
);

ALTER TABLE gn_modulator.t_imports
    ADD CONSTRAINT pk_gn_modulator_t_imports_id_import PRIMARY KEY (id_import);

ALTER TABLE gn_modulator.t_imports
    ADD CONSTRAINT fk_modulator_t_impt_t_role_id_digitiser FOREIGN KEY (id_digitiser)
    REFERENCES utilisateurs.t_roles(id_role)
    ON UPDATE CASCADE ON DELETE SET NULL;

CREATE TRIGGER tri_meta_dates_change_gnm_t_import
    BEFORE INSERT OR UPDATE
    ON gn_modulator.t_imports
    FOR EACH ROW
    EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


DROP FUNCTION IF EXISTS gn_modulator.check_value_for_type(VARCHAR, varchar);
DROP FUNCTION IF EXISTS gn_modulator.check_value_for_type(VARCHAR, anyelement);
CREATE OR REPLACE FUNCTION gn_modulator.check_value_for_type(type_in VARCHAR, value_in varchar)
    RETURNS BOOLEAN AS
    $$
    BEGIN
        IF type_in = 'VARCHAR' THEN PERFORM value_in::VARCHAR; RETURN TRUE; END IF;
        IF type_in = 'INTEGER' THEN PERFORM value_in::INTEGER; RETURN TRUE; END IF;
        IF type_in = 'BOOLEAN' THEN PERFORM value_in::BOOLEAN; RETURN TRUE; END IF;
        IF type_in = 'FLOAT' THEN PERFORM value_in::FLOAT; RETURN TRUE; END IF;
        IF type_in = 'DATE' THEN PERFORM value_in::DATE; RETURN TRUE; END IF;
        IF type_in = 'TIMESTAMP' THEN PERFORM value_in::TIMESTAMP; RETURN TRUE; END IF;
        IF type_in = 'UUID' THEN PERFORM value_in::UUID; RETURN TRUE; END IF;
        IF type_in = 'GEOMETRY' THEN PERFORM value_in::GEOMETRY; RETURN TRUE; END IF;
        IF type_in = 'JSONB' THEN PERFORM value_in::JSONB; RETURN TRUE; END IF;
        RETURN FALSE;
        EXCEPTION WHEN OTHERS THEN
            RETURN FALSE;
    END;
    $$
    LANGUAGE 'plpgsql' COST 100

    """
    )
    pass


def downgrade():
    op.execute(
        """
    DROP TABLE gn_modulator.t_imports;
    
    DROP FUNCTION IF EXISTS gn_modulator.check_value_for_type(VARCHAR, varchar);
    DROP FUNCTION IF EXISTS gn_modulator.check_value_for_type(VARCHAR, anyelement);

    """
    )
    pass
