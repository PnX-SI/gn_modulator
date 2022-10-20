"""
    repositories - filters
"""
import unidecode
from sqlalchemy import cast, and_, or_, not_
from geonature.utils.env import db
from ..errors import SchemaRepositoryFilterError, SchemaRepositoryFilterTypeError
from sqlalchemy.sql.functions import ReturnTypeFromArgs


class unaccent(ReturnTypeFromArgs):
    pass


class SchemaRepositoriesFilters:
    """
    repositories - filters

    """

    __abstract__ = True

    def process_filters(self, Model, filters, query):
        """
        process filter

        TODO dict entry
        {
            a: f1,
            b: f2,
            c: f3,
            d: f4,
            e: f5,
            cond: '!a*(b+c*!(de))'
        }
        """

        filters_processed, query = self.process_filter_array(Model, filters, query)
        if filters_processed is not None:
            query = query.filter(filters_processed)
            return query

        return query

    def process_filter_array(self, Model, filter_array, query=None, condition=None):
        """
        process filter list

        traite un liste qui peux contenir
            - des listes (traitement récursif)
            - des filtres : { field : <f_field>, type: <filter_type>, value: <filter_value>}
            - des operateurs :
                - '!' : négation, unitaire
                - '*' : et
                - '| : ou

        l'opérateur par défaut est '*':

        exemples (f1 et f2 sont des filtres):

            - [ f1, '*', f2]                  =>  f1 ET f2
            - [ f1, '|', f2]                  =>  f1 OU f2
            - [ f1, f2]                       =>  f1 ET f2
            - [ '!', f1, '|', '!', f2]        =>  (NON f1) OU (NON f2)
            - [ '!', [ f1, '|', '!', f2 ] ]   =>  NON (f1 OU (NON f2))
        """
        cur_filter = None
        cur_ops = []

        for elem in filter_array:

            loop_filter = None

            # récursivité sur les listes
            if isinstance(elem, list):
                loop_filter, query = self.process_filter_array(
                    Model, elem, query, condition
                )

            # filtre
            elif isinstance(elem, dict):
                loop_filter, query = self.get_filter(Model, elem, query, condition)

            # operation
            elif elem in "!|*":
                # deux négations '!' s'annulent
                if elem == "!" and len(cur_ops) > 0 and cur_ops[-1] == "!":
                    cur_ops = cur_ops[:-1]
                else:
                    cur_ops.append(elem)

            else:
                raise SchemaRepositoryFilterError(
                    "L'élément de liste de filtre {} est mal défini.".format(elem)
                )

            if loop_filter is not None:

                # on prend le dernier opérateur de la liste ou bien '*' par défaut
                op = cur_ops.pop() if len(cur_ops) > 0 else "*"

                # traitement de la négation '!'
                if op == "!":
                    loop_filter = not_(loop_filter)
                    # on prend le dernier opérateur de la liste ou bien '*' par défaut
                    op = cur_ops.pop() if len(cur_ops) > 0 else "*"

                # s'il y un filtre courant, on applique l'opération en cours
                if cur_filter is not None:
                    if op == "*":
                        cur_filter = and_(cur_filter, loop_filter)
                    if op == "|":
                        cur_filter = or_(cur_filter, loop_filter)

                # s'il n'y a pas de filtre courant, on initialise la variable cur_filter
                else:
                    cur_filter = loop_filter
        return cur_filter, query

    def find_index_close(self, index_open, filters):
        """
        pour trouver l'index de la parenthèse fermante ] correspondante
        """
        cpt_open = 0
        for index in range(index_open + 1, len(filters)):
            if filters[index] == "[":
                cpt_open += 1
            if filters[index] == "]":
                if cpt_open == 0:
                    return index
                else:
                    cpt_open -= 1
        filters[index_open] = f"   {filters[index_open]}   "
        raise Exception(
            f"Pas de parenthèse fermante trouvée {','.join(filters[index_open:])}"
        )

    def parse_filters(self, filters):
        """
        traite une liste de chaine de caractères représentant des filtres
        """

        if not filters:
            return []

        if isinstance(filters, str):
            return self.parse_filters(filters.split(","))

        filters_out = []

        nb_filters = len(filters)
        index = 0
        while index < nb_filters:

            # calcul du filtre {field, type, value}
            filter = self.parse_filter(filters[index])

            # si on tombe sur une parenthèse ouvrante
            if filter == "[":

                # on cherche l'index de la parenthèse fermante ] correspondante
                index_close = self.find_index_close(index, filters)

                # on calcule les filtres entre les deux [...]
                filters_out.append(self.parse_filters(filters[index + 1 : index_close]))

                # on passe à l'index qui suit index_close
                index = index_close + 1
                # de l'indice du ']' correspondant

            # si on tombe sur une parenthère fermante => pb
            elif filter == "]":
                filters[index] = f"   {filters[index]}   "
                raise SchemaRepositoryFilterError(
                    f"Parenthese fermante non appariée trouvée dans  {','.join(filters)}"
                )

            # sinon on ajoute le filtre à la liste et on passe à l'index suivant
            else:
                filters_out.append(filter)
                index += 1

        return filters_out

    def parse_filter(self, str_filter):
        """
        renvoie un filtre a partir d'une chaine de caractère
        id_truc=5 => { field: id_truc type: = value: 5 } etc...
        """

        if str_filter in "*|![]":
            return str_filter

        index_min = None
        filter_type_min = None
        for filter_type in ["=", "<", ">", ">=", "<=", "like", "ilike", "in", "~"]:
            try:
                index = str_filter.index(f" {filter_type} ")
            except ValueError:
                continue

            if (
                (index_min is None)
                or (index < index_min)
                or (index_min == index and len(filter_type) > len(filter_type_min))
            ):
                index_min = index
                filter_type_min = filter_type

        if not filter_type_min:
            return None

        filter = {
            "field": str_filter[:index_min],
            "type": filter_type_min,
            "value": str_filter[index_min + len(filter_type_min) + 2 :],
        }

        if filter_type_min == "in":
            filter["value"] = filter["value"].split(";")

        return filter

    def get_filter(self, Model, filter, query=None, condition=None):
        """
        get filter

        à voir ce qu'il y a pour les relations de type array(Object)
          - oneOf
          - allOf ??????
        """

        filter_out = None

        filter_field = filter["field"]
        filter_type = filter["type"]
        filter_value = filter.get("value", None)

        model_attribute, query = self.custom_getattr(
            Model, filter_field, query, condition
        )

        if filter_type in ["like", "ilike"]:
            filter_out = getattr(
                unaccent(cast(model_attribute, db.String)), filter_type
            )(filter_value)

        elif filter_type == "~":
            filter_value_unaccent = unidecode.unidecode(filter_value)
            filters_out = []
            for v in filter_value_unaccent.split(" "):
                filters_out.append(
                    getattr(unaccent(cast(model_attribute, db.String)), "ilike")(
                        f"%{v}%"
                    )
                )
            filter_out = and_(*filters_out)

        elif filter_type == ">":
            filter_out = model_attribute > filter_value

        elif filter_type == ">=":
            filter_out = model_attribute >= filter_value

        elif filter_type == "<":
            filter_out = model_attribute < filter_value

        elif filter_type == "<=":
            filter_out = model_attribute <= filter_value

        elif filter_type == "=":

            filter_out = (
                model_attribute == filter_value
                # or_(
                # model_attribute == filter_value,
                # cast(model_attribute, db.String) == (str(filter_value)),
            )

        elif filter_type == "!=":
            filter_out = cast(model_attribute, db.String) != (str(filter_value))

        elif filter_type == "in":
            filter_out = cast(model_attribute, db.String).in_(
                [str(x) for x in filter_value]
                # map(
                #     lambda x: str(x),
                #     filter_value
                # )
            )

        else:
            raise SchemaRepositoryFilterTypeError(
                "Le type de filtre {} n'est pas géré".format(filter_type)
            )

        return filter_out, query
