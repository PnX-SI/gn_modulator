"""
    Test pour valider les fonctionalité repository
    - get_one
    - insert
    - update
    - delete
    - list ??
"""

import pytest
from .utils.repository import test_schema_repository
from .data import commons as data_commons
from .data import meta as data_meta
from gn_modulator import SchemaMethods, ModuleMethods, DefinitionMethods
from gn_modulator import SchemaMethods
from gn_modulator.query.repository import query_list
from gn_modulator.query.utils import pretty_sql
from .fixtures import passages_faune_with_diagnostic
from geonature.tests.fixtures import *
from geonature.tests.test_permissions import g_permissions
from geonature.utils.env import db


@pytest.mark.usefixtures("client_class", "temporary_transaction", "g_permissions")
class TestExport:
    def test_sql_export(self):
        schema_code = "m_sipaf.pf"
        export_code = "m_sipaf.pf"
        module_code = "m_sipaf.pf"
        sm = SchemaMethods(schema_code)
        params = DefinitionMethods.get_definition("export", export_code)

        headers, fields = sm.process_export_fields(params["fields"], True)

        action = "R"

        # recupération de la liste
        q = query_list(
            sm.Model(),
            module_code=module_code,
            action=action,
            params={"fields": fields},
            query_type="select",
        )

        sql_txt = sm.process_export_sql(q, params)
        SchemaMethods.c_sql_exec_txt(sql_txt)
