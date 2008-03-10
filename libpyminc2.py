#/usr/bin/env python

from ctypes import *
from numpy import *

# load the library
#libminc = CDLL("/projects/mice/share/arch/linux64/lib/libminc2.so")
libminc = CDLL("/usr/local/minc2/lib/libminc2.dylib")

# some typedef definitions
MI_DIMCLASS_SPATIAL = c_int(1)
MI_DIMATTR_ALL = c_int(0)
MI_DIMORDER_FILE = c_int(0)
MI_TYPE_DOUBLE = c_int(6)
MI_TYPE_UBYTE = c_int(100)
MI_CLASS_REAL = c_int(0)

# opaque minc structs can be represented as pointers
mihandle = c_void_p
midimhandle = c_void_p

# some type information
dimensions = c_void_p * 5
voxel = c_double
location = c_ulong * 5
int_sizes = c_int * 5
long_sizes = c_ulong * 5

# argument declarations - not really necessary but does make
# segfaults a bit easier to avoid.
libminc.miopen_volume.argtypes = [c_char_p, c_int, POINTER(mihandle)]
libminc.miget_real_value.argtypes = [mihandle, location, c_int, POINTER(voxel)]
libminc.miget_volume_dimensions.argtypes = [mihandle, c_int, c_int, c_int,
					    c_int, dimensions]
libminc.miget_dimension_sizes.argtypes = [dimensions, c_int, int_sizes]
libminc.miget_real_value_hyperslab.argtypes = [mihandle, c_int, long_sizes,
					       long_sizes, POINTER(c_double)]
libminc.micopy_dimension.argtypes = [c_void_p, POINTER(c_void_p)]
libminc.micreate_volume.argtypes = [c_char_p, c_int, dimensions, c_int, c_int,
				    c_void_p, POINTER(mihandle)]
libminc.micreate_volume_image.argtypes = [mihandle]
libminc.miset_volume_valid_range.argtypes = [mihandle, c_double, c_double]
libminc.miset_volume_range.argtypes = [mihandle, c_double, c_double]
libminc.miset_real_value_hyperslab.argtypes = [mihandle, c_int, long_sizes,
					       long_sizes, POINTER(c_double)]
libminc.miclose_volume.argtypes = [mihandle]
