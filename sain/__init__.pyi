from . import boxed as boxed
from . import cell as cell
from . import default as default
from . import error as error
from . import futures as futures
from . import iter as iter
from . import macros as macros
from . import option as option
from . import result as result
from .boxed import Box as Box
from .cfg import cfg as cfg
from .cfg import cfg_attr as cfg_attr
from .default import Default as Default
from .error import Error as Error
from .iter import Iter as Iter
from .macros import deprecated as deprecated
from .macros import doc as doc
from .macros import todo as todo
from .macros import unimplemented as unimplemented
from .option import NOTHING as NOTHING
from .option import Option as Option
from .option import Some as Some
from .result import Err as Err
from .result import Ok as Ok
from .result import Result as Result
from .vec import Vec as Vec
from .vec import vec as vec

__all__: tuple[str, ...]
__url__: str
__author__: str
__version__: str
__license__: str
