"""
    repositories - filters
"""
import unidecode
from sqlalchemy import cast, and_, or_, not_, func, orm
from geonature.utils.env import db
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from gn_modulator.utils.filters import parse_filters
from .base import BaseSchemaQuery
from .getattr import _getModelAttr, _clear_query_cache


# late import ?
def SchemaMethods():
    from gn_modulator import SchemaMethods

    return SchemaMethods


class SchemaQueryFilterError(Exception):
    pass


class SchemaQueryFilterTypeError(Exception):
    pass


class unaccent(ReturnTypeFromArgs):
    pass


class SchemaQueryFilters(BaseSchemaQuery):
    """
    repositories - filters

    """

    __abstract__ = True

    def process_filters(self, filters):
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

        filters_processed, self = self.process_filter_array(filters)
        if filters_processed is not None:
            self = self.filter(filters_processed)
            return self

        return self

    def process_filter_array(self, filter_array):
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

        if isinstance(filter_array, str):
            filter_array = [filter_array]

        for elem in filter_array:
            loop_filter = None

            # récursivité sur les listes
            if isinstance(elem, list):
                loop_filter, self = self.process_filter_array(elem)

            # filtre
            elif isinstance(elem, dict):
                loop_filter, self = self.get_filter(elem)

            # operation
            elif elem in "!|*":
                # deux négations '!' s'annulent
                if elem == "!" and len(cur_ops) > 0 and cur_ops[-1] == "!":
                    cur_ops = cur_ops[:-1]
                else:
                    cur_ops.append(elem)

            elif isinstance(elem, str):
                loop_filter, self = self.process_filter_array(parse_filters(elem))

            else:
                raise SchemaQueryFilterError(
                    f"L'élément de liste de filtre {elem} est mal défini."
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
        return cur_filter, self

    def get_filter(self, filter):
        """
        get filter

        à voir ce qu'il y a pour les relations de type array(Object)
          - oneOf
          - allOf ??????
        """

        filter_out = None

        filter_field = filter["field"].strip()
        filter_type = filter["type"]
        filter_value = filter.get("value", None)

        model_attribute, self = self.getModelAttr(self.Model(), filter_field)

        if filter_type in ["like", "ilike"]:
            if "%" not in filter_value:
                filter_value = f"%{filter_value}%"
                if "_" in filter_value and "\\_" not in filter_value:
                    filter_value = filter_value.replace("_", "\\_")

                filter_value
            filter_out = getattr(unaccent(cast(model_attribute, db.String)), filter_type)(
                filter_value
            )

        elif filter_type == "~" and filter_value != "":
            filter_value_unaccent = unidecode.unidecode(filter_value)
            filters_out = []
            for v in filter_value_unaccent.split(" "):
                if "_" in v and "\\_" not in v:
                    v = v.replace("_", "\\_")
                filters_out.append(
                    getattr(unaccent(cast(model_attribute, db.String)), "ilike")(f"%{v}%")
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
                model_attribute
                == filter_value
                # or_(
                # model_attribute == filter_value,
                # cast(model_attribute, db.String) == (str(filter_value)),
            )

        elif filter_type == "!=":
            filter_out = cast(model_attribute, db.String) != (str(filter_value))

        elif filter_type == "in":
            filter_out = cast(model_attribute, db.String).in_([str(x) for x in filter_value])

        # filtre sur la distance à un point donnée
        elif filter_type == "dwithin":
            # if ";" in filter_value:
            #     # filter_value de type '<x>;<y>;radius'
            #     # - x : longitude du point
            #     # - y : lattitude du point
            #     # - radius : distance en m

            #     x, y, radius = filter_value.split(";")
            #     geo_filter = func.ST_DWithin(
            #         func.ST_GeogFromWKB(model_attribute),
            #         func.ST_GeogFromWKB(func.ST_MakePoint(x, y)),
            #         radius,
            #     )
            #     filter_out = geo_filter

            if ";" in filter_value:
                schema_code, value, geom_field, radius = filter_value.split(";")
                Model = SchemaMethods()(schema_code).Model()
                alias = orm.aliased(Model)
                self = self.join(alias, getattr(alias, Model.pk_field_name()) == value)
                geom = getattr(alias, geom_field)
                geo_filter = func.ST_DWithin(
                    func.ST_GeogFromWKB(model_attribute), func.ST_GeogFromWKB(geom), radius
                )
                filter_out = geo_filter

        # filtre de type bouding box :
        #   on souhaite que les données soient comprise dans un rectangle
        #   par exemple l'emprise d'une carte
        # filter_value de type '<x_min>;<y_min>;<x_max>;<y_max>'
        # - x_min(max) : longitude min(max) de la fenetre
        # - y_min(max) : lattitude min(max) de la fenetre

        elif filter_type == "bbox":
            x_min, y_min, x_max, y_max = filter_value.split(";")
            geo_filter = func.ST_Intersects(
                model_attribute,
                func.ST_SetSRID(func.ST_MakeEnvelope(x_min, y_min, x_max, y_max), 4326),
            )
            filter_out = geo_filter

        elif filter_type == "any":
            filter_out = model_attribute.any()

        else:
            raise SchemaQueryFilterTypeError(f"Le type de filtre {filter_type} n'est pas géré")

        return filter_out, self
