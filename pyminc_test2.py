#!/usr/bin/env python

# import minc definitions
from libpyminc2 import *
from scipy import weave
from scipy.weave import converters
from sys import argv

# create a new mihandle and open a volume
test = mihandle()
libminc.miopen_volume(argv[1], 1, test)

# define a location, a voxel, and get that location from the mihandle
l = location(0,0,0)
v = voxel()
libminc.miget_real_value(test, l, 3, v)
print "Voxel: %f" % v.value

# get volume dimensions and their sizes
d = dimensions(0,0,0)
s = int_sizes(0,0,0)
libminc.miget_volume_dimensions(test, MI_DIMCLASS_SPATIAL, MI_DIMATTR_ALL,
				MI_DIMORDER_FILE, 3, d)
libminc.miget_dimension_sizes(d, 3, s)
print "sizes: %d %d %d " % (s[0], s[1], s[2])

# get a hyperslab of the whole volume as numpy array
start = long_sizes(0,0,0)
count = long_sizes(s[0],s[1],s[2])

narr = ascontiguousarray(zeros(s[0] * s[1] * s[2]))

print narr[0]
libminc.miget_real_value_hyperslab(test, MI_TYPE_DOUBLE, start, count, 
				   narr.ctypes.data_as(POINTER(c_double)))

# reshape the numpy array to be a 3D array like the volume
print narr[0]
print narr.shape

narr.shape = (s[0],s[1],s[2])
print narr.shape
print narr[0,0,0]


# cute trick - smooth the volume by iterative neighbourhood averages
import time
method = argv[2]
print "computing ten neighbourhood averages using %s method" % method
times = arange(10, dtype="double")
for i in range(10):
   starttime = time.clock()
   if method == "numpy":
      narr[1:-1,1:-1,1:-1] = (narr[0:-2,1:-1,1:-1] + 
			      narr[1:-1,0:-2,1:-1] + 
			      narr[1:-1,1:-1,0:-2] + 
			      narr[2:,1:-1,1:-1] + 
			      narr[1:-1,2:,1:-1] + 
			      narr[1:-1,1:-1,2:]) / 6
   elif method == "blitz":
      code = "narr[1:-1,1:-1,1:-1] = (narr[0:-2,1:-1,1:-1] + "\
	  "narr[1:-1,0:-2,1:-1] + "\
	  "narr[1:-1,1:-1,0:-2] + "\
	  "narr[2:,1:-1,1:-1] + "\
	  "narr[1:-1,2:,1:-1] + "\
	  "narr[1:-1,1:-1,2:]) / 6"
      weave.blitz(code, check_size=0)
   elif method == "weave":
      code = """
#line 68 "pyminc_test2.py"
for (int x=1; x<nx-1; ++x) {
  for (int y=1; y<ny-1; ++y) {
    for (int z=1; z<nz-1; ++z) {
       narr(x,y,z) = (narr(x-1,y,z) + narr(x+1,y,z) + 
                      narr(x,y-1,z) + narr(x,y+1,z) + 
                      narr(x,y,z-1) + narr(x,y,z+1)) / 6;
    }
  }
}
"""
      nx,ny,nz = s[0],s[1],s[2]
      weave.inline(code, ['narr', 'nx', 'ny', 'nz'], 
		   type_converters=converters.blitz,
		   compiler="gcc")

   times[i] = time.clock() - starttime
   print "Iterations %d took %.3f seconds" % (i,times[i])

print "done averaging. Took a total of %.3f seconds, averaging %.3f seconds" % (sum(times), average(times))

d_new_tmp = [0,0,0]
for i in range(3):
   d_new_tmp[i] = c_void_p()
   libminc.micopy_dimension(d[i], d_new_tmp[i])

d_new = dimensions(d_new_tmp[0], d_new_tmp[1], d_new_tmp[2])

new_volume = mihandle()
print "before volume"
libminc.micreate_volume(argv[3], 3, d_new, MI_TYPE_UBYTE, MI_CLASS_REAL, 
			None, new_volume)
libminc.micreate_volume_image(new_volume)
print "after volume"
libminc.miset_volume_valid_range(new_volume, 255, 0)
libminc.miset_volume_range(new_volume, narr.max(), narr.min())
print "before setting hyperslab"
libminc.miset_real_value_hyperslab(new_volume, MI_TYPE_DOUBLE, start, count,
				   narr.ctypes.data_as(POINTER(c_double)))
print "after setting hyperslab"
libminc.miclose_volume(new_volume)
