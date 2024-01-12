"""init sous-module {{cookiecutter.module_name}}

Revision ID: dfsdgf45sdf1
Create Date: 2023-02-01 12:48:24.613956
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "dfsdgf45sdf1"# TODO : Change it !!!
down_revision = None
branch_labels = "{{cookiecutter.module_name}}"
depends_on = "modulator"


def upgrade():
    op.execute("create schema {{cookiecutter.db_schema_name}}")
    op.create_table(
        "author",
        sa.Column("id_author", sa.Integer, primary_key=True),
        sa.Column("first_name", sa.String),
        sa.Column("last_name", sa.String),
        sa.Column("email_address", sa.String),
        schema="{{cookiecutter.db_schema_name}}",
    )
    op.create_table(
        "post",
        sa.Column("id_post", sa.Integer, primary_key=True),
        sa.Column("post_title", sa.String),
        sa.Column("post_content", sa.String),
        sa.Column("id_author", sa.Integer, sa.ForeignKey("{{cookiecutter.db_schema_name}}.author.id_author")),
        schema="{{cookiecutter.db_schema_name}}",
    )


def downgrade():
    op.drop_table("post", schema="{{cookiecutter.db_schema_name}}")
    op.drop_table("author", schema="{{cookiecutter.db_schema_name}}")
    op.execute("drop schema {{cookiecutter.db_schema_name}}")
