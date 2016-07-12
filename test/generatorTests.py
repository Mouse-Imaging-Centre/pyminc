import unittest
from pyminc.volumes.volumes import *
from pyminc.volumes.factory import *
from pyminc.volumes.libpyminc2 import *
import numpy as N
import os
import subprocess
import tempfile

outputFilename = tempfile.NamedTemporaryFile(prefix="test-out-", suffix=".mnc").name
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

class TestFromFile(unittest.TestCase):
    """test the volumeFromFile generator"""
    def testFromFileError(self):
        """attempting to load a garbage file should raise exception"""
        self.assertRaises(mincException, volumeFromFile, "garbage.mnc")
    def testFromFileDataTypeByte(self):
        """ensure byte data is read as double by default"""
        v = volumeFromFile(inputFile_byte)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeShort(self):
        """ensure short data is read as double by default"""
        v = volumeFromFile(inputFile_short)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeInt(self):
        """ensure int data is read as double by default"""
        v = volumeFromFile(inputFile_int)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeFloat(self):
        """ensure float data is read as double by default"""
        v = volumeFromFile(inputFile_float)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeDouble(self):
        """ensure double data is read as double"""
        v = volumeFromFile(inputFile_double)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeUByte(self):
        """ensure unsigned byte data is read as double by default"""
        v = volumeFromFile(inputFile_ubyte)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeUShort(self):
        """ensure unsigned short data is read as double by default"""
        v = volumeFromFile(inputFile_ushort)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
    def testFromFileDataTypeUInt(self):
        """ensure unsigned int data is read as double by default"""
        v = volumeFromFile(inputFile_uint)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float64')
        
    def testFromFileDataTypeSetToByte(self):
        """ensure that datatype can be set to byte"""
        v = volumeFromFile(inputFile_short, dtype="byte")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "int8")
    def testFromFileDataTypeSetToShort(self):
        """ensure that datatype can be set to short"""
        v = volumeFromFile(inputFile_byte, dtype="short")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "int16")
    def testFromFileDataTypeSetToInt(self):
        """ensure that datatype can be set to int"""
        v = volumeFromFile(inputFile_byte, dtype="int")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "int32")
    def testFromFileDataTypeSetToFloat(self):
        """ensure that datatype can be set to float"""
        v = volumeFromFile(inputFile_byte, dtype="float")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "float32")
    def testFromFileDataTypeSetToDouble(self):
        """ensure that datatype can be set to double"""
        v = volumeFromFile(inputFile_byte, dtype="double")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "float64")
    def testFromFileDataTypeSetToUByte(self):
        """ensure that datatype can be set to unsigned byte"""
        v = volumeFromFile(inputFile_byte, dtype="ubyte")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "uint8")
    def testFromFileDataTypeSetToUShort(self):
        """ensure that datatype can be set to unsigned short"""
        v = volumeFromFile(inputFile_byte, dtype="ushort")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "uint16")
    def testFromFileDataTypeSetToUInt(self):
        """ensure that datatype can be set to unsigned int"""
        v = volumeFromFile(inputFile_byte, dtype="uint")
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, "uint32")
    def testFromFileDataByte(self):
        """ensure that byte data is read correct with a precision of 8 decimals on a call to aveage()"""
        v = volumeFromFile(inputFile_byte)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % inputFile_byte, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 8)
    def testFromFileDataShort(self):
        """ensure that short data is read correct with a precision of 8 decimals on a call to aveage()"""
        v = volumeFromFile(inputFile_short)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % inputFile_short, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 8)
    def testFromFileDataInt(self):
        """ensure that int data is read correct with a precision of 8 decimals on a call to aveage()"""
        v = volumeFromFile(inputFile_int)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % inputFile_int, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 8)
    def testFromFileDataFloat(self):
        """ensure that float data is read correct with a precision of 8 decimals on a call to aveage()"""
        v = volumeFromFile(inputFile_float)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % inputFile_float, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 8)
    def testFromFileDataDouble(self):
        """ensure that double data is read correct with a precision of 8 decimals on a call to aveage()"""
        v = volumeFromFile(inputFile_double)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % inputFile_double, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 8)
        
        
class TestWriteFileDataTypes(unittest.TestCase):
    ############################################################################
    # volumeFromDescription
    ############################################################################
    def testWriteDataAsByte(self):
        """ensure that a volume created by volumeFromDescription as byte is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="byte")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "byte")
    def testWriteDataAsShort(self):
        """ensure that a volume created by volumeFromDescription as short is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="short")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "short")
    def testWriteDataAsInt(self):
        """ensure that a volume created by volumeFromDescription as int is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="int")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "int")
    def testWriteDataAsFloat(self):
        """ensure that a volume created by volumeFromDescription as float is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="float")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "float")
    def testWriteDataAsDouble(self):
        """ensure that a volume created by volumeFromDescription as double is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="double")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "double")
    def testWriteDataAsUByte(self):
        """ensure that a volume created by volumeFromDescription as unsigned byte is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="ubyte")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ubyte")
    def testWriteDataAsUShort(self):
        """ensure that a volume created by volumeFromDescription as unsigned short is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="ushort")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ushort")
    def testWriteDataAsUInt(self):
        """ensure that a volume created by volumeFromDescription as unsigned int is written out as such"""
        v = volumeFromDescription(newFilename, ("xspace", "yspace", "zspace"), 
                                  (10,20,30), (-10,10,20), (0.5,0.5,0.5),
                                  volumeType="uint")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(newFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "uint")
    ############################################################################
    # volumeFromInstance
    ############################################################################
    def testWriteDataAsByte_vFI(self):
        """ensure that a volume created by volumeFromInstance as byte is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="byte")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "byte")
    def testWriteDataAsShort_vFI(self):
        """ensure that a volume created by volumeFromInstance as short is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="short")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "short")
    def testWriteDataAsInt_vFI(self):
        """ensure that a volume created by volumeFromInstance as int is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="int")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "int")
    def testWriteDataAsFloat_vFI(self):
        """ensure that a volume created by volumeFromInstance as float is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="float")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "float")
    def testWriteDataAsDouble_vFI(self):
        """ensure that a volume created by volumeFromInstance as double is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="double")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "double")
    def testWriteDataAsUByte_vFI(self):
        """ensure that a volume created by volumeFromInstance as unsigned byte is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="ubyte")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ubyte")
    def testWriteDataAsUShort_vFI(self):
        """ensure that a volume created by volumeFromInstance as unsigned short is written out as such"""
        in_v = volumeFromFile(inputFile_byte)
        v = volumeFromInstance(in_v, outputFilename, volumeType="ushort")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ushort")
    def testWriteDataAsUInt_vFI(self):
        """ensure that a volume created by volumeFromInstance as unsigned int is written out as such"""
        in_v = volumeFromFile(inputFile_short)
        v = volumeFromInstance(in_v, outputFilename, volumeType="uint")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "uint")
    ############################################################################
    # volumeLikeFile
    ############################################################################
    def testWriteDataAsByte_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (byte)"""
        v = volumeLikeFile(inputFile_byte, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "byte")
    def testWriteDataAsShort_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (short)"""
        v = volumeLikeFile(inputFile_short, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "short")
    def testWriteDataAsInt_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (int)"""
        v = volumeLikeFile(inputFile_int, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "int")
    def testWriteDataAsFloat_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (float)"""
        v = volumeLikeFile(inputFile_float, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "float")
    def testWriteDataAsDouble_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (double)"""
        v = volumeLikeFile(inputFile_double, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "double")
    def testWriteDataAsUByte_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (ubyte)"""
        v = volumeLikeFile(inputFile_ubyte, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ubyte")
    def testWriteDataAsUShort_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (ushort)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ushort")
    def testWriteDataAsUint_vLF_base(self):
        """ensure that a volume created by volumeLikeFile has the same type as its input (uint)"""
        v = volumeLikeFile(inputFile_uint, outputFilename)
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "uint")
    #########################
    # changing the volumeType
    #########################
    def testWriteDataAsByte_vLF(self):
        """ensure that a volume created by volumeLikeFile as byte is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, volumeType="byte")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "byte")
    def testWriteDataAsShort_vLF(self):
        """ensure that a volume created by volumeLikeFile as short is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, volumeType="short")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "short")
    def testWriteDataAsInt_vLF(self):
        """ensure that a volume created by volumeLikeFile as int is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, volumeType="int")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "int")
    def testWriteDataAsFloat_vLF(self):
        """ensure that a volume created by volumeLikeFile as float is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, volumeType="float")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "float")
    def testWriteDataAsDouble_vLF(self):
        """ensure that a volume created by volumeLikeFile as double is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, volumeType="double")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "double")
    def testWriteDataAsUByte_vLF(self):
        """ensure that a volume created by volumeLikeFile as ubyte is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_double, outputFilename, volumeType="ubyte")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ubyte")
    def testWriteDataAsUShort_vLF(self):
        """ensure that a volume created by volumeLikeFile as ushort is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_float, outputFilename, volumeType="ushort")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ushort")
    def testWriteDataAsUInt_vLF(self):
        """ensure that a volume created by volumeLikeFile as uint is written out as such (input file has different volumeType)"""
        v = volumeLikeFile(inputFile_byte, outputFilename, volumeType="uint")
        v.data[::] = 5
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "uint")
    ############################################################################
    # volumeFromData
    ############################################################################
    def testWriteDataAsByte_vFD(self):
        """ensure that a volume created by volumeFromData as byte is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="byte")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "byte")
    def testWriteDataAsByte_vFD_content(self):
        """ensure that a volume created by volumeFromData as byte writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="byte")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsShort_vFD(self):
        """ensure that a volume created by volumeFromData as short is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="short")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "short")
    def testWriteDataAsShort_vFD_content(self):
        """ensure that a volume created by volumeFromData as short writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="short")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsInt_vFD(self):
        """ensure that a volume created by volumeFromData as int is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="int")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "int")
    def testWriteDataAsInt_vFD_content(self):
        """ensure that a volume created by volumeFromData as int writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="int")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsFloat_vFD(self):
        """ensure that a volume created by volumeFromData as float is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="float")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "float")
    def testWriteDataAsFloat_vFD_content(self):
        """ensure that a volume created by volumeFromData as float writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="float")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsDouble_vFD(self):
        """ensure that a volume created by volumeFromData as double is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="double")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "double")
    def testWriteDataAsDouble_vFD_content(self):
        """ensure that a volume created by volumeFromData as double writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="double")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsUByte_vFD(self):
        """ensure that a volume created by volumeFromData as unsigned byte is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="ubyte")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ubyte")
    def testWriteDataAsUByte_vFD_content(self):
        """ensure that a volume created by volumeFromData as unsigned byte writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="ubyte")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsUShort_vFD(self):
        """ensure that a volume created by volumeFromData as unsigned short is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="ushort")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "ushort")
    def testWriteDataAsUShort_vFD_content(self):
        """ensure that a volume created by volumeFromData as unsigned short writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="ushort")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    def testWriteDataAsUInt_vFD(self):
        """ensure that a volume created by volumeFromData as unsigned int is written out as such"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="uint")
        v.writeFile()
        # retrieve data type from written file:
        vol_in = volumeFromFile(outputFilename)
        vol_in_data_type = vol_in.volumeType
        self.assertEqual(vol_in_data_type, "uint")
    def testWriteDataAsUInt_vFD_content(self):
        """ensure that a volume created by volumeFromData as unsigned int writes correct data"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="uint")
        v.writeFile()
        # retrieve mean of data written to disk:
        pipe = os.popen("mincstats -mean -quiet %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(output, data_block.mean(), 8)
    ############################################################################
    # writeFile() sets the image:complete flag
    ############################################################################
    def testSettingImageCompleteFlag(self):
        """ensure that when writeFile() is called, the image:complete flag is set correctly"""
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="uint")
        v.writeFile()
        pipe = os.popen("minccomplete %s" % outputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertEqual(output, 0.0)
    
class TestCopyConstructor(unittest.TestCase):
    def testCopyConstructorDimensions(self):
        """dimensions should be the same in copied volume"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename)
        ns = n.sizes[0:3]
        vs = v.sizes[0:3]
        n.closeVolume()
        v.closeVolume()
        self.assertEqual(ns, vs)
    def testCopyWithoutData(self):
        """copying without data=True flag should result in array of zeros"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename)
        m = n.data.max()
        v.closeVolume()
        n.closeVolume()
        self.assertEqual(m, 0)
    def testCopyWithData(self):
        """copying with data=True flag should result in a copy of the data"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename, data=True)
        va = N.average(v.data)
        na = N.average(n.data)
        v.closeVolume()
        n.closeVolume()
        self.assertEqual(va, na)
    def testCopyWithData2(self):
        """ensure that data is copied and not referenced"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, outputFilename, data=True)
        # set data to some random value
        n.data[:,:,:] = 10
        va = N.average(v.data)
        na = N.average(n.data)
        v.closeVolume()
        n.closeVolume()
        self.assertNotEqual(va, na)
    def testEmptyFile(self):
        """ensure that empty volume is not written to disk"""
        v = volumeFromFile(inputFile_ushort)
        n = volumeFromInstance(v, emptyFilename)
        v.closeVolume()
        n.closeVolume()
        self.assertRaises(OSError, os.stat, emptyFilename)
        
        
class TestEmptyConstructor(unittest.TestCase):
    """tests for when no generator was used"""
    def testErrorOnDataAccess(self):
        """ensure error is raised on data access"""
        v = mincVolume(inputFile_ushort)
        self.assertRaises(NoDataException, v.getdata)
    def testLoadData(self):
        """data should be accessible once openFile is called"""
        v = mincVolume(inputFile_ushort)
        v.openFile()
        self.assertEqual(v.data.dtype, 'float64')
        v.closeVolume()
        
class TestReadWrite(unittest.TestCase):
    """test the read-write cycle"""
    def testReadWrite(self):
        """ensure that data can be read and written correctly"""
        v = volumeFromFile(inputFile_ushort)
        o = volumeFromInstance(v, outputFilename, data=True)
        #print(o.data)
        o.data = v.data * 5
        oa = N.average(o.data)
        v.closeVolume()
        o.writeFile()
        o_back_in = volumeFromFile(outputFilename)
        o_back_in_a = N.average(o_back_in.data)
        o_back_in.closeVolume()
        self.assertAlmostEqual(o_back_in_a, oa, 8)

class TestFromDescription(unittest.TestCase):
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
        self.assertAlmostEqual(v_mean, o_mean, 8)


class TestHyperslabs(unittest.TestCase):
    """test getting and setting of hyperslabs"""
    def testGetHyperslab(self):
        """hyperslab should be same as slice from data array"""
        v = volumeFromFile(inputFile_ushort)
        sliceFromData = v.data[10,:,:]
        hyperslab = v.getHyperslab((10,0,0), (1, v.sizes[1], v.sizes[2]))
        sa = N.average(sliceFromData)
        ha = N.average(hyperslab)
        v.closeVolume()
        self.assertEqual(sa, ha)
    def testHyperslabInfo(self):
        """make sure that hyperslabs store enough info about themselves"""
        v = volumeFromFile(inputFile_ushort)
        start = (10,0,0)
        count = (1, v.sizes[1], v.sizes[2])
        hyperslab = v.getHyperslab(start, count)
        v.closeVolume()
        self.assertEqual(hyperslab.start[1], start[1])
    def testSetHyperslab(self):
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
        self.assertAlmostEqual(N.average(hyperslab), N.average(h2), 8)
    def testHyperslabArray(self):
        """hyperslab should be reinsertable into volume"""
        v = volumeFromFile(inputFile_ushort)
        o = volumeFromInstance(v, outputFilename, data=False)
        hyperslab = v.getHyperslab((10,0,0), (1, v.sizes[1], v.sizes[2]))
        hyperslab = hyperslab * 100
        o.setHyperslab(hyperslab, (10,0,0))
        o.writeFile()
        v2 = volumeFromFile(outputFilename)
        h2 = v2.getHyperslab((10,0,0), (1, v2.sizes[1], v2.sizes[2]))
        v2.closeVolume()
        self.assertAlmostEqual(N.average(hyperslab), N.average(h2), 8)
class testVectorFiles(unittest.TestCase):
    """test reading and writing of vector files"""
    def testVectorRead(self):
        """make sure that a vector file can be read correctly"""
        v = volumeFromFile(inputVector)
        dimnames = v.dimnames
        v.closeVolume()
        self.assertEqual(dimnames[0], "vector_dimension")
    def testVectorRead2(self):
        """make sure that volume has four dimensions"""
        v = volumeFromFile(inputVector)
        ndims = v.ndims
        v.closeVolume()
        self.assertEqual(ndims, 4)
    def testReduceDimensions(self):
        """ensure that vector file can be turned into spatial volume"""
        v = volumeFromFile(inputVector)
        v2 = volumeFromInstance(v, outputFilename, dims=["xspace", "yspace", "zspace"])
        ndims = v2.ndims
        v.closeVolume()
        v2.closeVolume()
        self.assertEqual(ndims, 3)
        
class testDirectionCosines(unittest.TestCase):
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
        self.assertAlmostEqual(v._x_direction_cosines[0], 1.0, 8)
        self.assertAlmostEqual(v._x_direction_cosines[1], 0.0, 8)
        self.assertAlmostEqual(v._x_direction_cosines[2], 0.0, 8)
        
        self.assertAlmostEqual(v._y_direction_cosines[0], 0.0, 8)
        self.assertAlmostEqual(v._y_direction_cosines[1], 1.0, 8)
        self.assertAlmostEqual(v._y_direction_cosines[2], 0.0, 8)
        
        self.assertAlmostEqual(v._z_direction_cosines[0], 0.0, 8)
        self.assertAlmostEqual(v._z_direction_cosines[1], 0.0, 8)
        self.assertAlmostEqual(v._z_direction_cosines[2], 1.0, 8)
    def testNonDefaultDirCos3DVFF(self):
        """testing reading the direction cosines of a file with non-standard values (volumeFromFile)"""
        v = volumeFromFile(input3DdirectionCosines)
        
        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(v._x_direction_cosines[0], float(from_file[0]), 8)
        self.assertAlmostEqual(v._x_direction_cosines[1], float(from_file[1]), 8)
        self.assertAlmostEqual(v._x_direction_cosines[2], float(from_file[2]), 8)
        
        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(v._y_direction_cosines[0], float(from_file[0]), 8)
        self.assertAlmostEqual(v._y_direction_cosines[1], float(from_file[1]), 8)
        self.assertAlmostEqual(v._y_direction_cosines[2], float(from_file[2]), 8)
        
        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(v._z_direction_cosines[0], float(from_file[0]), 8)
        self.assertAlmostEqual(v._z_direction_cosines[1], float(from_file[1]), 8)
        self.assertAlmostEqual(v._z_direction_cosines[2], float(from_file[2]), 8)
        
    def testWriteStandardDirCos3D(self):
        """test writing out a file with standard direction cosines (volumeLikeFile)"""
        v = volumeLikeFile(inputFile_ushort, outputFilename, data=True)
        v.data[::] = 367623
        v.writeFile()
        
        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), 1.0, 8)
        self.assertAlmostEqual(float(from_file[1]), 0.0, 8)
        self.assertAlmostEqual(float(from_file[2]), 0.0, 8)
        
        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), 0.0, 8)
        self.assertAlmostEqual(float(from_file[1]), 1.0, 8)
        self.assertAlmostEqual(float(from_file[2]), 0.0, 8)

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), 0.0, 8)
        self.assertAlmostEqual(float(from_file[1]), 0.0, 8)
        self.assertAlmostEqual(float(from_file[2]), 1.0, 8)
        
    def testWriteNonStandardDirCos3D(self):
        """test writing out a file with non standard direction cosines (volumeLikeFile)"""
        v = volumeLikeFile(input3DdirectionCosines, outputFilename, data=True)
        v.data[::] = 282518
        v.writeFile()
        
        ### X
        pipe_out = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % outputFilename, "r")
        from_file_out = pipe_out.read().rstrip().split(" ")
        pipe_in = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file_in = pipe_in.read().rstrip().split(" ")
        
        self.assertAlmostEqual(float(from_file_out[0]), float(from_file_in[0]), 8)
        self.assertAlmostEqual(float(from_file_out[1]), float(from_file_in[1]), 8)
        self.assertAlmostEqual(float(from_file_out[2]), float(from_file_in[2]), 8)
        
        ### Y
        pipe_out = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % outputFilename, "r")
        from_file_out = pipe_out.read().rstrip().split(" ")
        pipe_in = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file_in = pipe_in.read().rstrip().split(" ")
        
        self.assertAlmostEqual(float(from_file_out[0]), float(from_file_in[0]), 8)
        self.assertAlmostEqual(float(from_file_out[1]), float(from_file_in[1]), 8)
        self.assertAlmostEqual(float(from_file_out[2]), float(from_file_in[2]), 8)
        
        ### Z
        pipe_out = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % outputFilename, "r")
        from_file_out = pipe_out.read().rstrip().split(" ")
        pipe_in = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % input3DdirectionCosines, "r")
        from_file_in = pipe_in.read().rstrip().split(" ")
        
        self.assertAlmostEqual(float(from_file_out[0]), float(from_file_in[0]), 8)
        self.assertAlmostEqual(float(from_file_out[1]), float(from_file_in[1]), 8)
        self.assertAlmostEqual(float(from_file_out[2]), float(from_file_in[2]), 8)
        
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
        self.assertAlmostEqual(v._x_direction_cosines[0], x0, 8)
        self.assertAlmostEqual(v._x_direction_cosines[1], x1, 8)
        self.assertAlmostEqual(v._x_direction_cosines[2], x2, 8)
        
        self.assertAlmostEqual(v._y_direction_cosines[0], y0, 8)
        self.assertAlmostEqual(v._y_direction_cosines[1], y1, 8)
        self.assertAlmostEqual(v._y_direction_cosines[2], y2, 8)
        
        self.assertAlmostEqual(v._z_direction_cosines[0], z0, 8)
        self.assertAlmostEqual(v._z_direction_cosines[1], z1, 8)
        self.assertAlmostEqual(v._z_direction_cosines[2], z2, 8)
        
        v.writeFile()
        
        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % newFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), x0, 8)
        self.assertAlmostEqual(float(from_file[1]), x1, 8)
        self.assertAlmostEqual(float(from_file[2]), x2, 8)
        
        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % newFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), y0, 8)
        self.assertAlmostEqual(float(from_file[1]), y1, 8)
        self.assertAlmostEqual(float(from_file[2]), y2, 8)

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % newFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), z0, 8)
        self.assertAlmostEqual(float(from_file[1]), z1, 8)
        self.assertAlmostEqual(float(from_file[2]), z2, 8)
        
    def testDirCosVolumeFromData(self):
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
        data_block = N.arange(24000).reshape(20,30,40)
        v = volumeFromData(outputFilename, data_block,
                           dimnames=("xspace", "yspace", "zspace"),
                           starts=(0, 0, 0),
                           steps=(1, 1, 1),
                           volumeType="int",
                           x_dir_cosines=(x0, x1, x2),
                           y_dir_cosines=(y0, y1, y2),
                           z_dir_cosines=(z0, z1, z2))
        
        ### test that the attributes have been set
        self.assertAlmostEqual(v._x_direction_cosines[0], x0, 8)
        self.assertAlmostEqual(v._x_direction_cosines[1], x1, 8)
        self.assertAlmostEqual(v._x_direction_cosines[2], x2, 8)
        
        self.assertAlmostEqual(v._y_direction_cosines[0], y0, 8)
        self.assertAlmostEqual(v._y_direction_cosines[1], y1, 8)
        self.assertAlmostEqual(v._y_direction_cosines[2], y2, 8)
        
        self.assertAlmostEqual(v._z_direction_cosines[0], z0, 8)
        self.assertAlmostEqual(v._z_direction_cosines[1], z1, 8)
        self.assertAlmostEqual(v._z_direction_cosines[2], z2, 8)
        
        v.writeFile()
        
        pipe = os.popen("mincinfo -attvalue xspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), x0, 8)
        self.assertAlmostEqual(float(from_file[1]), x1, 8)
        self.assertAlmostEqual(float(from_file[2]), x2, 8)
        
        pipe = os.popen("mincinfo -attvalue yspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), y0, 8)
        self.assertAlmostEqual(float(from_file[1]), y1, 8)
        self.assertAlmostEqual(float(from_file[2]), y2, 8)

        pipe = os.popen("mincinfo -attvalue zspace:direction_cosines %s" % outputFilename, "r")
        from_file = pipe.read().rstrip().split(" ")
        self.assertAlmostEqual(float(from_file[0]), z0, 8)
        self.assertAlmostEqual(float(from_file[1]), z1, 8)
        self.assertAlmostEqual(float(from_file[2]), z2, 8)
    
    def testDirCosVolumeFromInstance(self):
        """test creating a volume with direction cosines using volumeFromInstance"""
        in_v = volumeFromFile(input3DdirectionCosines)
        v = volumeFromInstance(in_v, outputFilename, volumeType="short")
        v.data[::] = 5
        
        self.assertAlmostEqual(v._x_direction_cosines[0], in_v._x_direction_cosines[0], 8)
        self.assertAlmostEqual(v._x_direction_cosines[1], in_v._x_direction_cosines[1], 8)
        self.assertAlmostEqual(v._x_direction_cosines[2], in_v._x_direction_cosines[2], 8)
        
        self.assertAlmostEqual(v._y_direction_cosines[0], in_v._y_direction_cosines[0], 8)
        self.assertAlmostEqual(v._y_direction_cosines[1], in_v._y_direction_cosines[1], 8)
        self.assertAlmostEqual(v._y_direction_cosines[2], in_v._y_direction_cosines[2], 8)
        
        self.assertAlmostEqual(v._z_direction_cosines[0], in_v._z_direction_cosines[0], 8)
        self.assertAlmostEqual(v._z_direction_cosines[1], in_v._z_direction_cosines[1], 8)
        self.assertAlmostEqual(v._z_direction_cosines[2], in_v._z_direction_cosines[2], 8)
        
        v.writeFile()
        in_v.closeVolume()
        
if __name__ == "__main__":
    unittest.main()
        
        
