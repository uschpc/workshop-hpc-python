#!/usr/local/bin/python3
import numpy as np
import multiprocessing as mp
import time, sys, getopt, os, io, cProfile
from mpi4py import MPI

def generate_data(x,y,n,t):
    value = (x/10)**2*(y/10) + (y/10)**2*(x/10)+t/n
    value = value %1 # Keep number between 0 and 1
    return value

def write_data(X,Y,output,nFiles,i):

    filename=("output/%s%05d" %(output,i))
    Z = generate_data(X,Y,nFiles,i)

    np.save(filename,Z)


def set_params(argv):
    nFiles=15
    size=100
    output="data"
    debug=False

    try:
        opts,args=getopt.getopt(argv,"hdn:s:o:",["debug","nFiles=","size=", "output="])
    except getopt.GetoptError:
        print("plot.py -n <number_of_files> -s <array_size> -o <outfile>")
        sys.exit(2)
    for opt,arg in opts:
        if opt=='-h':
            print(" -n <number_of_files> -s <array_size> -o <outfile>")
            sys.exit()
        elif opt in ("-n", "--nFiles"):
            nFiles = int(arg)
        elif opt in ("-s", "--size"):
            size = int(float(arg))
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-d", "--debug"):
            debug = True


    return nFiles,size,output,debug


def main(nFiles,size,output):
    os.makedirs("output",exist_ok='True')
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    world_size  = MPI.COMM_WORLD.Get_size()


    if nFiles%(world_size) != 0:
        sys.exit("Uneven distribution of workers and work")

    # Set XY coords
    x_origin=0
    y_origin=500
    x = np.arange(x_origin-size/2,x_origin+size/2,1)
    y = np.arange(y_origin-size/2,y_origin+size/2,1)
    X,Y = np.meshgrid(x,y)


    n_chunks   = world_size

    print("My names is rank %d"%rank+  " and I'm starting...")
    chunks=None
    if rank == 0:
         # Summarize params
        print('world_size= %s' %world_size)
        print('nFiles=%s' %nFiles)
        print('output_template=%s%%05d.txt ' %output)
        print('size=%d' %size)

    # Send pieces of data from rank 0 to whole world
        data   = np.arange(nFiles,dtype='i')
        chunks = data.reshape((n_chunks,int(nFiles/n_chunks)))

    recvbuf = np.empty(int(nFiles/n_chunks),dtype='i')

    comm.Scatter(chunks,recvbuf,root=0)


    for i in recvbuf:
        #print("writing ...", i)
        write_data(X,Y,output,nFiles,i)


if __name__=='__main__':
    nFiles,size,output,debug = set_params(sys.argv[1:])
    if debug:
        pr = cProfile.Profile()
        pr.enable()
        main(nFiles,size,output)
        pr.disable()

        pid=int(os.getenv('SLURM_PROCID'))
        # Binary results
        #pr.dump_stats('cpu_%02d'%pid)
        # Text results
        with open( 'cpu_%02d' %pid, 'w') as output_file:
            sys.stdout = output_file
            pr.print_stats( sort='time' )
            sys.stdout = sys.__stdout__
    else:
        main(nFiles,size,output)
