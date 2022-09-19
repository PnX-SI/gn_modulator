"""module_group

Revision ID: 1ae21aca17e1
Revises: d3f266c7b1b6
Create Date: 2022-07-08 14:49:32.547083

"""
from alembic import op
from sqlalchemy.sql import text
import pkg_resources


# revision identifiers, used by Alembic.
revision = '1ae21aca17e1'
down_revision = 'd3f266c7b1b6'
branch_labels = None
depends_on = None


def upgrade():
    sql_files = ['module_group.sql']
    for sql_file in sql_files:
        operations = pkg_resources.resource_string("gn_modules.migrations", f"data/{sql_file}").decode('utf-8')
        op.get_bind().execute(text(operations))


def downgrade():
    op.execute(f'DROP TABLE IF EXISTS gn_modules.t_module_groups CASCADE')

