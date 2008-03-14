import unittest
from volumes import mincException, mincVolume, NoDataException, IncorrectDimsException
from factory import volumeFromFile, volumeFromInstance
import numpy as N
import os

class TestGenerators(unittest.TestCase):
    def setUp(self):
        self.inputFilename = "/home/jlerch/src/test.mnc"
        self.outputFilename = "/home/jlerch/src/test-out.mnc"

    def testFromFileError(self):
        """attempting to load a garbage file should raise exception"""
        self.assertRaises(mincException, volumeFromFile, "garbage.mnc")
    def testFromFileDataType(self):
        """ensure that default datatype is float"""
        v = volumeFromFile(self.inputFilename)
        dt = v.data.dtype
        v.closeVolume()
        self.assertEqual(dt, 'float32')
    def testFromFileData(self):
        """ensure data read from file is correct"""
        v = volumeFromFile(self.inputFilename)
        a = N.average(v.data)
        v.closeVolume()
        pipe = os.popen("mincstats -mean -quiet %s" % self.inputFilename, "r")
        output = float(pipe.read())
        pipe.close()
        self.assertAlmostEqual(a, output, 1)
    def testCopyConstructorDimensions(self):
        """dimensions should be the same in copied volume"""
        v = volumeFromFile(self.inputFilename)
        n = volumeFromInstance(v, self.outputFilename)
        ns = n.sizes[0:3]
        vs = v.sizes[0:3]
        n.closeVolume()
        v.closeVolume()
        self.assertEqual(ns, vs)
    def testCopyWithoutData(self):
        """copying without data=True flag should result in array of zeros"""
        v = volumeFromFile(self.inputFilename)
        n = volumeFromInstance(v, self.outputFilename)
        m = n.data.max()
        v.closeVolume()
        n.closeVolume()
        self.assertEqual(m, 0)
    def testCopyWithData(self):
        """copying with data=True flag should result in a copy of the data"""
        v = volumeFromFile(self.inputFilename)
        n = volumeFromInstance(v, self.outputFilename, data=True)
        va = N.average(v.data)
        na = N.average(n.data)
        v.closeVolume()
        n.closeVolume()
        self.assertEqual(va, na)
    def testCopyWithData2(self):
        """ensure that data is copied and not referenced"""
        v = volumeFromFile(self.inputFilename)
        n = volumeFromInstance(v, self.outputFilename, data=True)
        # set data to some random value
        n.data[:,:,:] = 10
        va = N.average(v.data)
        na = N.average(n.data)
        v.closeVolume()
        n.closeVolume()
        self.assertNotEqual(va, na)
        
if __name__ == "__main__":
    unittest.main()
        
        