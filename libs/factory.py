"""factories for creating mincVolumes"""

from volumes import mincException,mincVolume

def volumeFromFile(filename):
    """creates a new mincVolume from existing file"""
    v = mincVolume(filename)
    v.openFile()
    return(v)
    
def volumeFromInstance(volInstance, outputFilename, data=False):
    """creates new mincVolume from another mincVolume"""
    v = mincVolume(outputFilename)
    v.copyDimensions(volInstance)
    v.copyDtype(volInstance)
    v.createVolumeHandle()
    if data:
        if not volInstance.dataLoaded:
            volInstance.loadData()
        v.createVolumeImage()  
        v.data = volInstance.data.copy()
    
    return(v)