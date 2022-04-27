from pyminc.volumes.volumes import (mincException, mincVolume, transform_xyz_coordinates_using_xfm, NoDataException)
from pyminc.volumes.factory import (volumeFromData,
                                    volumeFromDescription,
                                    volumeFromFile,
                                    volumeFromInstance,
                                    volumeLikeFile)

import numpy as np
import os
import subprocess
import tempfile

import pytest
from pytest import approx

from parameterized import parameterized


@pytest.fixture
def outputFilename():
    f = tempfile.NamedTemporaryFile(prefix="test-out-", suffix=".mnc", delete=False)
    yield f.name
    try:
        if os.path.exists(f.name):  # not actually needed but otherwise Pytest reports all the exceptions
            os.remove(f.name)
    except FileNotFoundError:
        # Pyminc didn't write data to this file.  This is fine.
        # (We could have separate fixtures for the case when the file should exist or not,
        # but this seems like testing in a few tests should be sufficient)
        pass


def tmp_mnc_file():
    return tempfile.NamedTemporaryFile(prefix="test-out-", suffix=".mnc", delete=False)


emptyFilename = tempfile.NamedTemporaryFile(prefix="test-empty-", suffix=".mnc").name
newFilename = tempfile.NamedTemporaryFile(prefix="test-new-volume-", suffix=".mnc").name

inputFile_byte = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_byte, '-osigned', '-obyte', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_short = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_short, '-osigned', '-oshort', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_int = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_int, '-oint', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_float = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_float, '-ofloat', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_double = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_double, '-odouble', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_ubyte = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_ubyte, '-ounsigned', '-obyte', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_ushort = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_ushort, '-ounsigned', '-oshort', '-input', '/dev/urandom', '100', '150', '125'])

inputFile_uint = tempfile.NamedTemporaryFile(prefix="test-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputFile_uint, '-ounsigned', '-oint', '-input', '/dev/urandom', '100', '150', '125'])



inputVector = tempfile.NamedTemporaryFile(prefix="test-vector-", suffix=".mnc").name
subprocess.check_call(['rawtominc', inputVector, '-input', '/dev/urandom', '3', '100', '150', '125',
                       '-dimorder', 'vector_dimension,xspace,yspace,zspace'])


input3DdirectionCosines = tempfile.NamedTemporaryFile(prefix="test-3d-direction-cosines", suffix=".mnc").name
subprocess.check_call(['rawtominc', input3DdirectionCosines, '-input', '/dev/urandom', '100', '150', '125',
                       '-xdircos',  '0.9305326623',   '0.1308213523', '0.34202943789',
                       '-ydircos', '-0.1958356912',  '0.96692346178', '0.16316734231',
                       '-zdircos', '-9.3093890238', '-0.21882376893', '0.92542348732'])

# testing for applying transformations to coordinates:
outputXfmFilename1 = tempfile.NamedTemporaryFile(prefix="test-xfm-1", suffix=".xfm").name
outputXfmFilename2 = tempfile.NamedTemporaryFile(prefix="test-xfm-2", suffix=".xfm").name
outputXfmFilename3 = tempfile.NamedTemporaryFile(prefix="test-xfm-3", suffix=".xfm").name
subprocess.check_call(["param2xfm", "-center", '2.21', '-3.765', '4.09', "-translation", '1.23', '6.4', '-7.8', "-scales", '0.2', '4.3', '-3', outputXfmFilename1])
subprocess.check_call(["param2xfm", "-center", '-23.98', '0.46', '9.5', "-translation", '0.0', '-46', '89.3', "-scales", '10', '7.33', '84', outputXfmFilename2])
subprocess.check_call(["xfmconcat", outputXfmFilename1, outputXfmFilename2, outputXfmFilename3])


input_files_and_dtypes = [("byte", inputFile_byte),
                          ("short", inputFile_short),
                          ("int", inputFile_int),
                          ("float", inputFile_float),
                          ("double", inputFile_double),
                          ("ubyte", inputFile_ubyte),
                          ("ushort", inputFile_ushort),
                          ("uint", inputFile_uint)]

dtypes = [dtype for dtype, _ in input_files_and_dtypes]
input_files = [f for _, f in input_files_and_dtypes]

data_block = np.arange(24000).reshape(20,30,40)
data_blocks = (data_block, data_block.T.copy())


def tearDownModule():
    os.remove(inputFile_byte)
    os.remove(inputFile_short)
    os.remove(inputFile_int)
    os.remove(inputFile_float)
    os.remove(inputFile_double)
    os.remove(inputFile_ubyte)
    os.remove(inputFile_ushort)
    os.remove(inputFile_uint)
    os.remove(inputVector)
    os.remove(newFilename)
    os.remove(input3DdirectionCosines)
    os.remove(outputXfmFilename1)
    os.remove(outputXfmFilename2)
    os.remove(outputXfmFilename3)

class TestFromFile:
    """test the volumeFromFile generator"""
    def testFromFileError(self):
        """attempting to load a garbage file should raise exception"""
        with pytest.raises(mincException):
             volumeFromFile("garbage.mnc")

    @parameterized.expand(input_files)
    def testDataTypeFromFileIsDouble(self, input_file):
        """ensure data is read as double by default"""
        v = volumeFromFile(input_file)
        dt = v.data.dtype
        v.closeVolume()
        assert dt == 'float64'

    @parameterized.expand([("byte", "int8"),
                           ("short", "int16"),
                           ("int", "int32"),
                           ("float", "float32"),
                           ("double", "float64"),
                           ("ubyte", "uint8"),
                           ("ushort", "uint16"),
                           ("uint", "uint32")])
    def testFromFileDataTypeSetToDtype(self, in_dtype, out_dtype):
        """ensure that datatype can be set to byte"""
        v = volumeFromFile(inputFile_short, dtype=in_dtype)
        dt = v.data.dtype
        v.closeVolume()
        assert dt == out_dtype

    @parameterized.expand(input_files)
    def testMeanFromFile(self, input_file):
        """ensure that data is read correct with a precision of 8 decimals on a call to average()"""
        v = volumeFromFile(input_file)
        a = np.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % input_file, "r")
        output = float(pipe.read())
        pipe.close()
        np.testing.assert_allclose(a, output, 8)


class TestWriteFileDataTypes:
    ############################################################################
    # volumeFromDescription
    ############################################################################
    @parameterized.expand(dtypes)
    def testWriteDataAsDtype(self, dtype):
        """ensure that a volume created by volumeFromDescription as byte is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"),
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType=dtype)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        assert vol_in_data_type == dtype

    ############################################################################
    # volumeFromInstance
    ############################################################################
    @parameterized.expand(dtypes)
    def testWriteDataAsDtype_vFI(self, dtype):
      """ensure that a volume created by volumeFromInstance as byte is written out as such"""
      with tmp_mnc_file() as f:
        outputFilename = f.name
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType=dtype)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        assert vol_in.volumeType == dtype

    ############################################################################
    # volumeLikeFile
    ############################################################################
    @parameterized.expand(input_files_and_dtypes)
    def testWriteDataAsDtype_vLF_base(self, dtype, input_file):
      """ensure that a volume created by volumeLikeFile has the same type as its input (byte)"""
      with tmp_mnc_file() as f:
        outputFilename = f.name
        v = volumeLikeFile(input_file, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        assert vol_in.volumeType == dtype

    #########################
    # changing the volumeType
    #########################
    @parameterized.expand(input_files_and_dtypes)
    def testWriteDataAsDtype_vLF(self, dtype, input_file):
      """ensure that a volume created by volumeLikeFile as byte is written out as such (input file has different volumeType)"""
      with tmp_mnc_file() as f:
        outputFilename = f.name
        v = volumeLikeFile(input_file, outputFilename, volumeType=dtype)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        assert vol_in.volumeType == dtype

    ############################################################################
    # volumeFromData
    ############################################################################
    @pytest.mark.parametrize("dtype", dtypes)
    @pytest.mark.parametrize("data_block", data_blocks)
    def testWriteDataAsDtype_vFD(self, dtype, data_block):
      """ensure that a volume created by volumeFromData as byte is written out as such"""
      with tmp_mnc_file() as f:
        outputFilename = f.name
        #data_block = np.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType=dtype)
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        assert vol_in.volumeType == dtype
    @pytest.mark.parametrize("dtype", dtypes)
    @pytest.mark.parametrize("data_block", data_blocks)
    def testWriteDataAsDtype_vFD_content(self, dtype, data_block):
      """ensure that a volume created by volumeFromData as byte writes correct data"""
      with tmp_mnc_file() as f:
        outputFilename = f.name
        #data_block = np.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType=dtype)
        v.writeFile()
        v.closeVolume()
        # retrieve mean of data written to disk:
        #pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        #output = float(pipe.read())
        #pipe.close()
        #assert output == approx(data_block.mean())
        #v_in = volumeFromFile(outputFilename)
        #self.assertAlmostEqual(data_block, v_in.data)  # fails!!!

        if dtype in ["byte", "ubyte", "short", "ushort", "int", "uint"]:
            pytest.xfail("not enough precision")

        vol_in = volumeFromFile(outputFilename)
        np.testing.assert_allclose(data_block, vol_in.data) #, rtol = 3e-6)

    #def testWriteNonContiguousArray(self):
    #    data_block = np.arange(24000).reshape(20, 30, 40).T
    #    v = volumeFromData(outputFilename, data_block,
    #                       dimnames=("xspace", "yspace", "zspace"),
    #                       starts = (0, 0, 0), steps = (0.04, 0.04, 0.04), volumeType="float")
    #    v.writeFile()
    #    vol_in = volumeFromFile(outputFilename)
    #    np.testing.assert_allclose(data_block, vol_in.data)

    ############################################################################
    # using volumeFromData specifying the dtype from a numpy array
    ############################################################################
    def testWriteDataFromNumpyByte(self, outputFilename):
        """ensure that a volume created by volumeFromData uses the dtype of the datablock by default"""
        data_block = np.arange(24000, dtype="byte").reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="ushort")
        v.writeFile()
        assert v.dtype == "byte"
    def testWriteDataFromNumpyChangeDtype(self, outputFilename):
        """ensure that a volume created by volumeFromData can overwrite the dtype if set explicitly"""
        data_block = np.arange(24000, dtype="ushort").reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="ushort",
                           dtype="float")
        v.writeFile()
        assert v.dtype == "float"
    ############################################################################
    # writeFile() sets the image:complete flag
    ############################################################################
    def testSettingImageCompleteFlag(self, outputFilename):
        """ensure that when writeFile() is called, the image:complete flag is set correctly"""
        data_block = np.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="uint")
        v.writeFile()
        pipe = os.popen("minccomplete %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        assert output == approx(0.0)

class TestCopyConstructor:
    def testCopyConstructorDimensions(self, outputFilename):
        """dimensions should be the same in copied volume"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename)
        ns = n.sizes[0:3]
        vs = v.sizes[0:3]
        n.closeVolume()
        v.closeVolume()
        assert ns == vs
    def testCopyWithoutData(self, outputFilename):
        """copying without data=True flag should result in array of zeros"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename)
        m = n.data.max()
        v.closeVolume()
        n.closeVolume()
        assert m == 0
    def testCopyWithData(self, outputFilename):
        """copying with data=True flag should result in a copy of the data"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename, data=True)
        va = np.average(v.data)
        na = np.average(n.data)
        v.closeVolume()
        n.closeVolume()
        assert va == na
    def testCopyWithData2(self, outputFilename):
        """ensure that data is copied and not referenced"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename, data=True)
        # set data to some random value
        n.data[:,:,:] = 10
        va = np.average(v.data)
        na = np.average(n.data)
        v.closeVolume()
        n.closeVolume()
        assert va != na
    def testEmptyFile(self):
        """ensure that empty volume is not written to disk"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, emptyFilename)
        v.closeVolume()
        n.closeVolume()
        with pytest.raises(OSError):
            os.stat(emptyFilename)


class TestEmptyConstructor:
    """tests for when no generator was used"""
    def testErrorOnDataAccess(self):
        """ensure error is raised on data access"""
        v = mincVolume(inputFile_ushort)
        with pytest.raises(NoDataException):
            v.getdata()
    def testLoadData(self):
        """data should be accessible once openFile is called"""
        v = mincVolume(inputFile_ushort)
        v.openFile()
        assert v.data.dtype == 'float64'
        v.closeVolume()

class TestReadWrite:
    """test the read-write cycle"""
    def testReadWrite(self, outputFilename):
        """ensure that data can be read and written correctly"""
        v = volumeFromFile(inputFile_ushort)
        o = volumeFromInstance(v, outputFilename, data=True)
        #print(o.data)
        o.data = v.data * 5
        v.closeVolume()
        o.writeFile()
        o_back_in = volumeFromFile(outputFilename)
        np.testing.assert_allclose(o.data, o_back_in.data)
        o_back_in.closeVolume()  # after this o.data is an array of zeros!

class TestFromDescription:
    """testing creation of brand new volumes"""
    def testCreateVolume(self):
        """test whether new volume can be created"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), (10,20,30),
                                  (-10,10,20), (0.5,0.5,0.5))
        v.data[:,:,:] = 3
        v.data[5,:,:] = 10
        v_mean = v.data.mean()
        v.writeFile()
        o = volumeFromFile(newFilename)
        o_mean = o.data.mean()
        o.closeVolume()
        assert o_mean == approx(v_mean)


class TestHyperslabs:
    """test getting and setting of hyperslabs"""
    def testGetHyperslab(self):
        """hyperslab should be same as slice from data array"""
        v = volumeFromFile(inputFile_ushort)
        sliceFromData = v.data[10,:,:]
        hyperslab = v.getHyperslab((10,0,0), (1, v.sizes[1], v.sizes[2]))
        sa = np.average(sliceFromData)
        ha = np.average(hyperslab)
        v.closeVolume()
        assert sa == approx(ha)
    def testHyperslabInfo(self):
        """make sure that hyperslabs store enough info about themselves"""
        v = volumeFromFile(inputFile_ushort)
        start = (10,0,0)
        count = (1, v.sizes[1], v.sizes[2])
        hyperslab = v.getHyperslab(start, count)
        v.closeVolume()
        assert hyperslab.start[1] == start[1]
    def testSetHyperslab(self, outputFilename):
        """setting hyperslab should change underlying volume"""
        v = volumeFromFile(inputFile_ushort)
        o = volumeFromInstance(v, outputFilename, data=False)
        hyperslab = v.getHyperslab((10,0,0), (1, v.sizes[1], v.sizes[2]))
        hyperslab = hyperslab * 100
        o.setHyperslab(hyperslab, (10,0,0), (1, v.sizes[1], v.sizes[2]))
        o.writeFile()
        v2 = volumeFromFile(outputFilename)
        h2 = v2.getHyperslab((10,0,0), (1, v2.sizes[1], v2.sizes[2]))
        v2.closeVolume()
        np.testing.assert_allclose(hyperslab, h2)
    def testSetHyperslabArrayNonContiguous(self, outputFilename):
        """same as above but with a non-C-contiguous hyperslab"""
        v = volumeFromFile(inputFile_ushort)
        o = volumeFromInstance(v, outputFilename, data=False)
        hyperslab = v.getHyperslab((10,0,0), (10, 15, 20)).T
        hyperslab = hyperslab * 100
        o.setHyperslab(hyperslab, (10,0,0), (20, 15, 10))
        o.writeFile()
        v2 = volumeFromFile(outputFilename)
        h2 = v2.getHyperslab((10,0,0), (20, 15, 10))
        v2.closeVolume()
        np.testing.assert_allclose(hyperslab, h2)
    def testHyperslabArray(self):
      """hyperslab should be reinsertable into volume"""
      with tmp_mnc_file() as f:
        outputFilename = f.name
        v = volumeFromFile(inputFile_ushort)
        o = volumeFromInstance(v, outputFilename, data=False)
        hyperslab = v.getHyperslab((10,0,0), (1, v.sizes[1], v.sizes[2]))
        hyperslab = hyperslab * 100
        o.setHyperslab(hyperslab, (10,0,0))
        o.writeFile()
        v2 = volumeFromFile(outputFilename)
        h2 = v2.getHyperslab((10,0,0), (1, v2.sizes[1], v2.sizes[2]))
        v2.closeVolume()
        np.testing.assert_allclose(hyperslab, h2)  #, 8)

class TestVectorFiles:
    """test reading and writing of vector files"""
    def testVectorRead(self):
        """make sure that a vector file can be read correctly"""
        v = volumeFromFile(inputVector)
        dimnames = v.dimnames
        v.closeVolume()
        assert dimnames[0] == "vector_dimension"
    def testVectorRead2(self):
        """make sure that volume has four dimensions"""
        v = volumeFromFile(inputVector)
        ndims = v.ndims
        v.closeVolume()
        assert ndims == 4
    def testReduceDimensions(self, outputFilename):
        """ensure that vector file can be turned into spatial volume"""
        f = tmp_mnc_file()
        outputFilename = f.name
        v = volumeFromFile(inputVector)
        v2 = volumeFromInstance(v, outputFilename, dims=["xspace", "yspace", "zspace"])
        ndims = v2.ndims
        v.closeVolume()
        v2.closeVolume()
        assert ndims == 3

class TestDirectionCosines:
    """test that pyminc deals correctly with direction cosines"""
    def testDefaultDirCos3DVFF(self):
        """testing reading the direction cosines of a file with standard values (volumeFromFile)"""
        v = volumeFromFile(inputFile_ushort)
        #
        # This file was created without explicitly setting the direction cosines.
        # in that case, the attribute is not set altogether, so we should test
        # for it using the known defaults, because libminc does extract the correct
        # default values
        #
        assert v._x_direction_cosines == approx((1.0, 0.0, 0.0))
        assert v._y_direction_cosines == approx((0.0, 1.0, 0.0))
        assert v._z_direction_cosines == approx((0.0, 0.0, 1.0))

    def testNonDefaultDirCos3DVFF(self):
        """testing reading the direction cosines of a file with non-standard values (volumeFromFile)"""
        v = volumeFromFile(input3DdirectionCosines)

        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert v._x_direction_cosines[0] == approx(float(from_file[0]))
        assert v._x_direction_cosines[1] == approx(float(from_file[1]))
        assert v._x_direction_cosines[2] == approx(float(from_file[2]))

        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert v._y_direction_cosines[0] == approx(float(from_file[0]))
        assert v._y_direction_cosines[1] == approx(float(from_file[1]))
        assert v._y_direction_cosines[2] == approx(float(from_file[2]))

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert v._z_direction_cosines[0] == approx(float(from_file[0]))
        assert v._z_direction_cosines[1] == approx(float(from_file[1]))
        assert v._z_direction_cosines[2] == approx(float(from_file[2]))

    def testWriteStandardDirCos3D(self, outputFilename):
        """test writing out a file with standard direction cosines (volumeLikeFile)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, data=True)
        v.data[::] = 367623
        v.writeFile()

        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(1.0)
        assert float(from_file[1]) == approx(0.0)
        assert float(from_file[2]) == approx(0.0)

        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(0.0)
        assert float(from_file[1]) == approx(1.0)
        assert float(from_file[2]) == approx(0.0)

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(0.0)
        assert float(from_file[1]) == approx(0.0)
        assert float(from_file[2]) == approx(1.0)

    def testWriteNonStandardDirCos3D(self, outputFilename):
        """test writing out a file with non standard direction cosines (volumeLikeFile)"""
        v = volumeLikeFile(input3DdirectionCosines, outputFilename, data=True)
        v.data[::] = 282518
        v.writeFile()

        ### X
        pipe_out = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % outputFilename, "r")
        from_file_out = pipe_out.read().rstrip().split(" ")
        pipe_out.close()
        pipe_in = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file_in = pipe_in.read().rstrip().split(" ")
        pipe_in.close()

        assert float(from_file_out[0]) == approx(float(from_file_in[0]))
        assert float(from_file_out[1]) == approx(float(from_file_in[1]))
        assert float(from_file_out[2]) == approx(float(from_file_in[2]))

        ### Y
        pipe_out = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % outputFilename, "r")
        from_file_out = pipe_out.read().rstrip().split(" ")
        pipe_out.close()
        pipe_in = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file_in = pipe_in.read().rstrip().split(" ")
        pipe_in.close()

        assert float(from_file_out[0]) == approx(float(from_file_in[0]))
        assert float(from_file_out[1]) == approx(float(from_file_in[1]))
        assert float(from_file_out[2]) == approx(float(from_file_in[2]))

        ### Z
        pipe_out = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % outputFilename, "r")
        from_file_out = pipe_out.read().rstrip().split(" ")
        pipe_out.close()
        pipe_in = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file_in = pipe_in.read().rstrip().split(" ")
        pipe_in.close()

        assert float(from_file_out[0]) == approx(float(from_file_in[0]))
        assert float(from_file_out[1]) == approx(float(from_file_in[1]))
        assert float(from_file_out[2]) == approx(float(from_file_in[2]))

    def testDirCosVolumeFromDescription(self):
        """test creating a volume with direction cosines using volumeFromDescription"""
        x0 = 0.9563735353
        x1 = 0.1093836343
        x2 = 0.2345342349
        y0 = 0.2186893435
        y1 = 0.3457428934
        y2 = 0.0219273265
        z0 = 0.0217054823
        z1 = 0.1252894877
        z2 = 0.9344668322
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"),
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="float",
                                  x_dir_cosines=(x0, x1, x2),
                                  y_dir_cosines=(y0, y1, y2),
                                  z_dir_cosines=(z0, z1, z2))
        v.data[::] = 5

        ### test that the attributes have been set
        assert v._x_direction_cosines == approx((x0, x1, x2))

        assert v._y_direction_cosines == approx((y0, y1, y2))

        assert v._z_direction_cosines == approx((z0, z1, z2))

        v.writeFile()

        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % newFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(x0)
        assert float(from_file[1]) == approx(x1)
        assert float(from_file[2]) == approx(x2)

        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % newFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(y0)
        assert float(from_file[1]) == approx(y1)
        assert float(from_file[2]) == approx(y2)

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % newFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(z0)
        assert float(from_file[1]) == approx(z1)
        assert float(from_file[2]) == approx(z2)

    def testDirCosVolumeFromData(self, outputFilename):
        """test creating a volume with direction cosines using volumeFromData"""
        x0 = 0.8476348547
        x1 = 0.2164954895
        x2 = 0.2534970854
        y0 = 0.1232442363
        y1 = 0.7664544689
        y2 = 0.0047723742
        z0 = 0.1784390237
        z1 = 0.4534233971
        z2 = 0.8564847453
        data_block = np.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="int",
                           x_dir_cosines=(x0, x1, x2),
                           y_dir_cosines=(y0, y1, y2),
                           z_dir_cosines=(z0, z1, z2))

        ### test that the attributes have been set
        assert v._x_direction_cosines == approx((x0, x1, x2))
        assert v._y_direction_cosines == approx((y0, y1, y2))
        assert v._z_direction_cosines == approx((z0, z1, z2))

        v.writeFile()

        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(x0)
        assert float(from_file[1]) == approx(x1)
        assert float(from_file[2]) == approx(x2)

        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(y0)
        assert float(from_file[1]) == approx(y1)
        assert float(from_file[2]) == approx(y2)

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        pipe.close()
        assert float(from_file[0]) == approx(z0)
        assert float(from_file[1]) == approx(z1)
        assert float(from_file[2]) == approx(z2)

    def testDirCosVolumeFromInstance(self, outputFilename):
        """test creating a volume with direction cosines using volumeFromInstance"""
        in_v = volumeFromFile(input3DdirectionCosines)
        v = volumeFromInstance(in_v, outputFilename, volumeType="short")
        v.data[::] = 5

        assert v._x_direction_cosines[0] == approx(in_v._x_direction_cosines[0])
        assert v._x_direction_cosines[1] == approx(in_v._x_direction_cosines[1])
        assert v._x_direction_cosines[2] == approx(in_v._x_direction_cosines[2])
        assert v._y_direction_cosines[0] == approx(in_v._y_direction_cosines[0])
        assert v._y_direction_cosines[1] == approx(in_v._y_direction_cosines[1])
        assert v._y_direction_cosines[2] == approx(in_v._y_direction_cosines[2])
        assert v._z_direction_cosines[0] == approx(in_v._z_direction_cosines[0])
        assert v._z_direction_cosines[1] == approx(in_v._z_direction_cosines[1])
        assert v._z_direction_cosines[2] == approx(in_v._z_direction_cosines[2])
        # FIXME fails:
        #assert in_v._y_direction_cosines == approx(v._x_direction_cosines)
        #assert v._y_direction_cosines == approx(in_v._y_direction_cosines)
        #assert v._z_direction_cosines == approx(in_v._z_direction_cosines)

        v.writeFile()
        in_v.closeVolume()

class TestXfmsAppliedToCoordinates:
    """test that xfm files can be used to transform x,y,z coordinates"""
    def testForwardTransformSingleXfm(self):
        """testing coordinates transformed using the forward transform and a single transformation"""

        new_xyz_coords = transform_xyz_coordinates_using_xfm(outputXfmFilename1, 6.68, 3.14, 7.00)
        assert new_xyz_coords == approx((4.33400016486645, 32.3265016365052, -12.4399995803833))

    def testInverseTransformSingleXfm(self):
        """testing coordinates transformed using the inverse transform and a single transformation"""

        new_xyz_coords = transform_xyz_coordinates_using_xfm(outputXfmFilename1, 6.68, 3.14, 7.00, use_inverse=True)
        assert new_xyz_coords == approx((18.4099990008772, -3.64755821904214, 0.520000139872233))

    def testForwardTransformConcatenatedXfm(self):
        """testing coordinates transformed using the forward transform and a concatenated transformation"""

        new_xyz_coords = transform_xyz_coordinates_using_xfm(outputXfmFilename3, 6.68, 3.14, 7.00)
        assert new_xyz_coords == approx((259.159993714094, 188.041454144745, -1744.15997695923))

    def testInverseTransformConcatenatedXfm(self):
        """testing coordinates transformed using the inverse transform and a concatenated transformation"""

        new_xyz_coords = transform_xyz_coordinates_using_xfm(outputXfmFilename3,
                                                             6.68, 3.14, 7.00, use_inverse=True)
        assert new_xyz_coords == approx((-119.559994975925, -2.72634880128239, 0.0509524723840147))
