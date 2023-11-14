from . import default as default
from . import iter as iter
from . import option as option
from . import ref as ref
from . import futures as futures
from .cfg import cfg as cfg
from .cfg import cfg_attr as cfg_attr
from .default import Default as Default
from .iter import Iter as Iter
from .iter import into_iter as into_iter
from .macros import deprecated as deprecated
from .macros import todo as todo
from .macros import unimplemented as unimplemented
from .option import Option as Option
from .option import Some as Some
from .ref import Ref as Ref
from .ref import RefMut as RefMut

__all__: tuple[str, ...]
__url__: str
__author__: str
__version__: str
__license__: str
