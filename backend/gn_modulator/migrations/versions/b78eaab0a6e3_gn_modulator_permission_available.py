"""gn_modulator permissions available

Revision ID: b78eaab0a6e3
Revises: 3920371728d8
Create Date: 2023-06-20 15:19:21.097194

"""

from alembic import op
import sqlalchemy as sa
from gn_modulator import MODULE_CODE

# revision identifiers, used by Alembic.
revision = "b78eaab0a6e3"
down_revision = "3920371728d8"
depends_on = None


def upgrade():
    pass

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
                    ('MODULATOR', 'ALL', 'R', False, 'Accéder aux modules')
            ) AS v (module_code, object_code, action_code, scope_filter, label)
        JOIN
            gn_commons.t_modules m ON m.module_code = v.module_code
        JOIN
            gn_permissions.t_objects o ON o.code_object = v.object_code
        JOIN
            gn_permissions.bib_actions a ON a.code_action = v.action_code
    """
    )

    op.execute(
        f"""
        WITH bad_permissions AS (
            SELECT
                p.id_permission
            FROM
                gn_permissions.t_permissions p
            JOIN gn_commons.t_modules m
                    USING (id_module)
            WHERE
                m.module_code IN ('{MODULE_CODE}')
            EXCEPT
            SELECT
                p.id_permission
            FROM
                gn_permissions.t_permissions p
            JOIN gn_permissions.t_permissions_available pa ON
                (p.id_module = pa.id_module
                    AND p.id_object = pa.id_object
                    AND p.id_action = pa.id_action)
        )
        DELETE
        FROM
            gn_permissions.t_permissions p
                USING bad_permissions bp
        WHERE
            bp.id_permission = p.id_permission;
    """
    )


def downgrade():
    # suppression des droits disponibles pour le module MODULATOR

    op.execute(
        """
        DELETE FROM
            gn_permissions.t_permissions_available pa
        USING
            gn_commons.t_modules m
        WHERE
            pa.id_module = m.id_module
            AND
            module_code = 'MODULATOR'
        """
    )
