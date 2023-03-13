from gn_modulator.schema.errors import SchemaRepositoryFilterError, SchemaRepositoryFilterTypeError


def parse_filters(filters):
    """
    traite une liste de chaine de caractères représentant des filtres
    """

    if not filters:
        return []

    if isinstance(filters, str):
        return parse_filters(filters.split(","))

    filters_out = []

    nb_filters = len(filters)
    index = 0
    while index < nb_filters:
        # calcul du filtre {field, type, value}
        filter = parse_filter(filters[index])

        # si on tombe sur une parenthèse ouvrante
        if filter == "[":
            # on cherche l'index de la parenthèse fermante ] correspondante
            index_close = find_index_close(index, filters)

            # on calcule les filtres entre les deux [...]
            filters_out.append(parse_filters(filters[index + 1 : index_close]))

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


def parse_filter(str_filter):
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


def find_index_close(index_open, filters):
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
    raise Exception(f"Pas de parenthèse fermante trouvée {','.join(filters[index_open:])}")
