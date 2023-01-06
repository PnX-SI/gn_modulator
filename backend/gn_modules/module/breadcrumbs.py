from gn_modules.schema import SchemaMethods


class ModuleBreadCrumbs:
    @classmethod
    def breadcrumbs(cls, module_code, page_code, data):
        """
        Renvoie le breadcrumb pour un module et une page
        """
        # recupération de la config de la page
        module_config = cls.module_config(module_code)
        page_config = module_config["pages"][page_code]

        # page parent
        parent_page_code = page_config.get("parent")
        object_code = page_config["object_code"]

        # schema name
        schema_code = module_config["objects"][object_code]["schema_code"]
        sm = SchemaMethods(schema_code)

        # url
        url_page = page_config["url"]
        for key, value in data.items():
            url_page = url_page.replace(f":{key}", str(value))

        # full url
        url_page = f"#/modules/{module_code}/{url_page}"

        parent_breadcrumbs = []

        # dans le cas ou l'on a une page parent, on refait un appel à breadcrumbs
        if parent_page_code:

            # label ???
            if data.get(sm.pk_field_name()):
                m = sm.get_row(data[sm.pk_field_name()], module_code=module_code, params={}).one()
                data_label = sm.serialize(m, fields=[sm.label_field_name()])
                label_page = f"{sm.label()} {data_label[sm.label_field_name()]}"
            else:
                # todo create ou list ???

                label_page = (
                    f"Création {sm.label()}" if page_config["type"] == "create" else sm.labels()
                )

            label_page = label_page.capitalize()

            parent_page_config = module_config["pages"][parent_page_code]
            parent_page_url = parent_page_config["url"]
            # determination des données pour l'appel à breadcrumb
            # ici on assume un seul parametre de route commencant par ':'
            # TODO trouver la regex qui va bien
            # TODO pour les page de creation pas de pk mais on peut récupérer le pk du parent directement
            data_parent = {}

            if ":" in parent_page_url and data.get(sm.pk_field_name()):
                data_parent_key = parent_page_url.split(":")[1]
                m = sm.get_row(data[sm.pk_field_name()], params={}).one()

                data_parent = sm.serialize(m, fields=[data_parent_key])
            else:
                data_parent = data

            breadcrumb = [{"label": label_page, "url": url_page}]
            parent_breadcrumbs = cls.breadcrumbs(module_code, parent_page_code, data_parent)

        else:
            # racine du module on met le nom du module
            breadcrumb = [{"url": url_page, "label": f"{module_config['module']['module_label']}"}]
            parent_breadcrumbs = [{"url": "#/modules/", "label": "Modules"}]

        return parent_breadcrumbs + breadcrumb
