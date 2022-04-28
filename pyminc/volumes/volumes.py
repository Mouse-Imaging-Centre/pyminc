from ctypes import (byref,
                    c_double, c_int,
                    c_char_p, c_void_p,
                    POINTER, create_string_buffer)
from .libpyminc2 import (c_stringy,
                         direction_cosines_array, GeneralTransform, libminc,
                         mibool,
                         mihandle,
                         misize_t, misize_t_sizes, mincSizes,
                         mitype_t, MI_TYPE_STRING,
                         MI_DIMATTR_ALL, MI_DIMCLASS_ANY,
                         MI_DIMORDER_APPARENT,
                         voxel_coord, world_coord, MI_CLASS_REAL, MI2_OPEN_RDWR, MI2_OPEN_READ, MI_DIMCLASS_SPATIAL,
                         MI_DIMCLASS_RECORD, MI_DIMATTR_REGULARLY_SAMPLED, int_sizes, MI_ROOT_PATH_FOR_IMAGE_ATTR,
                         dimensions, double_sizes, encoding, c_py3_unicode_p)
from .hyperslab import HyperSlab
import operator
import os
import sys
import datetime as datetime
from functools import reduce
import subprocess
import numpy as numpy


class mincException(Exception): pass
class NoDataException(Exception): pass
class IncorrectDimsException(Exception): pass
class NoDataTypeException(Exception): pass
class mincTypeNotDetermined(Exception): pass
class volumeTypeNotDetermined(Exception): pass
class directionCosinesNotDetermined(Exception): pass


def testMincReturn(value):
    if value < 0:
        raise mincException


def getDtype(data):
    """get the mincSizes datatype based on a numpy array"""
    dtype = None
    for m_type in mincSizes:
        if mincSizes[m_type]["numpy"] == data.dtype:
            dtype = m_type
            break
    return dtype


def transform_multiple_xyz_coordinates_using_xfm(xfm_filename, x_coor, y_coor, z_coor, use_inverse=False):
    # make sure we have the same number of input coordinates for x y and z
    if len(x_coor) != len(y_coor) or len(y_coor) != len(z_coor):
        raise ValueError("The function transform_multiple_xyz_coordinates_using_xfm was provided with incorrect coordinate data. The length of the lists differ.")

    # read the transformation file
    handle_for_transform = GeneralTransform()
    r = libminc.input_transform_file(xfm_filename, handle_for_transform)
    testMincReturn(r)

    # return arrays
    ret_x = []
    ret_y = []
    ret_z = []

    # holders for the transformed coordinates
    new_x = c_double()
    new_y = c_double()
    new_z = c_double()

    for i in range(len(x_coor)):
        if use_inverse:
            r = libminc.general_inverse_transform_point(handle_for_transform,
                                                        c_double(x_coor[i]), c_double(y_coor[i]), c_double(z_coor[i]),
                                                        byref(new_x), byref(new_y), byref(new_z))
        else:
            r = libminc.general_transform_point(handle_for_transform,
                                                c_double(x_coor[i]), c_double(y_coor[i]), c_double(z_coor[i]),
                                                byref(new_x), byref(new_y), byref(new_z))
        testMincReturn(r)
        ret_x += [new_x.value]
        ret_y += [new_y.value]
        ret_z += [new_z.value]

    # free up memory
    libminc.delete_general_transform(handle_for_transform)
    # return transformed values
    return (ret_x, ret_y, ret_z)


def transform_xyz_coordinates_using_xfm(xfm_filename, x_coor, y_coor, z_coor, use_inverse=False):
    ret_x_array, rey_y_array, rey_z_array = transform_multiple_xyz_coordinates_using_xfm(xfm_filename,
                                                                                         [x_coor],
                                                                                         [y_coor],
                                                                                         [z_coor],
                                                                                         use_inverse=use_inverse)
    return ret_x_array[0], rey_y_array[0], rey_z_array[0]


class mincVolume(object):
    def __init__(self, filename=None, dtype=None, readonly=True, labels=False):
        self.volPointer = mihandle() # holds the pointer to the mihandle
        self.dims = dimensions()     # holds the actual pointers to dimensions
        self.ndims = 0               # number of dimensions in this volume
        self.ndims_misize_t = 0      # same number, but in different format
        self.sizes = int_sizes()     # holds dimension sizes info
        self.dataLoadable = False    # we know enough about the file on disk to load data
        self.dataLoaded = False      # data sits inside the .data attribute
        self.dtype = dtype           # numpy data type for array representation (in Python) can either be a string (str) or of type numpy.dtype
        self.volumeType = None       # data type on file, will be determined by openFile()
        self.filename = filename     # the filename associated with this volume
        self.readonly = readonly     # flag indicating that volume is for reading only
        self.labels = labels         # whether it contains labels - affects how ranges are set
        self.history = create_string_buffer(b"") # string holding the history information of the file (type = ctypes array of c_char)
        self.historyupdated = False  # does the history contain information about what pyminc has done?
        self.order = "C"
        self.debug = "PYMINCDEBUG" in os.environ
        self._x_direction_cosines = None
        self._y_direction_cosines = None
        self._z_direction_cosines = None
        self._data_written_to_file = False


    def numpy_type_to_string(self, dtype_in_numpy_form):
        # if the dtype is not found, return "unknown"
        return {
            numpy.int8    : "byte",
            numpy.int16   : "short",
            numpy.int32   : "int",
            numpy.float32 : "float",
            numpy.float64 : "double",
            numpy.uint8   : "ubyte",
            numpy.uint16  : "ushort",
            numpy.uint32  : "uint",
            "int8"    : "byte",
            "int16"   : "short",
            "int32"   : "int",
            "float32" : "float",
            "float64" : "double",
            "uint8"   : "ubyte",
            "uint16"  : "ushort",
            "uint32"  : "uint",
            numpy.dtype("int8")    : "byte",
            numpy.dtype("int16")   : "short",
            numpy.dtype("int32")   : "int",
            numpy.dtype("float32") : "float",
            numpy.dtype("float64") : "double",
            numpy.dtype("uint8")   : "ubyte",
            numpy.dtype("uint16")  : "ushort",
            numpy.dtype("uint32")  : "uint",
            }.get(dtype_in_numpy_form, "unknown")

    def get_numpy_dtype(self):
        return {
            numpy.int8    : numpy.int8,
            numpy.int16   : numpy.int16,
            numpy.int32   : numpy.int32,
            numpy.float32 : numpy.float32,
            numpy.float64 : numpy.float64,
            numpy.uint8   : numpy.uint8,
            numpy.uint16  : numpy.uint16,
            numpy.uint32  : numpy.uint32,
            "int8"    : numpy.int8,
            "byte"    : numpy.int8,
            "int16"   : numpy.int16,
            "short"   : numpy.int16,
            "int32"   : numpy.int32,
            "int"     : numpy.int32,
            "float32" : numpy.float32,
            "float"   : numpy.float32,
            "float64" : numpy.float64,
            "double"  : numpy.float64,
            "uint8"   : numpy.uint8,
            "ubyte"   : numpy.uint8,
            "uint16"  : numpy.uint16,
            "ushort"  : numpy.uint16,
            "uint32"  : numpy.uint32,
            "uint"    : numpy.uint32,
            numpy.dtype("int8")    : numpy.int8,
            numpy.dtype("int16")   : numpy.int16,
            numpy.dtype("int32")   : numpy.int32,
            numpy.dtype("float32") : numpy.float32,
            numpy.dtype("float64") : numpy.float64,
            numpy.dtype("uint8")   : numpy.uint8,
            numpy.dtype("uint16")  : numpy.uint16,
            numpy.dtype("uint32")  : numpy.uint32,
            }.get(self.dtype, "unknown")

    def get_string_form_of_numpy_dtype(self, dtype_in_numpy_form):
        """convert the variable of type numpy.dtype in the string (str) equivalent"""
        if type(dtype_in_numpy_form) == str:
            if self.debug:
                print("dtype provided to get_string_form_of_numpy_dtype was already in string format: " + dtype_in_numpy_form)
            # it's already fine:
            return dtype_in_numpy_form
        string_form = self.numpy_type_to_string(dtype_in_numpy_form)
        if string_form == "unknown":
                sys.stderr.write("Could not convert numpy.dtype: " + str(dtype_in_numpy_form) + " to the equivalent minc format...")
                raise NoDataException
        return string_form

    def getdata(self):
        """called when data attribute requested"""
        #print("getting data")
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
            print("setting data")
        if newdata.shape != tuple(self.sizes[0:self.ndims]):
            if self.debug:
                print("Shapes: " + str(newdata.shape) + " " + str(self.sizes[0:self.ndims]))
            raise IncorrectDimsException
        else:
            # make sure we don't change the data type of the data
            # we also need to provide the dtype here in a format
            # that won't confuse numpy. If you supply "float" to
            # astype(), it'll default to "float64" which we actually
            # consider to be "double".
            self._data = newdata.astype(self.get_numpy_dtype())
            self.dataLoaded = True
            if self.debug:
                print("New Shape: " + str(self.data.shape))

    def loadData(self):
        """loads the data from file into the data attribute"""
        if self.debug:
            print("size: "  + str(self.sizes[:]))
        if self.dataLoadable:
            self._data = self.getHyperslab(int_sizes(), self.sizes[0:self.ndims],
                                           self.dtype)
            self._data.shape = self.sizes[0:self.ndims]
            self.dataLoaded = True
        elif self.ndims > 0:
            length = reduce(operator.mul, self.sizes[0:self.ndims])
            self._data = numpy.zeros(length, order=self.order, dtype=self.dtype)
            self._data.shape = self.sizes[0:self.ndims]
        else:
            raise NoDataException

    def getHyperslab(self, start, count, dtype=None):
        """
        given starts and counts returns the corresponding array.  This is read
        either from memory or disk depending on the state of the dataLoaded variable.
        """

        dtype_to_get = dtype or self.dtype
        if not dtype_to_get:
            sys.stderr.write("dtype unknown in getHyperslab...")
            raise NoDataTypeException
        if self.dataLoadable == False:
            raise NoDataException
        if self.debug:
            print("We are loading the data from this file using dtype: " + str(dtype_to_get))

        # dtype_to_get can be provided either as a string, or as a variable of type
        # numpy.dtype. In the latter case, we should convert it here to the string form
        if type(dtype_to_get) == numpy.dtype:
            dtype_to_get = self.get_string_form_of_numpy_dtype(dtype_to_get)

        start = numpy.array(start[:self.ndims])
        count = numpy.array(count[:self.ndims])
        size = reduce(operator.mul, count)
        if self.debug:
            print(start[:], count[:], size)
        a = HyperSlab(numpy.zeros(count, dtype=mincSizes[dtype_to_get]["numpy"], order=self.order),
                      start=start, count=count, separations=self.separations)

        if self.dataLoaded:
            slices = tuple(map(lambda x, y: slice(x, x+y), start, count))
            if dtype_to_get == "float" or dtype_to_get == "double":
                a[...] = self.data[slices]
            else:
                raise RuntimeError("get hyperslab for integer datatypes not yet implemented"
                                   " when volume is already loaded into memory")
        else:  # if data not already loaded
            ctype_start = misize_t_sizes(*start)
            ctype_count = misize_t_sizes(*count)
            if self.debug:
                print(start[:], count[:], size)
            r = 0
            if dtype_to_get == "float" or dtype_to_get == "double":
                # return real values if datatpye is floating point
                r = libminc.miget_real_value_hyperslab(
                    self.volPointer,
                    mincSizes[dtype_to_get]["minc"],
                    ctype_start, ctype_count,
                    a.ctypes.data_as(POINTER(mincSizes[dtype_to_get]["ctype"])))
            else :
                # return normalized values if datatype is integer
                r = libminc.miget_hyperslab_normalized(
                    self.volPointer,
                    mincSizes[dtype_to_get]["minc"],
                    ctype_start, ctype_count,
                    c_double(mincSizes[dtype_to_get]["min"]),
                    c_double(mincSizes[dtype_to_get]["max"]),
                    a.ctypes.data_as(POINTER(mincSizes[dtype_to_get]["ctype"])))
            testMincReturn(r)
        return a

    def setHyperslab(self, data, start=None, count=None):
        """write hyperslab back to file"""

        if self.readonly:
            raise IOError("Writing to file %s which has been opened in readonly mode" % self.filename)
        if not self.dataLoadable:
            self.createVolumeImage()
        if count is None:
            count = data.count
        if start is None:
            start = data.start

        if self.dataLoaded:
            slices = list(map(lambda x, y: slice(x, x+y), start, count))
            self.data[slices] = data
        else: # if data is not in memory write hyperslab to disk
            ctype_start = misize_t_sizes(*start[:self.ndims])
            ctype_count = misize_t_sizes(*count[:self.ndims])
            # find the datatype map index
            dtype = getDtype(data)
            self.setVolumeRanges(data)
            if self.debug:
                print("before setting of hyperslab")
            arr = data if data.flags['C_CONTIGUOUS'] else data.copy()
            if dtype == "float" or dtype == "double":
                r = libminc.miset_real_value_hyperslab(
                        self.volPointer, mincSizes[dtype]["minc"],
                        ctype_start, ctype_count,
                        arr.ctypes.data_as(POINTER(mincSizes[dtype]["ctype"])))
                testMincReturn(r)
            else:
                raise NotImplementedError("setting hyperslab with types other than float or double not yet supported")
            self._data_written_to_file = True
            if self.debug:
                print("after setting of hyperslab")

    def writeFile(self):
        """write the current data array to file"""
        if self.readonly:
            raise IOError("Writing to file %s which has been opened in readonly mode" % self.filename)
        if not self.historyupdated:
            addToHist = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " >>> (default history added after pyminc usage) " + " ".join(sys.argv) + "\n"
            self.appendAndWriteHistory(history=addToHist)
        if not self.dataLoadable:  # if file doesn't yet exist on disk
            self.createVolumeImage()
        if self.dataLoaded:  # only write if data is in memory
            # find the datatype map index. If self.dtype is of type numpy.dtype
            # (not self.dtype) will return True...
            if (not type(self.dtype == numpy.dtype) and
               self.dtype == None) :
                sys.stderr.write("dtype unknown in writeFile...")
                raise NoDataTypeException
            self.setVolumeRanges(self._data)

            if type(self.dtype) != str:
                self.dtype = self.get_string_form_of_numpy_dtype(self.dtype)

            arr = self._data if self._data.flags["C_CONTIGUOUS"] else self._data.copy()

            r = libminc.miset_real_value_hyperslab(
                self.volPointer, mincSizes[self.dtype]["minc"],
                misize_t_sizes(), misize_t_sizes(*self.sizes[:]),
                arr.ctypes.data_as(POINTER(mincSizes[self.dtype]["ctype"])))
            testMincReturn(r)
            self._data_written_to_file = True

            # set the complete flag of the volume. Depending on which version
            # of libminc is being used, we can call miset_attr_values() (which
            # is the correct function to use) or miset_attribute() (which is 
            # a private function and should not be used). 
            # 
            # However, until the fix made on June 17, 2016:
            # https://github.com/BIC-MNI/libminc/commit/3ca34259f7d5bdae11bf77226492457cb7a1922a 
            # it is not possible to set the image:complete flag using miset_attr_values.
            # 
            # Right now we don't know yet which version of libminc has the fix, so
            # the version check will always fail. We should update this when the 
            # fix has made it into a new release of libminc.
            # 
            miget_version = libminc.miget_version
            miget_version.restype = c_char_p
            libminc_version = miget_version().decode()
            libminc_version_major = int(libminc_version.split('.')[0])
            libminc_version_minor = int(libminc_version.split('.')[1])
            libminc_version_patch = int(libminc_version.split('.')[2])
            # this "correct" version 3.5.99 is fictive, and to be determined.
            if (libminc_version_major >= 2 and
                libminc_version_minor >= 4 and
                libminc_version_patch >= 3):
                r = libminc.miset_attr_values(self.volPointer,
                                              MI_TYPE_STRING,
                                              c_stringy("image"),
                                              c_stringy("complete"),
                                              5,
                                              c_stringy("true_"))
                testMincReturn(r)
            else:
                try:
                    r = libminc.miset_attribute(self.volPointer,
                                                MI_ROOT_PATH_FOR_IMAGE_ATTR,
                                                c_stringy("complete"),
                                                MI_TYPE_STRING,
                                                5,
                                                c_stringy("true_"))
                    testMincReturn(r)
                except mincException:
                    print("Warning/Info: could not set the image:complete flag for file: " + self.filename +
                          " even though the file was written out successfully. Perhaps you need to update"
                          " your libminc libraries.")
            # also close the volume, that way it can be used directly after
            self.closeVolume()



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
        if(self.volumeType == "float" or self.volumeType == "double"):
            # there is no defined minimum or maximum to the float/double range
            # in this case, the volume and voxel range should be the same
            vmax = max
            vmin = min
        else:
            # for all other data types, set min and max to those associated
            # with the data type
            vmax = mincSizes[self.volumeType]["max"]
            vmin = mincSizes[self.volumeType]["min"]
        # if this is a label volume then make vmax and vmin be the same as max and min
        # note - in the future this should use the minc2 label types, but since no tool supports them yet ...
        if self.labels:
            if max > vmax or min < vmin:
                raise ValueError("label volume found where max or min label exceeds max or min of volume type")
            vmax = max
            vmin = min
        r = libminc.miset_volume_range(self.volPointer, max, min)
        testMincReturn(r)
        r = libminc.miset_volume_valid_range(self.volPointer, vmax, vmin)
        testMincReturn(r)

    def setVolumeRange(self, volume_max, volume_min):
        """This method sets the range (min and max) scale value for the volume. Note that this method only works if volume is not slice scaled."""
        status = libminc.miset_volume_range(self.volPointer,
                                            volume_max, volume_min)
        testMincReturn(status)

    def getVolumeRange(self):
        """
        This method gets the range (min and max) scale value for the volume.
        """
        if self.isSliceScaled:
            if self.debug:
                print("Slice scaling is enabled, will determine the range based on the data loaded")
            if not self.dataLoaded:
                self.loadData()
            return float(self.data.min()), float(self.data.max())
        else:
            volume_max, volume_min = c_double(), c_double()
            status = libminc.miget_volume_range(self.volPointer,
                                                byref(volume_max),
                                                byref(volume_min))
            testMincReturn(status)
            return volume_min.value, volume_max.value

    def isSliceScaled(self):
        "return slice_scaling_flag for volume"
        scaling_flag = mibool()
        status = libminc.miget_slice_scaling_flag(self.volPointer,
                                                  byref(scaling_flag))
        testMincReturn(status)
        return scaling_flag.value


    def setValidRange(self, valid_max, valid_min):
        """This method sets the valid range (min and max) for the datatype."""
        status = libminc.miset_volume_valid_range(self.volPointer,
                                                  valid_max, valid_min)
        testMincReturn(status)

    def getValidRange(self):
        """This method sets the valid range for the volume datatype"""
        valid_max, valid_min = c_double(), c_double()
        status = libminc.miget_volume_valid_range(self.volPointer,
                                                  byref(valid_max), byref(valid_min))
        testMincReturn(status)
        return valid_max.value, valid_min.value

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

    def getMincSizesFromMincType(self, minc_type):
        """
        minc_type -- c_int

        traverses mincSizes and determines the
        human readable name for the data type (e.g. byte, ushort,...)
        """
        found_type = None
        for mS_type in mincSizes:
            if mincSizes[mS_type]["minc"] == minc_type.value:
                found_type = mS_type
                break
        if not found_type:
            sys.stderr.write(f"The data type '{minc_type.value}' of the MINC file is not supported by pyminc yet. "
                             "Please submit an issue on GitHub: https://github.com/Mouse-Imaging-Centre/pyminc/issues "
                             "Value of the MINC type that is not supported: ")
            raise mincTypeNotDetermined
        return found_type

    def get_direction_cosines(self, dim_name):
        direction_cosines = direction_cosines_array()
        for i in range(len(self.dimnames)):
            if self.dimnames[i] == dim_name:
                r = libminc.miget_dimension_cosines(self.dims[i],
                                                    direction_cosines)
                testMincReturn(r)
                if self.debug:
                    print("Direction cosines for dimension: " + str(dim_name) + ": " + str(direction_cosines[:]))
                return direction_cosines
        # if we get to this point, we were not able to extract the direction cosines:
        sys.stderr.write("Could not retrieve direction cosines for dimension: " + dim_name)
        raise directionCosinesNotDetermined


    def openFile(self):
        """reads information from MINC file"""
        r = libminc.miopen_volume(self.filename, (MI2_OPEN_RDWR, MI2_OPEN_READ)[self.readonly],
                                  self.volPointer)
        testMincReturn(r)
        # get information about the data type of the input file
        file_datatype = mitype_t()
        r = libminc.miget_data_type(self.volPointer, file_datatype)
        testMincReturn(r)
        self.volumeType = self.getMincSizesFromMincType(file_datatype)
        if self.debug:
            print("Datatype of the input file: " + str(self.volumeType))
        # if the dtype was not explicitly set, set it to double in order
        # not to lose any precision while working with the data
        # unless we are reading in labels (a segmentation) file. In
        # which case we should read that in as ushort (i.e. integers)
        if not self.dtype and not self.labels:
            self.dtype = "double"
        if self.labels and self.dtype not in ["ubyte", "ushort", "uint"]:
            # the dtype should reflect integers of some sort. This
            # should also be unsigned, because negative label values
            # don't make sense
            if not self.volumeType in ["ubyte", "ushort", "uint"]:
                # set it to be the largest possible:
                self.dtype = "uint"
                if self.debug:
                    print("Changed the dtype of the data being to be uint to reflect label/segmentation data.")
            else:
                self.dtype = self.volumeType
                if self.debug:
                    print("Changed the dtype of the data being to be " + str(self.dtype) + " to reflect label/segmentation data.")

        if self.debug:
            print("Datatype of the numpy array: " + str(self.dtype))
        ndims = c_int(0)
        libminc.miget_volume_dimension_count(self.volPointer,
                                             MI_DIMCLASS_ANY,
                                             MI_DIMATTR_ALL,
                                             ndims)
        self.ndims = ndims.value
        self.ndims_misize_t = misize_t(ndims.value)
        r = libminc.miget_volume_dimensions(
            self.volPointer, MI_DIMCLASS_ANY,
            MI_DIMATTR_ALL, MI_DIMORDER_APPARENT,
            ndims, self.dims)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, self.ndims_misize_t, self.sizes)
        testMincReturn(r)
        if self.debug:
            print("sizes: " + str(self.sizes[0:self.ndims]))
        seps = double_sizes()
        r = libminc.miget_dimension_separations(self.dims, MI_DIMORDER_APPARENT,
                                                self.ndims_misize_t, seps)
        testMincReturn(r)
        self.separations = seps[0:self.ndims]
        if self.debug:
            print("separations: " + str(self.separations))
        starts = double_sizes()
        r = libminc.miget_dimension_starts(self.dims, MI_DIMORDER_APPARENT,
                                           self.ndims_misize_t, starts)
        testMincReturn(r)
        self.starts = starts[0:self.ndims]
        if self.debug:
            print("starts: " + str(self.starts))
        self.dimnames = []
        for i in range(self.ndims):
            name = c_stringy("")
            r = libminc.miget_dimension_name(self.dims[i], name)
            self.dimnames.append(name.value.decode(encoding))  # FIXME # TODO: mifree_name(name)
        if self.debug:
            print("dimnames: " + str(self.dimnames))
        try:
            self.history = self.getHistory(size=999999)  # FIXME ...
        except mincException:
            # some programs do not properly initialize the minc history attribute
            # (for example RMINC (july 2014)). Running getHistory() on one of those files will
            # generate a mincException. However, we can ignore that and simply
            # leave the current history of the input file initialized at ""
            if self.debug:
                print("MINC file does not have a history attribute, creating one")
        #
        # Direction cosines
        #
        self._x_direction_cosines = self.get_direction_cosines('xspace')
        self._y_direction_cosines = self.get_direction_cosines('yspace')
        self._z_direction_cosines = self.get_direction_cosines('zspace')

        self.dataLoadable = True

    def copyDimensions(self, otherInstance, dims=None):
        """create new local dimensions info copied from another instance"""
        if not dims:
            dims = otherInstance.dimnames
        self.ndims = c_int(len(dims))
        self.starts = list(range(self.ndims.value))
        self.separations = list(range(self.ndims.value))
        self.dimnames = list(range(self.ndims.value))
        tmpdims = list(range(self.ndims.value))
        j=0
        for i in range(otherInstance.ndims):
            if otherInstance.dimnames[i] in dims:
                tmpdims[j] = c_void_p(0)
                self.starts[j] = otherInstance.starts[i]
                self.separations[j] = otherInstance.separations[i]
                self.dimnames[j] = otherInstance.dimnames[i]
                r = libminc.micopy_dimension(otherInstance.dims[i], tmpdims[j])
                if self.debug:
                    print("Return from micopy_dimension: " + str(r) + " " +
                          str(otherInstance.dims[i]) + " " + str(tmpdims[j]) +
                          " " + str(self.dimnames[j]))
                testMincReturn(r)
                j = j+1
        self._x_direction_cosines = list(range(3))
        self._y_direction_cosines = list(range(3))
        self._z_direction_cosines = list(range(3))
        for i in range(3):
            self._x_direction_cosines[i] = otherInstance._x_direction_cosines[i]
            self._y_direction_cosines[i] = otherInstance._y_direction_cosines[i]
            self._z_direction_cosines[i] = otherInstance._z_direction_cosines[i]
        self.dims = dimensions(*tmpdims[0:self.ndims.value])
        self.ndims = self.ndims.value

    def setVolumeType(self, volumeType):
        """set the volumeType"""
        if not volumeType:
            sys.stderr.write("volumeType passed along to setVolumeType is None. "
                             "Should be set to a proper volumeType (e.g., short, float, ubyte...)")
            raise volumeTypeNotDetermined
        self.volumeType = volumeType

    def copyDtype(self, otherInstance):
        """copy the datatype to use for this instance from another instance"""
        self.dtype = otherInstance.dtype

    def copyHistory(self, otherInstance):
        """copy the history information to use for this instance from another instance"""
        self.history = otherInstance.history

    def createVolumeHandle(self, volumeType=None):
        """creates a new volume on disk"""
        self.volPointer = mihandle()
        if not volumeType and not self.volumeType:
            sys.stderr.write("volumeType passed along to createVolumeHandle is None "
                             "and the volumeType is not set in the object yet...")
            raise volumeTypeNotDetermined
        if volumeType:
            self.volumeType = volumeType
        if self.debug:
            print("Number of dimensions: " + str(self.ndims) + " " + str(self.dims[0:self.ndims]))
        r = libminc.micreate_volume(self.filename, self.ndims, self.dims,
                                    mincSizes[volumeType]["minc"], MI_CLASS_REAL,
                                    None, self.volPointer)
        testMincReturn(r)
        r = libminc.miget_dimension_sizes(self.dims, self.ndims, self.sizes)
        if self.debug:
            print("sizes: " + str(self.sizes[0:self.ndims]))
        testMincReturn(r)

    def createVolumeImage(self):
        """creates the volume image on disk"""
        r = libminc.micreate_volume_image(self.volPointer)
        testMincReturn(r)
        self.dataLoadable = True

    def createNewDimensions(self, dimnames, sizes, starts, steps,
                            x_dir_cosines, y_dir_cosines, z_dir_cosines):
        """creates new dimensions for a new volume"""
        self.ndims = len(dimnames)
        tmpdims = list(range(self.ndims))
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
                if dimnames[i] == "xspace":
                    r = libminc.miset_dimension_cosines(tmpdims[i], direction_cosines_array(x_dir_cosines[0],
                                                                                            x_dir_cosines[1],
                                                                                            x_dir_cosines[2]))
                    testMincReturn(r)
                if dimnames[i] == "yspace":
                    r = libminc.miset_dimension_cosines(tmpdims[i], direction_cosines_array(y_dir_cosines[0],
                                                                                            y_dir_cosines[1],
                                                                                            y_dir_cosines[2]))
                    testMincReturn(r)
                if dimnames[i] == "zspace":
                    r = libminc.miset_dimension_cosines(tmpdims[i], direction_cosines_array(z_dir_cosines[0],
                                                                                            z_dir_cosines[1],
                                                                                            z_dir_cosines[2]))
                    testMincReturn(r)
        self.dims = dimensions(*tmpdims[0:self.ndims])
        self.separations = steps
        self._x_direction_cosines = x_dir_cosines
        self._y_direction_cosines = y_dir_cosines
        self._z_direction_cosines = z_dir_cosines

    def closeVolume(self):
        """remove the file created on disk if we didn't actually write it out"""
        if (not self.readonly) and (not self._data_written_to_file):
            # the data was never written to file, delete 
            # the file that was created, because it won't be usable
            if self.debug:
                print("Removing file " + str(self.filename) + " created on disk, because data was not written out")
            subprocess.check_call(("rm -f %s" % self.filename).split())
        """close volume and release all pointer memory"""
        if self.volPointer is not None:  # avoid freeing memory twice
            # in the current version of miclose_volume, the dimension
            # handles are all freed as well
            # Also, since `closeVolume` is invoked by `__del__`,
            # the following line may cause a warning at program exit
            # due to Python's strange finalization behaviour.  We could
            # test for `libminc` being None ...
            r = libminc.miclose_volume(self.volPointer)
            testMincReturn(r)
            self.volPointer = None
        for i in range(self.ndims):
            if self.dims[i] is not None:
                 # dimension was freed by previous call of miclose_volume
                 self.dims[i] = None
        self.dataLoadable = False

    def __getitem__(self, i):
        return self.data[i]

    def __del__(self):
        "close file and release memory from libminc"
        self.closeVolume()

    # define access functions for getting and setting the data attribute
    data = property(getdata, setdata, None, doc="The voxel data of the volume")

    #adding history to minc files, history should be a string
    def appendAndWriteHistory(self, history):
        if self.debug:
            print("adding to history :" + str(history))
        fullHistory = self.history.value + history.encode(encoding)
        self.history = create_string_buffer(fullHistory)
        r = libminc.miadd_history_attr(self.volPointer, len(self.history), self.history)
        testMincReturn(r)
        self.historyupdated = True

    #retrieve history of file 
    def getHistory(self, size, history=None):
        history = create_string_buffer(size)
        r = libminc.miget_attr_values(self.volPointer, MI_TYPE_STRING, "", "history", len(history), history)
        testMincReturn(r)
        # add a new line to the history to ensure that this command is seen as a new
        # command in the MINC history (i.e., is not simply concatenated into a big
        # long string)
        history.value = history.value + b"\n"
        return history

    # set apparent dimension orders
    def setApparentDimensionOrder(self, name, size=None):
        array_type = c_py3_unicode_p * size
        names = array_type()
        for i in range(size):
            if len(name.split(',')[i]) == 1:
                names[i] = name.split(',')[i] + 'space'
            else:
                names[i] = name.split(',')[i]
        r = libminc.miset_apparent_dimension_order_by_name(self.volPointer, size, names)
        testMincReturn(r)
    # copy attributes from path
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
        return numpy.array(c_world[:])


#Jason's version of convertVoxelToWorld:
#
#    def convertVoxelToWorld(self, coordinates):
#        #takes a list of voxel coordinates and returns its world coords
#        wc = double_sizes()
#        vc = double_sizes()
#        vc[0:self.ndims] = coordinates[0:self.ndims]
#        libminc.miconvert_voxel_to_world(self.volPointer, vc, wc)
#        return(wc[0:self.ndims])


    def convertWorldToVoxel(self, world):
        """Convert world location to corresponding point in voxel coordinates. 
        
        world  : float array of length 3
        """
        c_voxel = voxel_coord()
        c_world = world_coord()
        c_world[:] = world
        status = libminc.miconvert_world_to_voxel(self.volPointer, c_world, c_voxel)
        testMincReturn(status)
        return numpy.array(c_voxel[:self.ndims])



# Jason's version of convertWorldToVoxel:
#
#    def convertWorldToVoxel(self, coordinates):
#        #takes a list of world coordinates and returns its voxel coords
#        #wc = double_sizes()
#        #vc = double_sizes()
#        #wc[0:self.ndims] = coordinates[0:self.ndims]
#        #libminc.miconvert_world_to_voxel(self.volPointer, wc, vc)
#        #return(vc[0:self.ndims])


