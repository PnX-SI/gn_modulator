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

    def process_export_csv(self, module_code, query_list, params):
        """
        génère la reponse csv à partir de la requête demandée

        TODO traiter par lot et streamer les données?
        """

        res = query_list.all()

        res_list = self.serialize_list(res, fields=params.get("fields"))

        if not res_list:
            return jsonify([]), 404

        data_csv = []
        keys = params.get("fields")
        data_csv.append(self.process_csv_keys(keys))
        data_csv += [[self.process_csv_data(key, d) for key in keys] for d in res_list]

        filename = f"export_{module_code}_{datetime.datetime.now().strftime('%Y_%m_%d_%Hh%M')}"

        response = Response(iter_csv(data_csv), mimetype="text/csv")
        response.headers.add("Content-Disposition", "attachment", filename=filename)

        return response
