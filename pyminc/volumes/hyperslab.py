import numpy as np


class HyperSlab(np.ndarray):
    """an ndarray with location and voxel-to-world mapping information"""
    def __new__(cls, data, start=None, separations=None,
                count=None, dimnames=None, dtype=None):

        if isinstance(data, np.ndarray):
            subarr = data.view(HyperSlab)
        else:
            raise TypeError("Can't handle non-ndarrays for the moment")
        # transform subarr into a hyperslab using view method
        #subarr = subarr.view(cls)
        if start is not None:
            subarr.start = start
        elif hasattr(data, 'start'):
            subarr.start = data.start
            
        if separations is not None:
            subarr.separations = separations
        elif hasattr(data, 'separations'):
            subarr.separations = data.separations
            
        if dimnames is not None:
            subarr.dimnames = dimnames
        elif hasattr(data, 'dimnames'):
            subarr.dimnames = data.dimnames
        
        if count is not None:
            subarr.count = count
        elif hasattr(data, 'count'):
            subarr.count = data.count
        
        return subarr
    
    def __array_finalize__(self, obj):
        self.start = getattr(obj, 'start', [])
        self.separations = getattr(obj, 'separations', [])
        self.dimnames = getattr(obj, 'dimnames', [])
        self.count = getattr(obj, 'count', [])

    def __repr__(self):
        desc = """
        array(data=
              %(data)s,
        start=%(start)s, count=%(count)s,
        separations=%(seps)s, dimnames=%(dims)s"""
        return desc % {'data': str(self), 'start': self.start, 'count': self.count,
                       'seps': self.separations, 'dims': self.dimnames}
