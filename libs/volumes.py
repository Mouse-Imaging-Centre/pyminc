from libpyminc2 import *
import operator

class mincException(Exception): pass
class NoDataException(Exception): pass
class IncorrectDimsException(Exception): pass

def testMincReturn(value):
    if value < 0:
        raise mincException

class mincVolume(object):
    def __init__(self, filename=None, dtype="float"):
        self.volPointer = mihandle() # holds the pointer to the mihandle
        self.dims = dimensions()     # holds the actual pointers to dimensions
        self.ndims = 0               # number of dimensions in this volume
        self.sizes = int_sizes()     # holds dimension sizes info
        self.dataLoadable = False    # we know enough about the file on disk to load data
        self.dataLoaded = False      # data sits inside the .data attribute
        self.dtype = dtype           # default datatype for array representation
        self.filename = filename     # the filename associated with this volume

    def getDtype(self, data):
        """get the mincSizes datatype based on a numpy array"""
        dtype = None
        for type in mincSizes:
            print "TYPE:", type, data.dtype
            if mincSizes[type]["numpy"] == data.dtype:
                dtype = type
                break
        return dtype
    def getdata(self):
        """called when data attribute requested"""
        print "getting data"
        if self.ndims > 0:
            if not self.dataLoaded:
                self.loadData()
                self.dataLoaded = True
            return self._data
        else:
            raise NoDataException
    def setdata(self, newdata):
        """sets the data attribute"""
        print "setting data"
        if newdata.shape != tuple(self.sizes[0:self.ndims]):
            print "Shapes", newdata.shape, self.sizes[0:self.ndims]
            raise IncorrectDimsException
        #elif self.dataLoadable == False:
        #    raise NoDataException
        else:
            self._data = newdata
            self.dataLoaded = True
            print "New Shape:", self.data.shape
    def writeToFile(self):
        pass
    def loadData(self):
        """loads the data from file into the data attribute"""
        print "size", self.sizes[:]
        if self.dataLoadable:
            self._data = self.getHyperslab(int_sizes(), self.sizes[0:self.ndims], 
                                           self.dtype)
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
    def setHyperslab(self, data, start):
        """write hyperslab back to file"""
        count = apply(long_sizes, data.shape)
        start = apply(long_sizes, start)
        # find the datatype map index
        dtype = self.getDtype(data)
        self.setVolumeRanges(data)
        if dtype == "float" or dtype == "double":
            r = libminc.miset_real_value_hyperslab(
                    self.volPointer, mincSizes[dtype]["minc"],
                    start, count,
                    data.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
            testMincReturn(r)
        else:
            raise "setting hyperslab with types other than float or byte not yet supported"
    def writeFile(self):
        """write the current data array to file"""
        self.setHyperslab(self.data, zeros(self.ndims, dtype='uint8').tolist())
    def setVolumeRanges(self, data):
        """sets volume and voxel ranges"""
        # ignore slice scaling for the moment
        max = data.max()
        min = data.min()
        vmax = mincSizes[self.volumeType]["max"]
        vmin = mincSizes[self.volumeType]["min"]
        r = libminc.miset_volume_range(self.volPointer, max, min)
        testMincReturn(r)
        r = libminc.miset_volume_valid_range(self.volPointer, vmax, vmin)
    def openFile(self):
        """reads information from MINC file"""
        r = libminc.miopen_volume(self.filename, 1, self.volPointer)
        testMincReturn(r)
        ndims = c_int(0)
        libminc.miget_volume_dimension_count(self.volPointer,
                                             MI_DIMCLASS_SPATIAL,
                                             MI_DIMATTR_ALL,
                                             ndims)
        self.ndims = ndims.value
        r = libminc.miget_volume_dimensions(
            self.volPointer, MI_DIMCLASS_SPATIAL,
            MI_DIMATTR_ALL, MI_DIMORDER_APPARENT,
            ndims, self.dims)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, ndims, self.sizes)
        testMincReturn(r)
        print "sizes", self.sizes[0:self.ndims]
        seps = double_sizes()
        r = libminc.miget_dimension_separations(self.dims, MI_DIMORDER_APPARENT,
                                                self.ndims, seps)
        testMincReturn(r)
        self.separations = seps[0:self.ndims]
        print "separations", self.separations
        starts = double_sizes()
        r = libminc.miget_dimension_starts(self.dims, MI_DIMORDER_APPARENT,
                                           self.ndims, starts)
        testMincReturn(r)
        self.starts = starts[0:self.ndims]
        print "starts", self.starts
        
        
        self.dataLoadable = True
    def copyDimensions(self, otherInstance):
        """create new local dimensions info copied from another instance"""
        self.ndims = c_int(otherInstance.ndims)
        self.starts = otherInstance.starts
        self.separations = otherInstance.separations
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
    def createVolumeHandle(self, volumeType="ubyte"):
        """creates a new volume on disk"""
        self.volPointer = mihandle()
        self.volumeType = volumeType
        r = libminc.micreate_volume(self.filename, self.ndims, self.dims, 
                                    mincSizes[volumeType]["minc"], MI_CLASS_REAL,
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

