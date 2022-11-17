from .base import DefinitionBase
from .utils import DefinitionUtils
from .template import DefinitionTemplates
from . import errors


class DefinitionMethods(DefinitionBase, DefinitionUtils, DefinitionTemplates):
    pass

    errors = errors
