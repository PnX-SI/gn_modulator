from py_mini_racer import MiniRacer
from gn_modulator.utils.errors import add_error


class DefinitionDynamic:
    """
    pour vérifier les definition dynamique
    """

    @classmethod
    def is_dynamic_element(cls, element):
        """
        test si l'element est dynamique
        """
        return isinstance(element, str) and element.strip().startswith("__f__")

    @classmethod
    def str_function(cls, element):
        """
        renvoie la chaîne de caractère qui sera utilisée dans la création de la fonction
        """

        # on enleve les blancs avant et apres
        str_function = element.strip()

        # on enleve '__f__'
        str_function = str_function[5:]

        # pour les cas comme
        #   data.truc == 'truc'
        # on ajoute des accolade et un return pour avoir
        #   { return data.truc == 'truc' }
        if str_function[0] != "{" and "return" not in str_function:
            str_function = f"{{ return {str_function} }}"

        # on ajoute la resolution des variables
        str_function = f"""{{
            const {{layout, data, globalData, o, utils, context, formGroup}} = x;
            {str_function[1:-1]}
        }}"""

        # on le prépare à être utilisé entre deux ` : f"`{str_function}`"
        str_function = str_function.replace("`", "\`").replace("$", "\$")

        return str_function

    @classmethod
    def str_x_for_test(cls):
        """
        variable x qui sera utilisée pour les test
        au plus proche de ce que l'on attend dans layout.service
        """

        return """{
    data: {},
    layout: {},
    globalData: {},
    formGroup: {},
    utils: {
        today: () => {},
        departementsForRegion: () => {},
        YML: {},

    },
    o: {
        prefilters: () => {},
        filters: () => {},
        config: () => {},
        value: () => {},
        schema_code: () => {},
        label: () => {},
        labels: () => {},
        du_label: () => {},
        des_labels: () => {},
        data_label: () => {},
        tab_label: () => {},
        title_details: () => {},
        title_create_edit: () => {},
        label_edit: () => {},
        label_create: () => {},
        label_delete: () => {},
        is_action_allowed: () => {},
        geometry_type: () => {},
        geometry_field_name: () => {},
        object: () => {},
        url_export: () => {}
    },
    context: {},
}"""

    @classmethod
    def check_definition_dynamic_layout(cls, definition_type, definition_code, element, keys=[]):
        """
        Vérifie récursivement les elements commençant par '__f__'
        - fonction dynamiques js
        - on vérifie seulement la creation de la fonction
          (à ce stade on ne peut pas prédire l'état des variables (data, etc...))
          on ignore les 'SyntaxError: Line 1: TemplateElement is not supported by ECMA 5.1.'
        """

        if isinstance(element, dict):
            for key, item in element.items():
                cls.check_definition_dynamic_layout(
                    definition_type, definition_code, item, keys + [key]
                )
            return

        if isinstance(element, list):
            # cas (à rendre obselete??) ou la fonction est une liste de string et le premier est '__f__' ??
            # if len(element) > 2 and isinstance(element[0], str) and element[0].startswith("__f__") and element[1]:
            #     return cls.check_definition_dynamic_layout(
            #         definition_type, definition_code, "\n".join(element), keys)
            for index, item in enumerate(element):
                cls.check_definition_dynamic_layout(
                    definition_type, definition_code, item, keys + [str(index)]
                )
            return

        if cls.is_dynamic_element(element):
            str_function = cls.str_function(element)

            str_x_for_test = cls.str_x_for_test()

            # chaine à evaluer pour essayer de détecter les erreurs
            str_eval = f"""
// chaine de la fonction
let strFunction, f, x;

// variable pour le test de la fonction
x = {str_x_for_test};

// chaine caractere function
strFunction = `{str_function}`;

// creation de la fonction
f = new Function('x', strFunction);


// test d'utilisation de la fonction
f(x);"""

            try:
                ctx = MiniRacer()
                ctx.eval(str_eval)
            except Exception as e:
                # par exemple ommetre data.site.value (avec data.site undefined)
                if "Uncaught TypeError: Cannot read property" in str(e):
                    pass

                elif "Uncaught TypeError: formGroup" in str(e):
                    pass
                else:
                    str_error = str(e).split("\n")[0]
                    add_error(
                        definition_type=definition_type,
                        definition_code=definition_code,
                        error_code="ERR_LOCAL_CHECK_DYNAMIC",
                        error_msg=f"[{'.'.join(keys)}] : {str_error}\n    {element}",
                    )

            return
