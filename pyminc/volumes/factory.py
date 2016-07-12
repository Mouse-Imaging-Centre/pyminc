"""factories for creating mincVolumes"""

from .volumes import mincException,mincVolume

def volumeFromFile(filename, dtype="double", readonly=True, labels=False):
    """creates a new mincVolume from existing file."""
    v = mincVolume(filename=filename, dtype=dtype, readonly=readonly, labels=labels)
    v.openFile()
    return(v)
    
def volumeFromInstance(volInstance, outputFilename, dtype="double", data=False,
                       dims=None, volumeType=None, path=False, labels=False):
    """creates new mincVolume from another mincVolume"""
    v = mincVolume(filename=outputFilename, dtype=dtype, readonly=False, labels=labels)
    v.copyDimensions(volInstance, dims)
    v.copyDtype(volInstance)
    v.createVolumeHandle(volumeType or volInstance.volumeType)
    v.copyHistory(volInstance)
    if data:
        if not volInstance.dataLoaded:
            volInstance.loadData()
        v.createVolumeImage()  
        v.data = volInstance.data.copy()
    if path:
        v.copyAttributes(volInstance, path)

    return(v)

def volumeLikeFile(likeFilename, outputFilename, dtype="double", volumeType=None,
                   labels=False, data=False):
    """creates a new mincVolume with dimension info taken from an existing file"""
    lf = volumeFromFile(filename=likeFilename, dtype=dtype, labels=labels)
    v = volumeFromInstance(volInstance=lf, outputFilename=outputFilename, 
                           dtype=dtype, volumeType=volumeType,
                           labels=labels, data=data)
    lf.closeVolume()
    return(v)

def volumeFromDescription(outputFilename, dimnames, sizes, starts, steps, volumeType="ushort",
                          dtype="double", labels=False,
                          x_dir_cosines=(1.0,0.0,0.0),
                          y_dir_cosines=(0.0,1.0,0.0),
                          z_dir_cosines=(0.0,0.0,1.0)):
    """creates a new mincVolume given starts, steps, sizes, and dimension names"""
    v = mincVolume(filename=outputFilename, dtype=dtype, readonly=False, labels=labels)
    v.createNewDimensions(dimnames, sizes, starts, steps, 
                          x_dir_cosines, y_dir_cosines, z_dir_cosines)
    v.createVolumeHandle(volumeType)
    v.createVolumeImage()
    return(v)

def volumeFromData(outputFilename, data, dimnames=("xspace", "yspace", "zspace"),
                   starts=(0,0,0), steps=(1,1,1),
                   volumeType="ushort", dtype="double", labels=False,
                   x_dir_cosines=(1.0,0.0,0.0),
                   y_dir_cosines=(0.0,1.0,0.0),
                   z_dir_cosines=(0.0,0.0,1.0)):
    """creates a mincVolume from a given array"""
    v = volumeFromDescription(outputFilename=outputFilename, sizes=data.shape,
                              dimnames=dimnames, starts=starts, steps=steps,
                              volumeType=volumeType, dtype=dtype, labels=labels,
                              x_dir_cosines=x_dir_cosines,
                              y_dir_cosines=y_dir_cosines,
                              z_dir_cosines=z_dir_cosines)
    if v.getDtype(data):
        v.dtype = v.getDtype(data)
    v.data = data
    return v
