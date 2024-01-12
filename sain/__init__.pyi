from . import futures as futures
from . import iter as iter
from .cfg import cfg as cfg
from .cfg import cfg_attr as cfg_attr
from .default import Default as Default
from .iter import Iter as Iter
from .macros import deprecated as deprecated
from .macros import todo as todo
from .macros import unimplemented as unimplemented
from .once import Once as Once
from .option import NOTHING as NOTHING
from .option import Option as Option
from .option import Some as Some
from .ref import AsMut as AsMut
from .ref import AsRef as AsRef

__all__: tuple[str, ...]
__url__: str
__author__: str
__version__: str
__license__: str
