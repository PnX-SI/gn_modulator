"""add admin object to modulator

Revision ID: abd7565a6618
Revises: b78eaab0a6e3
Create Date: 2023-10-03 16:34:43.468425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "abd7565a6618"
down_revision = "b78eaab0a6e3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    INSERT INTO gn_permissions.t_objects(code_object, description_object)
        VALUES ('ADMIN', 'Fonctions d''administration d''un module')
        ON CONFLICT DO NOTHING
    """
    )

    # ajout d'un object ADMIN et d'un droit sur le module MODULATOR
    op.execute(
        """
    INSERT INTO
            gn_permissions.t_permissions_available (
                id_module,
                id_object,
                id_action,
                label,
                scope_filter
            )
        SELECT
            m.id_module,
            o.id_object,
            a.id_action,
            v.label,
            v.scope_filter
        FROM
            (
                VALUES
                    ('MODULATOR', 'ADMIN', 'R', False, 'Accéder aux fonctionalités d''administration')
            ) AS v (module_code, object_code, action_code, scope_filter, label)
        JOIN
            gn_commons.t_modules m ON m.module_code = v.module_code
        JOIN
            gn_permissions.t_objects o ON o.code_object = v.object_code
        JOIN
            gn_permissions.bib_actions a ON a.code_action = v.action_code
        ;
        """
    )


def downgrade():
    # suppression d'un object ADMIN et d'un droit sur le module MODULATOR
    op.execute(
        """
            DELETE FROM gn_permissions.t_permissions_available
            USING
                gn_commons.t_modules m,
                gn_permissions.t_objects o
            WHERE
                m.module_code = 'MODULATOR'
                AND o.code_object = 'ADMIN'
        """
    )
