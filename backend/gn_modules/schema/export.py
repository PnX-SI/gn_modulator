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

class SchemaExport():
    '''
        export
    '''

    def process_export(self, export):
        '''
            process export
                pour l'instant csv
                TODO
        '''

        params = self.parse_request_args(request)

        fields = export['fields']
        query, query_info = self.get_list(params)
        res_list = query.all()

        out = {
            **query_info,
            'data': self.serialize_list(
                res_list,
                fields=fields,
                as_geojson=params.get('as_geojson'),
            )
        }

        if not out['data']:
            return '', 404
        data_csv = []
        keys = list(fields or out['data'][0].keys())
        keys = list(fields)
        data_csv.append(self.process_csv_keys(keys))
        data_csv += [
            [
                self.process_csv_data(key, d)
                for key in keys
            ] for d in out['data']
        ]

        if params.get('as_csv') == 'test':
            return jsonify(data_csv)

        response = Response(iter_csv(data_csv), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        return response
