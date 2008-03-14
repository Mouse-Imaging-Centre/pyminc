import unittest
from volumes import mincException, mincVolume, NoDataException
from factory import volumeFromFile

class TestGenerators(unittest.TestCase):
    def setUp(self):
        self.inputFilename = "/home/jlerch/src/test.mnc"
        self.outputFilename = "/home/jlerch/src/test-out.mnc"
        
    def testFromFileError(self):
        self.assertRaises(mincException, volumeFromFile, "garbage.mnc")
        
if __name__ == "__main__":
    unittest.main()
        
        