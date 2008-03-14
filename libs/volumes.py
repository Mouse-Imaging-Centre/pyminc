from libpyminc2 import *
import operator

class mincException(Exception): pass
class NoDataException(Exception): pass
class IncorrectDimsException(Exception): pass

def testMincReturn(value):
    if value < 0:
        raise mincException

class mincVolume(object):
    def __init__(self, filename=None):
        self.volPointer = mihandle() # holds the pointer to the mihandle
        self.dims = dimensions()     # holds the actual pointers to dimensions
        self.sizes = int_sizes()     # holds dimension sizes info
        self.dataLoadable = False    # we know enough about the file on disk to load data
        self.dataLoaded = False      # data sits inside the .data attribute
        self.dtype = "float"         # default datatype for array representation
        if filename: self.openFile(filename)
    def getdata(self):
        """called when data attribute requested"""
        #print "getting data"
        if not self.dataLoaded:
            self.loadData()
            self.dataLoaded = True
        return self._data
    def setdata(self, newdata):
        """sets the data attribute"""
        if newdata.shape != tuple(self.sizes[0:self.ndims]):
            print "Shapes", newdata.shape, self.sizes[0:self.ndims]
            raise IncorrectDimsException
        elif self.dataLoadable == False:
            raise NoDataException
        else:
            self._data = newdata
            self.dataLoaded = True
            print "New Shape:", self.data.shape
    def writeToFile(self):
        pass
    def loadData(self, dtype="float"):
        """loads the data from file into the data attribute"""
        print "size", self.sizes[:]
        if self.dataLoadable:
            self._data = self.getHyperslab(int_sizes(), self.sizes[0:self.ndims], 
                                           dtype)
            self._data.shape = self.sizes[0:self.ndims]
            self.dataLoaded = True
            self.dtype = dtype
        elif self.ndims > 0:
            length = reduce(operator.mul, self.sizes[0:self.ndims])
            self._data = ascontiguousarray(zeros(length))
            self._data.shape = self.sizes[0:self.ndims]
        else: 
            raise NoDataException
    def getHyperslab(self, start, count, dtype="float"):
        """given starts and counts returns the corresponding array"""
        if self.dataLoadable == False:
            raise NoDataException
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
            # return real values if datatpye is floating point
            r = libminc.miget_real_value_hyperslab(
                self.volPointer, 
                mincSizes[dtype]["minc"],
                start, count, 
                a.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
            
        else :
            # return normalized values if datatype is integer
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
        """reads information from MINC file"""
        r = libminc.miopen_volume(filename, 1, self.volPointer)
        testMincReturn(r)
        ndims = c_int(0)
        libminc.miget_volume_dimension_count(self.volPointer,
                                             MI_DIMCLASS_SPATIAL,
                                             MI_DIMATTR_ALL,
                                             ndims)
        self.ndims = ndims.value
        r = libminc.miget_volume_dimensions(
            self.volPointer, MI_DIMCLASS_SPATIAL,
            MI_DIMATTR_ALL, MI_DIMORDER_FILE,
            ndims, self.dims)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, ndims, self.sizes)
        print "sizes", self.sizes[0:self.ndims]
        testMincReturn(r)
        self.dataLoadable = True
    def copyDimensions(self, otherInstance):
        """create new local dimensions info copied from another instance"""
        self.ndims = c_int(otherInstance.ndims)
        tmpdims = range(self.ndims.value)
        for i in range(self.ndims.value):
            tmpdims[i] = c_void_p(0)
            r = libminc.micopy_dimension(otherInstance.dims[i], tmpdims[i])
            print r, otherInstance.dims[i], tmpdims[i]
            testMincReturn(r)
        self.dims = apply(dimensions, tmpdims[0:self.ndims.value])
        self.ndims = otherInstance.ndims
    def copyDtype(self, otherInstance):
        """copy the datatype to use for this instance from another instance"""
        self.dtype = otherInstance.dtype
    def createVolumeHandle(self, filename):
        """creates a new volume on disk"""
        self.volPointer = mihandle()
        r = libminc.micreate_volume(filename, self.ndims, self.dims, 
                                    mincSizes[self.dtype]["minc"], MI_CLASS_REAL,
                                    None, self.volPointer)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, self.ndims, self.sizes)
        print "sizes", self.sizes[0:self.ndims]
        testMincReturn(r)
    def createVolumeImage(self):
        """creates the volume image on disk"""
        r = libminc.micreate_volume_image(self.volPointer)
        testMincReturn(r)
        self.dataLoadable = True
    def closeVolume(self):
        """close volume and release all pointer memory"""
        r = libminc.miclose_volume(self.volPointer)
        testMincReturn(r)
        for i in range(self.ndims):
            r = libminc.mifree_dimension_handle(self.dims[i])
            testMincReturn(r)
        self.dataLoadable = False
    def __getitem__(self, i): return self.data[i]
    #def __repr__(self): return self.data
    data = property(getdata,setdata,None,None)
