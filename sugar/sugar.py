import ctypes
import os

import numpy as np

file_dir = os.path.os.path.dirname(__file__)
pkg_root = os.path.abspath(os.path.join(file_dir, "../"))
dylib_dir = os.path.join(pkg_root, "build")
dylib_path = os.path.join(dylib_dir, "libsugar.dylib")

# print(file_dir, pkg_root, dylib_dir, dylib_path)

ctypes.cdll.LoadLibrary(dylib_path)
_lib = ctypes.CDLL(dylib_path)

initialize = _lib.initialize
# initialize.argtypes = []
# initialize.restype = ctypes.

sum_double_np_array = _lib.sum_double_np_array
sum_double_np_array.argtypes = [np.ctypeslib.ndpointer(dtype=np.float64), ctypes.c_int]
sum_double_np_array.restype = ctypes.c_double

def sugar_sum(x):
    return sum_double_np_array(x, len(x))