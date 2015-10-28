#!/usr/bin/env python

from pyminc.volumes.factory import *
from numpy import *
from optparse import OptionParser

def convert_sva(filename, output_filename, step=0.2):
    infile = open(filename, 'r')
    comment = infile.readline()
    print("FILE: %s" % comment)
    dims = infile.readline().strip().split(":")[1].split(",")
    print("DIMS: %s" % dims)
    
    vol = volumeFromDescription(output_filename, 
                                ["yspace","zspace","xspace"],
                                [int(dims[0]), int(dims[1]), int(dims[2])],
                                [55,367,227], [-step,-step,-step])

    # now read the data
    while 1:
        line = infile.readline()
        if not line: break
        vals = line.strip().split(",")
        #print(vals)
        vol.data[int(vals[0]), int(vals[1]), int(vals[2])] = float(vals[3])

    vol.writeFile()

if __name__ == "__main__":
    sva = "/projects/mice/jlerch/allen/test-data/data/AtlasAnnotation200.sva"
    #sva = "/micehome/jlerch/downloads/77869800.sva"

    usage = "usage: %prog [options] input.sva output.mnc"

    parser = OptionParser(usage)

    parser.add_option("-s", "--step", dest="step",
                      help="step size of input volume",
                      type="float", default=0.2)

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")

    input_file = args[0]
    output_file = args[1]
    convert_sva(input_file, output_file, options.step)
    
                                
