"""init sous-module m_sipaf

Revision ID: ecde20d34f25
Create Date: 2023-02-01 12:48:24.613956
"""

import pkg_resources
from alembic import op
from sqlalchemy.sql import text
from gn_modules.module import ModuleMethods

# revision identifiers, used by Alembic.
revision = "ecde20d34f25"
down_revision = None
branch_labels = "m_sipaf"
depends_on = "modules"


def upgrade():

    # Creation du schema assiocié au module m_sipaf
    sql_files = ["m_sipaf/schema.sql"]
    for sql_file in sql_files:
        operations = pkg_resources.resource_string(
            "gn_modules.migrations", f"data/{sql_file}"
        ).decode("utf-8")
        op.get_bind().execute(text(operations))


def downgrade():

    # Suppression du schema associé au module m_sipaf
    sql_files = ["m_sipaf/reset.sql"]
    for sql_file in sql_files:
        operations = pkg_resources.resource_string(
            "gn_modules.migrations", f"data/{sql_file}"
        ).decode("utf-8")
        op.get_bind().execute(text(operations))
