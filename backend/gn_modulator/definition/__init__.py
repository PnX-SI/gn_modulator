from .base import DefinitionBase
from .utils import DefinitionUtils
from .template import DefinitionTemplates
from .dynamic import DefinitionDynamic
from . import errors


class DefinitionMethods(DefinitionBase, DefinitionDynamic, DefinitionUtils, DefinitionTemplates):
    pass

    errors = errors
