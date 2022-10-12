from gn_modules.schema import SchemaMethods

class ModulesBreadCrumbs():

    @classmethod
    def breadcrumbs(cls, module_code, page_name, data):
        '''
            Renvoie le breadcrumb pour un module et une page
        '''

        # recupération de la config de la page
        module_config = cls.module_config(module_code)
        page_config = module_config['pages'][page_name]

        # page parent
        parent_page_name =page_config.get('parent')
        page_key = page_config['key']

        # schema name
        schema_name = module_config['data'][page_key]['schema_name']
        sm = SchemaMethods(schema_name)

        # url
        url_page = page_config['url']
        for key, value in data.items():
            url_page = url_page.replace(f':{key}', str(value))

        # full url
        url_page = f'#/modules/{module_code}/{url_page}'

        parent_breadcrumbs = []

        # dans le cas ou l'on a une page parent, on refait un appel à breadcrumbs
        if parent_page_name:

            # label ???
            if data.get(sm.pk_field_name()):
                m = sm.get_row(
                    data[sm.pk_field_name()],
                    module_code=module_code,
                    params={}
                ).one()
                data_label = sm.serialize(m, fields = [sm.label_field_name()])
                label_page = f'{sm.label()} {data_label[sm.label_field_name()]}'
            else:
                # todo create ou list ???

                label_page = (
                    f'Création {sm.label()}' if page_config['type'] == 'create'
                    else sm.labels()
                )

            label_page = label_page.capitalize()

            parent_page_config = module_config['pages'][parent_page_name]
            parent_page_url = parent_page_config['url']
            # determination des données pour l'appel à breadcrumb
            # ici on assume un seul parametre de route commencant par ':'
            # TODO trouver la regex qui va bien
            # TODO pour les page de creation pas de pk mais on peut récupérer le pk du parent directement
            data_parent = {}


            if ':' in parent_page_url and data.get(sm.pk_field_name()):
                data_parent_key = parent_page_url.split(':')[1]
                m = sm.get_row(data[sm.pk_field_name()])

                data_parent = sm.serialize(
                    m,
                    fields = [data_parent_key]
                )
            else:
                data_parent = data


            breadcrumb = [ {'label': label_page, 'url': url_page} ]
            parent_breadcrumbs = cls.breadcrumbs(module_code, parent_page_name, data_parent)

        else:
            # racine du module on met le nom du module
            breadcrumb = [{ "url": url_page, "label": f"{module_config['module']['module_label']}"}]
            parent_breadcrumbs = [ {"url": "#/modules/", "label": "Modules"} ]

        return parent_breadcrumbs + breadcrumb