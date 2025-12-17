"""Renomme largeur_ouvrage et longueur_franchissement en longueur_traversee et largeur_ouvrage

Revision ID: af1c24a8044a
Revises: c11d028e1b42
Create Date: 2024-07-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "af1c24a8044a"
down_revision = "c11d028e1b42"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pr_sipaf'
                  AND table_name = 't_passages_faune'
                  AND column_name = 'pr'
                  AND data_type <> 'double precision'
            ) THEN
                ALTER TABLE pr_sipaf.t_passages_faune
                ALTER COLUMN pr TYPE double precision USING pr::double precision;
            END IF;
        END$$;
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pr_sipaf'
                  AND table_name = 't_passages_faune'
                  AND column_name = 'longueur_franchissement'
            ) THEN
                ALTER TABLE pr_sipaf.t_passages_faune
                RENAME COLUMN longueur_franchissement TO longueur_traversee;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pr_sipaf'
                  AND table_name = 't_passages_faune'
                  AND column_name = 'longueur_traversee'
            ) THEN
                COMMENT ON COLUMN pr_sipaf.t_passages_faune.longueur_traversee IS
                    'Longueur de traversée de l''ouvrage par l''animal en mètre';
            END IF;
        END$$;
        """
    )


def downgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pr_sipaf'
                  AND table_name = 't_passages_faune'
                  AND column_name = 'longueur_traversee'
            ) THEN
                ALTER TABLE pr_sipaf.t_passages_faune
                RENAME COLUMN longueur_traversee TO longueur_franchissement;

                COMMENT ON COLUMN pr_sipaf.t_passages_faune.longueur_franchissement IS
                    'Longueur de franchissement de l''ouvrage en mètres (ne prend pas en compte l''épaisseur des matériaux et éventuels obstacles)';
            END IF;
        END$$;
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pr_sipaf'
                  AND table_name = 't_passages_faune'
                  AND column_name = 'pr'
                  AND data_type <> 'integer'
            ) THEN
                ALTER TABLE pr_sipaf.t_passages_faune
                ALTER COLUMN pr TYPE integer USING round(pr)::integer;
            END IF;
        END$$;
        """
    )
