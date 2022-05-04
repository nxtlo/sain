# sain
A pure Python package that provides Rust style `#[cfg_attr]` and `cfg!` macros for Python.

This allows to run specific code when all conditions return True.

## Install
You'll need Python 3.8 or higher.

Still not on PyPI
```rs
$ pip install git+https://github.com/nxtlo/sain
```

## Example
```py
import sain

# This function will not run unless the target OS either linux or darwin.
@sain.cfg_attr(target_os = "unix")
def run_when_unix() -> None:
    import uvloop
    uvloop.install()

# If this returns True, run_when_unix will run, otherwise returns.
if sain.cfg(requires_modules = ("dotenv"), python_version = (3, 10, 0)):
    run_when_unix()

@sain.cfg_attr(target_os = 'win32')
class PotFriend:
    
    @staticmethod
    @sane.cfg_attr(requires_modules = 'hikari')
    def light(x: int, y: int) -> int:
        result = x * y if sain.cfg(python_version = (3.10.0)) else x + y
        return result
```

In Rust that'll be something like this.

```rs
#[cfg_attr(target_os = "windows")]
fn main() -> ! {
    loop {}
}
```

And since Rust is a compiled language, The main function will only be compiled if the target was windows.

But there's no such thing as this in Python, So only an error will be raised and whatever was predicated will not run.
