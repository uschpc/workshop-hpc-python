#!/usr/local/bin/python3
import numpy as np
import multiprocessing as mp
import time, sys, getopt, os, io

def generate_data(x,y,n,t):
    value = (x/10)**2*(y/10) + (y/10)**2*(x/10)+t/n
    value = value %1 # Keep number between 0 and 1
    return value

def write_data(x,y,output,nFiles,fileID):

    filename=("output/%s%05d.txt" %(output,fileID))

    i_max=len(x)
    j_max=len(y)
    data=np.zeros((i_max,j_max))

    for i in range(i_max):
        for j in range(j_max):
            data[i,j]=generate_data(x[i],y[j],nFiles,fileID)

    np.savetxt(filename,data)

def set_params(argv):
    nFiles=15
    nWorkers=1
    size=100
    output="data"

    try:
        opts,args=getopt.getopt(argv,"hn:s:o:",["nFiles=","size=", "output=", "nWorkers="])
    except getopt.GetoptError:
        print(" -n <number_of_files> -s <array_size> -o <outfile>")
        sys.exit(2)
    for opt,arg in opts:
        if opt=='-h':
            print("-n <number_of_files> -s <array_size> -o <outfile>")
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

    # Set XY coords
    x_origin=0
    y_origin=500
    x = np.arange(x_origin-size/2,x_origin+size/2,1)
    y = np.arange(y_origin-size/2,y_origin+size/2,1)

    os.makedirs("output",exist_ok='True')
    for i in range(0,nFiles):
        write_data(x,y,output,nFiles,i)

if __name__=='__main__':
    main(sys.argv[1:])
