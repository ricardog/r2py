
import importlib
import numpy as np
import os
import re
import sys

class Model(object):
  def __init__(self, name, pkg, func, inputs, out_name):
    self._name = name
    self._pkg = pkg
    self._func = func
    self._inputs = inputs
    self._out_name = out_name

  @property
  def name(self):
    return self._name

  @property
  def syms(self):
    return self._inputs

  @property
  def hstab(self):
    return {}

  @property
  def output(self):
    return self._out_name

  ## FIXME: This function is PREDICTS specific and should move to out of
  ## this package.
  @property
  def intercept(self):
    ins = map(lambda x: np.array([0.0]) if x == 'logHPD_rs' \
              else np.array([0.0]) if x == 'LogHPD_s2' \
              else np.array([0.0]) if x == 'LogHPD_diff' \
              else np.array([1.0]) if x == 'logDTR_rs' \
              else np.array([0.0]), self._inputs)
    func_name = getattr(self._pkg, 'func_name')()
    func = getattr(self._pkg, func_name)
    return func(*ins)

  def partial(self, df):
    shape = tuple(df.values())[0].shape
    dtype = tuple(df.values())[0].dtype
    for arg in self._inputs:
      if arg not in df:
        df[arg] = np.zeros(shape, dtype=dtype)
    return self.eval(df)
    ins = map(lambda x: np.linspace(0, 1.2, 13) if x == 'logHPD_rs' \
              else np.linspace(0, 10.02, 13) if x == 'LogHPD_s2' \
              else np.linspace(0, -10.02, 13) if x == 'LogHPD_diff' \
              else np.full(13, 1.0, dtype=np.float32) if x == 'logDTR_rs' \
              else np.zeros((13), dtype=np.float32), self._inputs)
    func_name = getattr(self._pkg, 'func_name')()
    func = getattr(self._pkg, func_name)
    return func(*ins)
  
  def eval(self, df):
    return self._func(df)
  
def read_py(fname):
  path, name = os.path.split(fname)
  pkg_name, ext = os.path.splitext(name)
  if path not in sys.path:
    sys.path.append(path)
  pkg = importlib.import_module(pkg_name)
  func_name = getattr(pkg, 'func_name')()
  func = getattr(pkg, func_name + '_st')
  inputs = getattr(pkg, 'inputs')()
  out_name = getattr(pkg, 'output')()
  return Model(pkg_name, pkg, func, inputs, out_name)

def load(path):
  if not os.path.isfile(path):
    raise RuntimeError('no such file: %s' % path)
  pypath = os.path.splitext(path)[0] + '.py'
  if (os.path.isfile(pypath) and
      os.path.getmtime(pypath) > os.path.getmtime(path)):
    #print("loading %s" % pypath)
    return read_py(pypath)
  print("compiling %s" % path)
  return read_py(_compile(path))

def _compile(fname):
  import rpy2.robjects as robjects

  from ..r2py import glm
  from ..r2py import lmermod
  from ..r2py import glmermod
  from .. import predicts

  def doit(obj):
    if 'lmerMod' in obj.rclass:
      mod = lmermod.LMerMod(obj)
    elif 'glmerMod' in obj.rclass:
      mod = glmermod.GLMerMod(obj)
    elif 'glm' in obj.rclass or 'lm' in obj.rclass:
      mod = glm.GLM(obj)
    else:
      print('Skipping object of type %s' % str(obj.rclass))
      return None
    predicts.predictify(mod)
    return mod
  
  name = os.path.basename(fname)
  base = os.path.splitext(name)[0]
  pname = re.sub(r'[ \-.$]', '_', base)
  outdir = os.path.dirname(fname)
  oname = os.path.join(outdir, base + '.py')
  
  print('%s:' % name)
  with open(oname, 'w') as ofile:
    obj = robjects.r('models <- readRDS("%s")' % fname)
    if 'list' in obj.rclass:
      for mm in obj.items():
        print("  %s" % mm[0])
        mod = doit(mm[1])
        if mod:
          ofile.write(mod.to_numba(mm[0]))
    else:
      mod = doit(obj)
      if mod:
        ofile.write(mod.to_numba(pname))
  return(oname)
