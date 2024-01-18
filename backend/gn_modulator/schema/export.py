from flask import request, jsonify, Response, make_response
import sqlparse
import csv
import datetime
from gn_modulator.query.utils import pretty_sql
from geonature.utils.env import db


class Line(object):
    def __init__(self):
        self._line = None

    def write(self, line):
        self._line = line

    def read(self):
        return self._line


def iter_csv(data):
    line = Line()
    writer = csv.writer(line)
    for csv_line in data:
        writer.writerow(csv_line)
        yield line.read()


class SchemaExport:
    """
    export
    """

    def process_export_fields(self, fields_in, process_field_name=False):
        """
        Renvoie
            - la liste des clé
            - la liste des headers
        """
        headers = []
        fields_out = []

        # si au moins une des clés possède une ',' on ne fait pas process_csv_keys

        process_fields = process_field_name and all(["," not in f for f in fields_in])

        if process_fields:
            return self.process_csv_keys(fields_in), fields_in

        # pour tous les champs
        for f in fields_in:
            if "," in f:
                field = f.split(",")[0]
                header = f.split(",")[1]
            else:
                field = header = f
            fields_out.append(field)
            headers.append(header)

        return headers, fields_out

    def parse_export_column(self, col, fields, headers, main_table):
        test = col
        res = {}

        if " AS " in col:
            test = col.split(" AS ")[-1]
            base_expression = " AS ".join(col.split(" AS ")[:-1])
            if test in fields:
                res["index"] = fields.index(test)
                res["base_expression"] = base_expression
                return res

            for index, field in enumerate(fields):
                if "." in field and test in field and ".".join(field.split(".")[1:]) in col:
                    res["index"] = index
                    res["base_expression"] = base_expression
                    return res

        if col in fields:
            res["index"] = fields.index(test)
            res["base_expression"] = col
            return res

        if col.startswith(main_table):
            test = col.replace(f"{main_table}.", "")
            if test in fields:
                res["index"] = fields.index(test)
                res["base_expression"] = col
                return res

        if col.startswith('"'):
            test = col.replace(f'"', "")
            if test in fields:
                res["index"] = fields.index(test)
                res["base_expression"] = col
                return res

    def process_exports_columns(self, columns, fields, headers, main_table):
        keep_columns = []
        for col in columns:
            res = self.parse_export_column(col, fields, headers, main_table)
            if res is None:
                continue

            res["field"] = fields[res["index"]]
            res["field_quote"] = f'''"{res["field"]}"''' if "." in res["field"] else res["field"]
            if "." in res["field"]:
                sub_fields = res["field"].split(".")
                for i in range(len(sub_fields)):
                    relation_key = ".".join(sub_fields[: -i + 1])
                    res["is_array"] = (
                        res.get("is_array")
                        or self.Model().is_relation_1_n(relation_key)
                        or self.Model().is_relation_n_n(relation_key)
                    )

            res["header"] = headers[res["index"]]
            # TODO array_agg
            res["base_alias"] = (
                f""" AS {res['field_quote']}"""
                if (res["field"] != res["base_expression"] or "." in res["field"])
                else ""
            )
            res["alias"] = f''' AS "{res['header']}"''' if res["header"] != res["field"] else ""
            res["expression"] = (
                f"""STRING_AGG(DISTINCT {res['field_quote']}, ', ')"""
                if res.get("is_array")
                else res["field_quote"]
            )

            keep_columns.append(res)

        return keep_columns

    def parse_sql(self, q):
        """Pour générer une vue destinée au module Export"""
        txt = pretty_sql(q)

        txt = txt.replace("\n", " ")
        txt = txt.replace("  ", " ")

        columns = []
        cur = ""
        nb_par_open = 0
        for c in txt:
            if c == "(":
                nb_par_open += 1
            if c == ")":
                nb_par_open -= 1
            if c == "," and nb_par_open == 0:
                cur = cur.strip()
                if cur.startswith("SELECT "):
                    cur = cur.replace("SELECT ", "")

                if "(":
                    columns.append(cur)
                cur = ""

                continue

            cur += c

        remaining = "FROM".join(cur.split("FROM")[1:]).strip()
        cur = cur.split("FROM")[0].strip()
        main_table = remaining.split(" ")[0]
        columns.append(cur.strip())

        return columns, main_table, remaining

    def process_export_sql(self, q, params):
        columns, main_table, remaining = self.parse_sql(q)

        headers, fields = self.process_export_fields(
            params.get("fields"), params.get("process_field_name")
        )

        keep_columns = sorted(
            self.process_exports_columns(columns, fields, headers, main_table),
            key=lambda x: x["field"],
        )

        base_columns_txt = "\n, ".join(
            map(lambda x: f"{x['base_expression']}{x['base_alias']}", keep_columns)
        )
        columns_txt = "\n, ".join(map(lambda x: f"{x['expression']}{x['alias']}", keep_columns))
        group_by_txt = ", ".join(
            map(
                lambda x: f"{x['field_quote']}",
                filter(lambda x: not x.get("is_array"), keep_columns),
            )
        )
        if group_by_txt:
            group_by_txt = f"GROUP BY {group_by_txt}"
        sql_txt = f"""
        WITH pre AS (
        SELECT {base_columns_txt}
        FROM {remaining}
        )
        SELECT {columns_txt}
        FROM pre
        {group_by_txt}
        """

        pretty_txt = sqlparse.format(sql_txt, reindent=True, keywordcase="upper")
        return pretty_txt

        # parser et récupérer les colonnes

    def process_export_csv_sql(self, query_list, params):
        response = make_response(
            self.process_export_sql(query_list, params),
            200,
        )
        response.mimetype = "text/plain"
        return response

    def process_export_csv(self, module_code, query_list, params):
        """
        génère la reponse csv à partir de la requête demandée

        TODO traiter par lot et streamer les données?
        """

        q = query_list

        # champs
        headers, fields = self.process_export_fields(
            params.get("fields"), params.get("process_field_name")
        )

        res_list = self.serialize_list(db.session.execute(q).unique().all(), fields=fields)

        if not res_list:
            return jsonify([]), 404

        data_csv = []
        data_csv.append(headers)
        data_csv += [
            [
                self.process_csv_data(key, d, process_label=params["process_label"])
                for key in fields
            ]
            for d in res_list
        ]

        filename = f"export_{module_code}_{datetime.datetime.now().strftime('%Y_%m_%d_%Hh%M')}.csv"

        response = Response(iter_csv(data_csv), mimetype="text/csv")
        response.headers.add("Content-Disposition", "attachment", filename=filename)

        return response
