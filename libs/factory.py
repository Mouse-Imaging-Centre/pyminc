"""factories for creating mincVolumes"""

from volumes import mincException,mincVolume

def volumeFromFile(filename):
    v = mincVolume()
    v.openFile(filename)
    