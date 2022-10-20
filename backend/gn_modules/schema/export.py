from flask import request, jsonify, Response

import csv


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

    def process_export_csv(self, query_list, params):
        """
        génère la reponse csv à partir de la requête demandée

        TODO traiter par lot et streamer les données?
        """

        res_list = self.serialize_list(query_list.all(), fields=params.get("fields"))

        if not res_list:
            return jsonify([]), 404

        data_csv = []
        keys = res_list[0].keys()
        data_csv.append(self.process_csv_keys(keys))
        data_csv += [[self.process_csv_data(key, d) for key in keys] for d in res_list]

        response = Response(iter_csv(data_csv), mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=data.csv"
        return response

    def process_export(self, export_params):
        """
        process export
            pour l'instant csv
            TODO reprendre comme get_list dans api.py
        """

        params = self.parse_request_args(request, export_params)

        cruved_type = params.get("cruved_type") or "R"
        module_code = export_params["module_code"]
        query_infos = self.get_query_infos(
            module_code=module_code, cruved_type=cruved_type, params=params
        )

        query_list = self.query_list(
            module_code=module_code, cruved_type=cruved_type, params=params
        )

        res_list = query_list.all()
        out = {
            **query_infos,
            "data": self.serialize_list(
                res_list,
                fields=params.get("fields"),
                as_geojson=params.get("as_geojson"),
            ),
        }

        return out

        params = self.parse_request_args(request)

        fields = export["fields"]
        query, query_info = self.get_list(params)
        res_list = query.all()

        out = {
            **query_info,
            "data": self.serialize_list(
                res_list, fields=fields, as_geojson=params.get("as_geojson")
            ),
        }

        if not out["data"]:
            return "", 404
        data_csv = []
        keys = list(fields or out["data"][0].keys())
        keys = list(fields)
        data_csv.append(self.process_csv_keys(keys))
        data_csv += [
            [self.process_csv_data(key, d) for key in keys] for d in out["data"]
        ]

        if params.get("as_csv") == "test":
            return jsonify(data_csv)

        response = Response(iter_csv(data_csv), mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=data.csv"
        return response
