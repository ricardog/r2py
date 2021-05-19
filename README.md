# r2py

This project is a very simple Python library that can "compile"
mixed-effect R models (fitted using `lme4`) into Python modules. 

The script uses `rpy2` to interface with `R` (so you need a working
version of `R` that can load the models you want to compile) to get the
model equation.  It parses the equation into a simple AST and feeds that
to one of several backends.  The backend walks the tree generating the
output.

I mostly use the [Numba](https://numba.pydata.org/) backend.  It
generates Python functions annotated for jit-ing.

The code is terribly simple and works with the models that I feed it.
But YMMV due to the enormous complexity of the `R` equation language.

The generated code needs access to this package (`r2py`) as it expects
to import a module with some utility functions.
