import pathlib
import pkgutil

__all__ = []
__path__ = pkgutil.extend_path(__path__, __name__)

_src_pkg = pathlib.Path(__file__).resolve().parent.parent / "src" / "usecase"
if _src_pkg.exists():
    _src_str = str(_src_pkg)
    if _src_str not in __path__:
        __path__.append(_src_str)
    _init = _src_pkg / "__init__.py"
    if _init.exists():
        exec(compile(_init.read_text(), str(_init), "exec"), globals())
