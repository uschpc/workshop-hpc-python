import numpy as np
import multiprocessing as mp
import time, sys, getopt, os, io
import h5py

def generate_data(x,y,n,t):
    value = (x/10)**2*(y/10) + (y/10)**2*(x/10)+t/n
    value = value %1 # Keep number between 0 and 1
    return value

def write_data(X,Y,output,nFiles,i,hf):

    filename=("output/%s%05d" %(output,i))
    Z = generate_data(X,Y,nFiles,i)

    hf.create_dataset(filename,data=Z)


def set_params(argv):
    nFiles=15
    nWorkers=1
    size=100
    output="data"

    try:
        opts,args=getopt.getopt(argv,"hn:s:o:w:",["nFiles=","size=", "output=", "nWorkers="])
    except getopt.GetoptError:
        print("plot.py -n <number_of_files> -s <array_size> -o <outfile>")
        sys.exit(2)
    for opt,arg in opts:
        if opt=='-h':
            print("plot.py -n <number_of_files> -s <array_size> -o <outfile>")
            sys.exit()
        elif opt in ("-n", "--nFiles"):
            print("Setting nFiles")
            nFiles = int(arg)
        elif opt in ("-s", "--size"):
            print("Setting size")
            size = int(float(arg))
        elif opt in ("-o", "--output"):
            print("Setting output")
            output = arg

# Summarize params
    print('nFiles=%s' %nFiles)
    print('size= %s' %size)
    print('output_template=%s%%05d.txt ' %output)

    return nFiles,size,output, nWorkers


def main(argv):

    nFiles,size,output,nWorkers = set_params(argv)
    hf = h5py.File('output/%s.h5'%output, 'w')

    # Set XY coords
    x_origin=0
    y_origin=500
    x = np.arange(x_origin-size/2,x_origin+size/2,1)
    y = np.arange(y_origin-size/2,y_origin+size/2,1)
    X,Y = np.meshgrid(x,y)


    os.makedirs("output",exist_ok='True')
    for i in range(0,nFiles):
        write_data(X,Y,output,nFiles,i,hf)

if __name__=='__main__':
    main(sys.argv[1:])
