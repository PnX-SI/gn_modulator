'''
    SchemaMethods : reference schema
    
    load reference schema in schema_ref
'''

import json
from pathlib import Path
from geonature.utils.env import GN_EXTERNAL_MODULE
from gn_modules import MODULE_CODE


path_schema_ref = Path(GN_EXTERNAL_MODULE / MODULE_CODE.lower() / 'config/schemas/ref/schema.json')

# chargement du fichier de reference
with open(path_schema_ref, 'r') as f:
    schema_ref = json.load(f)
