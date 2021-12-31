'''
    methodes pour les layout ajsf du frontend
'''


class SchemaConfigLayout():

    def form_layout(self):
        '''
            layout destiné au composant formulaire du frontend
        '''

        # - soit $meta.form.layout est defini,
        # - ou alors toutes les cle de properties
        form_layout = self.meta('form', {}).get('layout', list(self.properties().keys()))
        return form_layout

        # return self.process_form_layout(form_layout)
