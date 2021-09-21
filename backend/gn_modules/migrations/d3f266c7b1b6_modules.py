""" gn_modules
Revision ID: d3f266c7b1b6
Revises: 
Create Date: 2021-09-15 11:49:24.512562

"""
from alembic import op
from sqlalchemy.sql import text
import pkg_resources

from geonature.utils.config import config


# revision identifiers, used by Alembic.
revision = 'd3f266c7b1b6'
down_revision = None
branch_labels = ('modules',)
depends_on = None

def upgrade():
    sql_files = ['schema.sql']
    for sql_file in sql_files:
        operations = pkg_resources.resource_string("gn_modules.migrations", f"data/{sql_file}").decode('utf-8')
        op.get_bind().execute(text(operations))
        # op.get_bind().execute(text(operations), MYLOCALSRID=config['LOCAL_SRID'])

def downgrade():
    op.execute(f'DROP SCHEMA gn_modules CASCADE')
