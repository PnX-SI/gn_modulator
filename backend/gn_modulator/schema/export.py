from flask import request, jsonify, Response
import sqlparse
import csv
import datetime


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

    def process_export_csv(self, module_code, query_list, params):
        """
        génère la reponse csv à partir de la requête demandée

        TODO traiter par lot et streamer les données?
        """

        res = query_list.all()

        # champs
        headers, fields = self.process_export_fields(
            params.get("fields"), params.get("process_field_name")
        )

        res_list = self.serialize_list(res, fields=fields)

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
