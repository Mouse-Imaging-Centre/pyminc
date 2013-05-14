from libpyminc2 import *
from hyperslab import HyperSlab
import operator
import os

class mincException(Exception): pass
class NoDataException(Exception): pass
class IncorrectDimsException(Exception): pass

def testMincReturn(value):
    if value < 0:
        raise mincException

class mincVolume(object):
    def __init__(self, filename=None, dtype="float", readonly=True):
        self.volPointer = mihandle() # holds the pointer to the mihandle
        self.dims = dimensions()     # holds the actual pointers to dimensions
        self.ndims = 0               # number of dimensions in this volume
        self.sizes = int_sizes()     # holds dimension sizes info
        self.dataLoadable = False    # we know enough about the file on disk to load data
        self.dataLoaded = False      # data sits inside the .data attribute
        self.dtype = dtype           # default datatype for array representation
        self.filename = filename     # the filename associated with this volume
        self.readonly = readonly     # flag indicating that volume is for reading only
        self.order = "C"
        self.debug = os.environ.has_key("PYMINCDEBUG")

    def getDtype(self, data):
        """get the mincSizes datatype based on a numpy array"""
        dtype = None
        for type in mincSizes:
            if self.debug:
                print "TYPE:", type, data.dtype
            if mincSizes[type]["numpy"] == data.dtype:
                dtype = type
                break
        return dtype

    def getdata(self):
        """called when data attribute requested"""
        #print "getting data"
        if self.ndims > 0:
            if not self.dataLoaded:
                self.loadData()
                self.dataLoaded = True
            return self._data
        else:
            raise NoDataException

    def setdata(self, newdata):
        """sets the data attribute"""
        if self.debug:
            print "setting data"
        if newdata.shape != tuple(self.sizes[0:self.ndims]):
            if self.debug:
                print "Shapes", newdata.shape, self.sizes[0:self.ndims]
            raise IncorrectDimsException
        #elif self.dataLoadable == False:
        #    raise NoDataException
        else:
            self._data = newdata
            self.dataLoaded = True
            if self.debug:
                print "New Shape:", self.data.shape

    def loadData(self):
        """loads the data from file into the data attribute"""
        if self.debug:
            print "size", self.sizes[:]
        if self.dataLoadable:
            self._data = self.getHyperslab(int_sizes(), self.sizes[0:self.ndims], 
                                           self.dtype)
            self.dataLoaded = True
            self.dtype = dtype
        elif self.ndims > 0:
            self._data = zeros(self.sizes[0:self.ndims], order=self.order)
        else: 
            raise NoDataException

    def getHyperslab(self, start, count, dtype="float"):
        """given starts and counts returns the corresponding array.  This is read either from memory or disk depending on the state of the dataLoaded variable."""

        if self.dataLoadable == False:
            raise NoDataException

        start = array(start[:self.ndims])
        count = array(count[:self.ndims])

        a = HyperSlab(zeros(count, dtype=mincSizes[dtype]["numpy"], order=self.order), 
                      start=start, count=count, separations=self.separations) 

        if self.dataLoaded:
            slices = map(lambda x, y: slice(x, x+y), start, count)
            if dtype == "float" or dtype == "double":
                a[...] = self.data[slices]
            else:
                raise RuntimeError, "get hyperslab for integer datatypes not yet implements"+\
                    " when volume is already loaded into memory"
        else:  # if data not already loaded
            ctype_start = long_sizes(*start)
            ctype_count = long_sizes(*count)
            if self.debug:
                print start[:], count[:], size
            r = 0
            if dtype == "float" or dtype == "double":
                # return real values if datatpye is floating point
                r = libminc.miget_real_value_hyperslab(
                    self.volPointer, 
                    mincSizes[dtype]["minc"],
                    ctype_start, ctype_count, 
                    a.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
            else :
                # return normalized values if datatype is integer
                r = libminc.miget_hyperslab_normalized(
                    self.volPointer,
                    mincSizes[dtype]["minc"],
                    ctype_start, ctype_count,
                    c_double(mincSizes[dtype]["min"]),
                    c_double(mincSizes[dtype]["max"]),
                    a.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
            testMincReturn(r)
        return a

    def setHyperslab(self, data, start=None, count=None):
        """write hyperslab back to file"""

        if self.readonly:
            raise IOError, "Writing to file %s which has been opened in readonly mode" % self.filename
        if not self.dataLoadable:
            self.createVolumeImage() 
        if not count:
            count = data.count
        if not start:
            start = data.start
            
        if self.dataLoaded:
            slices = map(lambda x, y: slice(x, x+y), start, count)
            self.data[slices] = data
        else: # if data is not in memory write hyperslab to disk
            ctype_start = long_sizes(*start[:self.ndims])
            ctype_count = long_sizes(*count[:self.ndims])
            # find the datatype map index
            dtype = self.getDtype(data)
            self.setVolumeRanges(data)
            if self.debug:
                print "before setting of hyperslab"
            if dtype == "float" or dtype == "double":
                r = libminc.miset_real_value_hyperslab(
                        self.volPointer, mincSizes[dtype]["minc"],
                        ctype_start, ctype_count,
                        data.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
                testMincReturn(r)
            else:
                raise "setting hyperslab with types other than float or double not yet supported"
            if self.debug:
                print "after setting of hyperslab"

    def writeFile(self):
        """write the current data array to file"""
        if self.readonly:
            raise IOError, "Writing to file %s which has been opened in readonly mode" % self.filename
        if not self.dataLoadable:  # if file doesn't yet exist on disk
            self.createVolumeImage() 
        if self.dataLoaded:  # only write if data is in memory
            # find the datatype map index
            dtype = self.getDtype(self._data)
            self.setVolumeRanges(self._data)
            r = libminc.miset_real_value_hyperslab(
                self.volPointer, mincSizes[dtype]["minc"],
                long_sizes(), long_sizes(*self.sizes[:]),
                self._data.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
            testMincReturn(r)


    def setVolumeRanges(self, data):
        """sets volume and voxel ranges to use the maximum voxel range and the minumum necessary volume range.  This combination is makes optimal use of real valued data and integer volume types."""
        # ignore slice scaling for the moment

        count = reduce(operator.mul, data.shape)
        volumeCount = reduce(operator.mul, self.sizes[0:self.ndims])
        max, min = 0.0, 0.0
        if count == volumeCount:
            # if data encompasses entire volume, min and max is based solely on data
            max = data.max()
            min = data.min()
        else:
            # if data is only part of the volume, only update min and max if they
            # exceed the current range
            currentMin = c_double()
            currentMax = c_double()
            r = libminc.miget_volume_range(self.volPointer, currentMax, currentMin)
            if data.max() > currentMax.value:
                max = data.max()
            else:
                max = currentMax.value
            if data.min() < currentMin.value:
                min = data.min()
            else:
                min = currentMin.value
        # Note: for float volumes it would be better to set the volume 
        # and voxel range to be the same -- JGS
        vmax = mincSizes[self.volumeType]["max"]
        vmin = mincSizes[self.volumeType]["min"]
        r = libminc.miset_volume_range(self.volPointer, max, min)
        testMincReturn(r)
        r = libminc.miset_volume_valid_range(self.volPointer, vmax, vmin)
        testMincReturn(r)

    def setVolumeRange(self, volume_max, volume_min):
        """This method sets the range (min and max) scale value for the volume. Note that this method only works if volume is not slice scaled."""
        status = libminc.miset_volume_range(self.volPointer, \
                                                volume_max, volume_min)
        testMincReturn(status)

    def getVolumeRange(self):
        """This method gets the range (min and max) scale value for the volume. Note that this method only works if volume is not slice scaled."""
        volume_max, volume_min = c_double(), c_double()
        status = libminc.miget_volume_range(self.volPointer, \
                                    byref(volume_max), byref(volume_min))
        testMincReturn(status)
        return (volume_max.value, volume_min.value)

    def isSliceScaled(self):
        "return slice_scaling_flag for volume"
        scaling_flag = mibool()
        status = libminc.miget_slice_scaling_flag(self.volPointer, \
                                    byref(scaling_flag))
        testMincReturn(status)
        return scaling_flag.value
        

    def setValidRange(self, valid_max, valid_min):
        """This method sets the valid range (min and max) for the datatype."""
        status = libminc.miset_volume_valid_range(self.volPointer, \
                                                valid_max, valid_min)
        testMincReturn(status)

    def getValidRange(self):
        """This method sets the valid range for the volume datatype"""
        valid_max, valid_min = c_double(), c_double()
        status = libminc.miget_volume_valid_range(self.volPointer, \
                                    byref(valid_max), byref(valid_min))
        testMincReturn(status)
        return (valid_max.value, valid_min.value)
    
    def getSizes(self):
        "return volume sizes"
        return self.sizes[:self.ndims]

    def getSeparations(self):
        "return volume separations"
        return self.separations[:self.ndims]

    def getStarts(self):
        "return volume starts"
        return self.starts[:self.ndims]

    def getDimensionNames(self):
        "return volume dimension names"
        return self.dimnames

    def openFile(self):
        """reads information from MINC file"""
        r = libminc.miopen_volume(self.filename, (MI2_OPEN_RDWR, MI2_OPEN_READ)[self.readonly],
                                  self.volPointer)
        testMincReturn(r)
        ndims = c_int(0)
        libminc.miget_volume_dimension_count(self.volPointer,
                                             MI_DIMCLASS_ANY,
                                             MI_DIMATTR_ALL,
                                             ndims)
        self.ndims = ndims.value
        r = libminc.miget_volume_dimensions(
            self.volPointer, MI_DIMCLASS_ANY,
            MI_DIMATTR_ALL, MI_DIMORDER_APPARENT,
            ndims, self.dims)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, ndims, self.sizes)
        testMincReturn(r)
        if self.debug:
            print "sizes", self.sizes[0:self.ndims]
        seps = double_sizes()
        r = libminc.miget_dimension_separations(self.dims, MI_DIMORDER_APPARENT,
                                                self.ndims, seps)
        testMincReturn(r)
        self.separations = seps[0:self.ndims]
        if self.debug:
            print "separations", self.separations
        starts = double_sizes()
        r = libminc.miget_dimension_starts(self.dims, MI_DIMORDER_APPARENT,
                                           self.ndims, starts)
        testMincReturn(r)
        self.starts = starts[0:self.ndims]
        if self.debug:
            print "starts", self.starts
        self.dimnames = []
        for i in range(self.ndims):
            name = c_char_p("")
            r = libminc.miget_dimension_name(self.dims[i], name)
            self.dimnames.append(name.value)
        if self.debug:
            print "dimnames:", self.dimnames
        
        
        self.dataLoadable = True
    def copyDimensions(self, otherInstance, dims=None):
        """create new local dimensions info copied from another instance"""
        if not dims:
            dims = otherInstance.dimnames
        self.ndims = c_int(len(dims))
        self.starts = range(self.ndims.value)
        self.separations = range(self.ndims.value)
        self.dimnames = range(self.ndims.value)
        tmpdims = range(self.ndims.value)
        j=0
        for i in range(otherInstance.ndims):
            if otherInstance.dimnames[i] in dims:
                tmpdims[j] = c_void_p(0)
                self.starts[j] = otherInstance.starts[i]
                self.separations[j] = otherInstance.separations[i]
                self.dimnames[j] = otherInstance.dimnames[i]
                r = libminc.micopy_dimension(otherInstance.dims[i], tmpdims[j])
                if self.debug:
                    print r, otherInstance.dims[i], tmpdims[j], self.dimnames[j]
                testMincReturn(r)
                j = j+1
        self.dims = apply(dimensions, tmpdims[0:self.ndims.value])
        self.ndims = self.ndims.value
    def copyDtype(self, otherInstance):
        """copy the datatype to use for this instance from another instance"""
        self.dtype = otherInstance.dtype
    def createVolumeHandle(self, volumeType="ubyte"):
        """creates a new volume on disk"""
        self.volPointer = mihandle()
        self.volumeType = volumeType
        if self.debug:
            print self.ndims, self.dims[0:self.ndims]
        r = libminc.micreate_volume(self.filename, self.ndims, self.dims, 
                                    mincSizes[volumeType]["minc"], MI_CLASS_REAL,
                                    None, self.volPointer)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, self.ndims, self.sizes)
        if self.debug:
            print "sizes", self.sizes[0:self.ndims]
        testMincReturn(r)
    def createVolumeImage(self):
        """creates the volume image on disk"""
        r = libminc.micreate_volume_image(self.volPointer)
        testMincReturn(r)
        self.dataLoadable = True
    def createNewDimensions(self, dimnames, sizes, starts, steps):
        """creates new dimensions for a new volume"""
        self.ndims = len(dimnames)
        tmpdims = range(self.ndims)
        for i in range(self.ndims):
            tmpdims[i] = c_void_p(0)
            type = MI_DIMCLASS_SPATIAL
            if dimnames[i] == "vector_dimension":
                type = MI_DIMCLASS_RECORD
            r = libminc.micreate_dimension(dimnames[i], type, MI_DIMATTR_REGULARLY_SAMPLED,
                                           sizes[i], tmpdims[i])
            testMincReturn(r)
            if dimnames[i] != "vector_dimension":
                r = libminc.miset_dimension_separation(tmpdims[i], steps[i])
                testMincReturn(r)
                r = libminc.miset_dimension_start(tmpdims[i], starts[i])
                testMincReturn(r)
        self.dims = apply(dimensions, tmpdims[0:self.ndims])
        self.separations = steps

    def closeVolume(self):
        """close volume and release all pointer memory"""
        if self.volPointer is not None:  # avoid freeing memory twice
            r = libminc.miclose_volume(self.volPointer)
            testMincReturn(r)
            self.volPointer = None  

        for i in range(self.ndims):
            if self.dims[i] is not None:
                r = libminc.mifree_dimension_handle(self.dims[i])
                testMincReturn(r)
                self.dims[i] = None
        self.dataLoadable = False

    def __getitem__(self, i): 
        return self.data[i]

    def __del__(self):
        "close file and release memory from libminc"
        self.closeVolume()

    # define access functions for getting and setting the data attribute
    data = property(getdata,setdata,None,None)
    
    #adding history to minc files
    def addHistory(self, size=None, history=None):
        r = libminc.miadd_history_attr(self.volPointer, size, history)
        testMincReturn(r)

    #retrieve history of file 
    def getHistory(self, size, history=None):
        history = create_string_buffer(size) 
        r = libminc.miget_attr_values(self.volPointer, MI_TYPE_STRING, "", "history", len(history), history)
        testMincReturn(r)
        return history

    # set apparent dimension orders
    def setApparentDimensionOrder(self, size=None, name=[]):
        array_type = c_char_p * size
        names = array_type()
        for i in range(size):
            if (len(name.split(',')[i]) == 1):
                names[i] = name.split(',')[i] + 'space'
            else:
                names[i] = name.split(',')[i]
        r = libminc.miset_apparent_dimension_order_by_name(self.volPointer,size,names)
        testMincReturn(r)
    #copy attributes from path 
    def copyAttributes(self, otherInstance, path=None):
       	r = libminc.micopy_attr(otherInstance.volPointer, path, self.volPointer)
        testMincReturn(r)

    def convertVoxelToWorld(self, voxel):
        """Convert voxel location to corresponding point in world coordinates. 
        
        voxel  : float array of length ndims
        """
        c_voxel = voxel_coord()
        c_world = world_coord()
        c_voxel[:self.ndims] = voxel
        status = libminc.miconvert_voxel_to_world(self.volPointer, c_voxel, c_world)
        testMincReturn(status)
        return array(c_world[:])

    def convertWorldToVoxel(self, world):
        """Convert world location to corresponding point in voxel coordinates. 
        
        world  : float array of length 3
        """
        c_voxel = voxel_coord()
        c_world = world_coord()
        c_world[:] = world
        status = libminc.miconvert_world_to_voxel(self.volPointer, c_world, c_voxel)
        testMincReturn(status)
        return array(c_voxel[:self.ndims])
