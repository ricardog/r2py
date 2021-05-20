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

## Example

The following model

```R
library(lme4)
data(sleepstudy)
fm1 <- lmer(Reaction ~ Days + (Days | Subject), sleepstudy)
```

Will generate a Python file with the following

```python
from numba import jit, float32, int64
import numpy as np
import numpy.ma as ma
import r2py.poly as poly


@jit(#[float32[:](float32)],
     cache=True, nopython=True, nogil=True)
def test1(days):
  res = np.empty(days.size, dtype=np.float32)
  for idx in np.arange(days.size):
    
    res[idx] = ((np.float32(1) * np.float32(251.405105)) + (days[idx] * np.float32(10.467286)))
  return res


def test1_st(df):
  return test1(df['days'])

def inputs():
  return ['days']

def output():
  return "Reaction"

def output_range():
  return (194.3322, 466.3535)

def func_name():
  return "test1"
```
