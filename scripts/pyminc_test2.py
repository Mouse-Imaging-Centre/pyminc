#!/usr/bin/env python3


from argparse import ArgumentParser
from sys import argv
import time

from pyminc.volumes.libpyminc2 import *
from pyminc.volumes.volumes import *


def minc_test(input, method, output):

   # create a new mihandle and open a volume
   starttime = time.clock()
   test = mihandle()
   libminc.miopen_volume(input, 1, test)
   print("Opening volume took %.5f seconds" % (time.clock() - starttime))
   
   # define a location, a voxel, and get that location from the mihandle
   l = location(0,0,0)
   v = voxel()
   libminc.miget_real_value(test, l, 3, v)
   print("Voxel: %f" % v.value)
   
   # get volume dimensions and their sizes
   d = dimensions(0,0,0)
   s = int_sizes(0,0,0)
   libminc.miget_volume_dimensions(test, MI_DIMCLASS_SPATIAL, MI_DIMATTR_ALL,
                                   MI_DIMORDER_FILE, 3, d)
   libminc.miget_dimension_sizes(d, 3, s)
   print("sizes: %d %d %d " % (s[0], s[1], s[2]))
   
   # get a hyperslab of the whole volume as numpy array
   start = long_sizes(0,0,0)
   count = long_sizes(s[0],s[1],s[2])

   narr = ascontiguousarray(zeros(s[0] * s[1] * s[2], dtype='int32'))

   print(narr[0])
   starttime = time.clock()
#libminc.miget_real_value_hyperslab(test, 5, start, count, 
#                                   narr.ctypes.data_as(POINTER(c_float)))
   libminc.miget_hyperslab_normalized(test, 4, start, count,
                                      c_double(-2147483648),
                                      c_double(2147483647),
                                      narr.ctypes.data_as(POINTER(c_int)))
   print("Getting hyperslab took %.5f seconds" % (time.clock() - starttime))
   print(narr[100000])
   # reshape the numpy array to be a 3D array like the volume
   print(narr[0])
   print(narr.shape)
   
   narr.shape = (s[0],s[1],s[2])
   print(narr.shape)
   print(narr[0,0,0])
   
   
   # cute trick - smooth the volume by iterative neighbourhood averages
   print("computing ten neighbourhood averages using %s method" % method)
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
       else:
          raise ValueError("unknown method: %s" % method)

       times[i] = time.clock() - starttime
       print("Iterations %d took %.3f seconds" % (i,times[i]))

   print("done averaging. Took a total of %.3f seconds, averaging %.3f seconds" % (sum(times), average(times)))

   d_new_tmp = [0,0,0]
   for i in range(3):
      d_new_tmp[i] = c_void_p()
      libminc.micopy_dimension(d[i], d_new_tmp[i])

   d_new = dimensions(d_new_tmp[0], d_new_tmp[1], d_new_tmp[2])

   new_volume = mihandle()
   print("before volume")
   starttime = time.clock()
   libminc.micreate_volume(output, 3, d_new, MI_TYPE_UBYTE, MI_CLASS_REAL, 
                           None, new_volume)
   libminc.micreate_volume_image(new_volume)
   print("after volume")
   vmin = 0.0
   vmax = 255.0
   rmax = narr.max()
   rmin = narr.min()
   print("max and min", rmax, rmin)
   out_array = array( (((narr+0.0) - rmin)/(rmax-rmin)*(vmax-vmin)) + vmin, dtype='ubyte')
   print(out_array.shape)
   libminc.miset_volume_valid_range(new_volume, 255, 0)
   libminc.miset_volume_range(new_volume, narr.max(), narr.min())
   print("Creating new volume took %.5f seconds" % (time.clock() - starttime))
   print("before setting hyperslab")
   starttime = time.clock()
   dim_1 = s[0] - 1
   dim_2 = s[1] - 1
   dim_3 = s[2] - 1
   print(narr[dim_1,dim_2,dim_3])
   print((((narr[dim_1,dim_2,dim_3] - rmin)/(rmax-rmin)*(vmax*vmin)) + vmin))
   print(out_array[dim_1,dim_2,dim_3], out_array.max(), out_array.min(), average(out_array))
   print(narr.dtype, out_array.dtype)
   print(out_array)
#libminc.miset_real_value_hyperslab(new_volume, 4, start, count,
#                                   narr.ctypes.data_as(POINTER(c_int)))
   libminc.miset_voxel_value_hyperslab(new_volume, MI_TYPE_UBYTE,
                                       start, count,
                                       out_array.ctypes.data_as(POINTER(c_ubyte)))
   print("Setting hyperslab took %.5f seconds" % (time.clock() - starttime))
   libminc.miclose_volume(new_volume)

if __name__ == "__main__":
    main(argv[1:])

def main(args):
    p = ArgumentParser(help = "Perform some very basic operations using the pyminc library.")
    p.add_argument("infile")  # TODO add ".mnc" to example
    p.add_argument("method", choices = ["numpy"])  # TODO add numba, cython, pytorch
    p.add_argument("outfile")
    args = p.parse_args()
    minc_test(input = args.infile, method = args.method, output = args.outfile)
