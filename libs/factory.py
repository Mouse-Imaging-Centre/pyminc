"""factories for creating mincVolumes"""

from volumes import mincException,mincVolume

def volumeFromFile(filename, dtype="float"):
    """creates a new mincVolume from existing file"""
    v = mincVolume(filename, dtype)
    v.openFile()
    return(v)
    
def volumeFromInstance(volInstance, outputFilename, dtype="float", data=False):
    """creates new mincVolume from another mincVolume"""
    v = mincVolume(outputFilename, dtype)
    v.copyDimensions(volInstance)
    v.copyDtype(volInstance)
    v.createVolumeHandle()
    if data:
        if not volInstance.dataLoaded:
            volInstance.loadData()
        v.createVolumeImage()  
        v.data = volInstance.data.copy()
    
    return(v)

def volumeLikeFile(likeFilename, outputFilename, dtype="float"):
    """creates a new mincVolume with dimension info taken from an existing file"""
    lf = volumeFromFile(likeFilename)
    v = volumeFromInstance(lf, outputFilename, dtype)
    lf.closeVolume()
    return(v)
