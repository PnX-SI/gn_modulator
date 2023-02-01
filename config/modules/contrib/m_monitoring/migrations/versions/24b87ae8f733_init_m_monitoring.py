"""init sous-module m_monitoring

Revision ID: 24b87ae8f733
Create Date: 2022-05-20 16:55:43.120470
"""

import pkg_resources
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "24b87ae8f733"
down_revision = None
branch_labels = "m_monitoring"
depends_on = "modules"


def upgrade():
    # Creation du schema assiocié au module m_monitoring
    sql_files = ["m_monitoring/schema.sql"]
    for sql_file in sql_files:
        operations = pkg_resources.resource_string(
            "gn_modules.migrations", f"data/{sql_file}"
        ).decode("utf-8")
        op.get_bind().execute(text(operations))


def downgrade():
    # Suppression du schema associé au module m_monitoring
    sql_files = ["m_monitoring/reset.sql"]
    for sql_file in sql_files:
        operations = pkg_resources.resource_string(
            "gn_modules.migrations", f"data/{sql_file}"
        ).decode("utf-8")
        op.get_bind().execute(text(operations))
