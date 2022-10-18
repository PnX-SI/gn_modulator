from alembic import context, op
from pathlib import Path
from utils_flask_sqla.migrations.utils import logger


def table_exists(table):

    txt_table_exists = (
        op.get_bind()
        .execute(
            f"""SELECT EXISTS (SELECT FROM information_schema.tables
   WHERE  table_schema = '{table.split('.')[0]}'
   AND    table_name   = '{table.split('.')[1]}'
   );"""
        )
        .scalar()
    )
    print(txt_table_exists)
    return txt_table_exists


def import_csv_file(csvfile_path, temporary_table):

    cursor = op.get_bind().connection.cursor()

    data_dir = context.get_x_argument(as_dictionary=True).get("data-directory")
    abs_csvfile_path = Path(data_dir) / csvfile_path
    if not (abs_csvfile_path).exists():
        raise Exception(f"Le fichier {abs_csvfile_path} n existe pas")

    with open(abs_csvfile_path, "r") as f:
        line = f.readline()

        columns = line.replace("\n", "").split("\t")
        columns_fields = ", ".join(columns)
        columns_sql = "\n".join(map(lambda x: f"{x} VARCHAR,", columns))

        txt_create_temp_table = f"""
            CREATE TABLE IF NOT EXISTS {temporary_table} (
                id_import SERIAL NOT NULL,
                {columns_sql}
                CONSTRAINT pk_{'_'.join(temporary_table.split('.'))}_id_import PRIMARY KEY (id_import)
            );
        """

        op.execute(txt_create_temp_table)
        logger.info(f"Put data from {csvfile_path} into {temporary_table}")
        cursor.copy_expert(f"COPY {temporary_table}({columns_fields}) FROM STDIN;", f)
