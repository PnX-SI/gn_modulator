'''
    repositories - filters
'''
import unidecode

from sqlalchemy import cast, and_, or_, not_

from geonature.utils.env import db

from ..errors import (
    SchemaRepositoryFilterError,
    SchemaRepositoryFilterTypeError
)

from sqlalchemy.sql.functions import ReturnTypeFromArgs

class unaccent(ReturnTypeFromArgs):
    pass

filter_types = ['like', 'ilike', '=', 'in', '>e', '<', '>=', '>=']


class SchemaRepositoriesFilters():
    '''
        repositories - filters

    '''

    __abstract__ = True

    def process_filters(self, Model, filters, query):
        '''
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
        '''

        filters_processed, query = self.process_filter_array(Model, filters, query)

        if filters_processed is not None:
            return query.filter(filters_processed)

        return query

    def process_filter_array(self, Model, filter_array, query=None, condition=None):
        '''
            process filter list

            traite un liste qui peux contenir
                - des listes (traitement récursif)
                - des filtres : { field : <f_field>, type: <f_type>, value: <f_value>}
                - des operateurs :
                    - '!' : négation, unitaire
                    - '*' : et
                    - '+ : ou

            l'opérateur par défaut est '*':

            exemples (f1 et f2 sont des filtres):

                - [ f1, '*', f2]                  =>  f1 ET f2
                - [ f1, '+', f2]                  =>  f1 OU f2
                - [ f1, f2]                       =>  f1 ET f2
                - [ '!', f1, '+', '!', f2]        =>  (NON f1) OU (NON f2)
                - [ '!', [ f1, '+', '!', f2 ] ]   =>  NON (f1 OU (NON f2))
        '''
        cur_filter = None
        cur_ops = []

        for elem in filter_array:

            loop_filter = None

            # récursivité sur les listes
            if isinstance(elem, list):
                loop_filter, query = self.process_filter_array(Model, elem, query, condition)

            # filtre
            elif isinstance(elem, dict):
                loop_filter, query = self.get_filter(Model, elem, query, condition)

            # operation
            elif elem in '!+*':
                # deux négations '!' s'annulent
                if elem == '!' and len(cur_ops) > 0 and cur_ops[-1] == '!':
                    cur_ops = cur_ops[:-1]
                else:
                    cur_ops.append(elem)

            else:
                raise SchemaRepositoryFilterError(
                    "L'élément de liste de filtre {} est mal défini."
                    .format(elem)
                )

            if loop_filter is not None:

                # on prend le dernier opérateur de la liste ou bien '*' par défaut
                op = cur_ops.pop() if len(cur_ops) > 0 else "*"

                # traitement de la négation '!'
                if op == '!':
                    loop_filter = not_(loop_filter)
                    # on prend le dernier opérateur de la liste ou bien '*' par défaut
                    op = cur_ops.pop() if len(cur_ops) > 0 else "*"

                # s'il y un filtre courant, on applique l'opération en cours
                if cur_filter is not None:
                    if op == '*':
                        cur_filter = and_(cur_filter, loop_filter)
                    if op == '+':
                        cur_filter = or_(cur_filter, loop_filter)

                # s'il n'y a pas de filtre courant, on initialise la variable cur_filter
                else:
                    cur_filter = loop_filter
        return cur_filter, query

    def get_filter(self, Model, f, query=None, condition=None):
        '''
            get filter

            à voir ce qu'il y a pour les relations de type array(Object)
              - oneOf
              - allOf ??????
        '''

        filter_out = None

        f_field = f['field']
        f_type = f['type']
        f_value = f.get('value', None)

        model_attribute, query = self.custom_getattr(Model, f_field, query, condition)

        # si besoin de redefinir type

        # pour ilike et like, on teste sans tenir compte des accents
        if f_type in ['like', 'ilike']:
            f_value_unaccent = unidecode.unidecode(f_value)
            filter_out = (
                getattr(
                    unaccent(
                        cast(model_attribute, db.String)
                    ),
                    f_type
                )('{}'.format(f_value_unaccent))
            )

        elif f_type == '>':
            filter_out = (model_attribute > f_value)
        elif f_type == '>=':
            filter_out = (model_attribute >= f_value)
        elif f_type == '<':
            filter_out = (model_attribute < f_value)
        elif f_type == '<=':
            filter_out = (model_attribute <= f_value)

        elif f_type == '=':
            filter_out = (
                cast(model_attribute, db.String) == (str(f_value))
            )

        elif f_type == '!=':
            filter_out != (
                cast(model_attribute, db.String) == (str(f_value))
            )


        elif f_type == 'in':
            filter_out = (
                cast(model_attribute, db.String)
                .in_(
                    [str(x) for x in f_value]
                    # map(
                    #     lambda x: str(x),
                    #     f_value
                    # )
                )
            )

        else:
            raise SchemaRepositoryFilterTypeError(
                "Le type de filtre {} n'est pas géré"
                .format(f_type)
            )

        return filter_out, query
