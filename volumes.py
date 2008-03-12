from libpyminc2 import *
import operator

class mincException(Exception): pass

def testMincReturn(value):
    if value < 0:
        raise mincException

class mincVolume(object):
    def __init__(self, filename=None):
	self.volPointer = mihandle()
	self.dims = dimensions()
	self.sizes = int_sizes()
	self.dataLoaded = False
	if filename: self.openFile(filename)
    def getdata(self):
	if self.dataLoaded:
	    print "getting data"
	    return self._data
	else:
	    print "data not loaded yet"
	    return None
    def writeToFile(self):
	pass
    def loadData(self, dtype=None):
        print "size", self.sizes[:]
        self._data = self.getHyperslab(int_sizes(), self.sizes[0:self.ndims], 
                                       dtype)
	self._data.shape = self.sizes[0:3]
	self.dataLoaded = True
    def getHyperslab(self, start, count, dtype=None):
        print "count", count
        nstart = array(start[:self.ndims])
        ncount = array(count[:self.ndims])
        start = apply(long_sizes, nstart[:])
        count = apply(long_sizes, ncount[:])
        size = reduce(operator.mul, ncount-nstart)
        print nstart[:], ncount[:], size
        a = ascontiguousarray(zeros(size, dtype=mincSizes[dtype]["numpy"]))
        r = 0
        if dtype == "float" or dtype == "double":
            r = libminc.miget_real_value_hyperslab(
                self.volPointer, 
                mincSizes[dtype]["minc"],
                start, count, 
                a.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
        else :
            r = libminc.miget_hyperslab_normalized(
                self.volPointer,
                mincSizes[dtype]["minc"],
                start, count,
                c_double(mincSizes[dtype]["min"]),
                c_double(mincSizes[dtype]["max"]),
                a.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
        testMincReturn(r)
        return a
    def openFile(self, filename):
	r = libminc.miopen_volume(filename, 1, self.volPointer)
        testMincReturn(r)
        ndims = c_int(0)
        libminc.miget_volume_dimension_count(self.volPointer,
                                             MI_DIMCLASS_SPATIAL,
                                             MI_DIMATTR_ALL,
                                             byref(ndims))
        self.ndims = ndims.value
	r = libminc.miget_volume_dimensions(
            self.volPointer, MI_DIMCLASS_SPATIAL,
            MI_DIMATTR_ALL, MI_DIMORDER_FILE,
            ndims, self.dims)
        testMincReturn(r)
	r = libminc.miget_dimension_sizes(self.dims, ndims, self.sizes)
        print "sizes", self.sizes[0:self.ndims]
        testMincReturn(r)
    def __getitem__(self, i): return self.data[i]
    #def __repr__(self): return self.data
    data = property(getdata,None,None,None)

