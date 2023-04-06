import pytest

from flask import url_for
from gn_modulator import SchemaMethods, ModuleMethods
from geonature.tests.utils import set_logged_user_cookie, unset_logged_user_cookie


@pytest.mark.skip()
def test_schema_rest(client, user, module_code, object_code, data_post, data_update):
    """
    Test chainage sur les api rest
        - get (vide)
        - post
        - get
        - patch
        - delete
        - get(vide)
    """

    # patch cruved for tests
    ModuleMethods.add_actions(module_code, object_code, "CUD")

    # INIT
    set_logged_user_cookie(client, user)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    assert schema_code is not None
    sm = SchemaMethods(schema_code)
    field_name = sm.unique()
    data_unique = ",".join(list(map(lambda x: data_post[x], field_name)))

    # GET VIDE
    r = client.get(
        url_for(
            "modulator.api_rest_get_one",
            value=data_unique,
            module_code=module_code,
            object_code=object_code,
            field_name=field_name,
        )
    )
    assert r.status_code == 404, "La donnée ne devrait pas exister"

    # POST
    fields = list(data_post.keys())
    fields.append(sm.pk_field_name())

    r = client.post(
        url_for(
            "modulator.api_rest_post",
            module_code=module_code,
            object_code=object_code,
            fields=",".join(fields),
        ),
        data=data_post,
    )

    assert r.status_code == 200, "Erreur avec POST"

    data_from_post = r.json
    assert all(data_post[k] == data_from_post[k] for k in list(data_post.keys()))

    assert sm.pk_field_name() in data_from_post
    id = data_from_post[sm.pk_field_name()]

    # GET OK
    r = client.get(
        url_for(
            "modulator.api_rest_get_one",
            value=id,
            module_code=module_code,
            object_code=object_code,
        )
    )
    assert r.status_code == 200, "Erreur avec GET"

    # PATCH
    r = client.patch(
        url_for(
            "modulator.api_rest_patch",
            value=id,
            module_code=module_code,
            object_code=object_code,
            fields=",".join(list(data_update.keys())),
        ),
        data=data_update,
    )

    assert r.status_code == 200, "Erreur avec PATCH"
    data_from_patch = r.json
    assert all(data_update[k] == data_from_patch[k] for k in list(data_update.keys()))

    # DELETE
    r = client.delete(
        url_for(
            "modulator.api_rest_delete",
            value=id,
            module_code=module_code,
            object_code=object_code,
        )
    )

    assert r.status_code == 200, "Erreur avec DELETE"
    # GET VIDE
    r = client.get(
        url_for(
            "modulator.api_rest_get_one",
            value=data_unique,
            module_code=module_code,
            object_code=object_code,
            field_name=field_name,
        )
    )
    assert r.status_code == 404, "La donnée n'a pas été effacée"

    # FINALIZE
    unset_logged_user_cookie(client)
