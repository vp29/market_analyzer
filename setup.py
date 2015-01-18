from distutils.core import setup
from Cython.Build import cythonize
#python setup.py build_ext --inplace

setup(
  name = 'Least Squares',
  ext_modules = cythonize("function_script.pyx"),
)