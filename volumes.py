from libpyminc2 import *
import operator


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
    def openFile(self, filename):
	libminc.miopen_volume(filename, 1, self.volPointer)
	libminc.miget_volume_dimensions(self.volPointer, MI_DIMCLASS_SPATIAL,
					MI_DIMATTR_ALL, MI_DIMORDER_FILE,
					3, self.dims)
	libminc.miget_dimension_sizes(self.dims, 3, self.sizes)
	start = long_sizes(0,0,0)
	count = long_sizes(self.sizes[0], self.sizes[1], self.sizes[2])
	self._data = ascontiguousarray(zeros(reduce(operator.mul, count[0:3])))
	libminc.miget_real_value_hyperslab(self.volPointer, MI_TYPE_DOUBLE,
					   start, count,
					   self._data.ctypes.data_as(POINTER(c_double)))
	self._data.shape = self.sizes[0:3]
	self.dataLoaded = True
    def __getitem__(self, i): return self.data[i]
    #def __repr__(self): return self.data
    data = property(getdata,None,None,None)

