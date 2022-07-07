'''
    methodes pour les layout ajsf du frontend
'''


# from ast import keyword
# from concurrent.futures import process

# from pkg_resources import LegacyVersion


class SchemaConfigLayout():

    def form_layout(self):
        '''
            layout destiné au composant formulaire du frontend
        '''

        # - soit $meta.form.layout est defini,
        # - ou alors toutes les cle de properties

        form_layout = self.attr('form.layout', list(self.properties().keys()))
        return self.process_layout(form_layout)

    def process_layout(self, layout):
        '''
            récupérer les infos d'une clé depuis les définitions
        '''

        if isinstance(layout, dict):
            if "key" in layout:
                if "." in layout['key']:
                    definition = self.property(layout['key'].split('.')[0])
                    layout['title'] = layout.get('title', definition['title'])


                if not self.has_property(layout['key']):
                    return layout
                definition = self.property(layout['key'])
                layout['required'] = (
                    layout['required'] if layout.get('required') is not None
                    else self.is_required(layout['key'])
                )
                for key in [
                    'title',
                    'description',
                    'type',
                    'schema_name',
                    'nomenclature_type',
                    'min',
                    'max',
                    'change',
                    'placeholder',
                    'disabled'
                ]:
                    if key in definition:
                        layout[key] = layout.get(key, definition[key])

                if layout['type'] in ['array', 'object'] and layout.get('schema_name'):
                    rel = self.cls(layout['schema_name'])
                    layout['items'] = rel.process_layout(layout['items'])
                return layout

            return {
                k: self.process_layout(v)
                for k, v in layout.items()
            }

        if isinstance(layout, list):
            return [self.process_layout(elem) for elem in layout]

        if isinstance(layout, str) and (not layout.startswith('__f__')) and self.has_property(layout):
            return self.process_layout({'key': layout})

        return layout


