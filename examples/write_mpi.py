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

    if world_size<= 1:
        sys.exit("World size must be greater than 1.")

    if nFiles%(world_size-1) != 0:
        sys.exit("Uneven distribution of workers and work")

    # Set XY coords
    x_origin=0
    y_origin=500
    x = np.arange(x_origin-size/2,x_origin+size/2,1)
    y = np.arange(y_origin-size/2,y_origin+size/2,1)
    X,Y = np.meshgrid(x,y)


    n_chunks   = world_size-1

    if n_chunks==0:
        n_chunks=1

    if rank == 0:
 # Summarize params
        print("My names is rank %d"%rank+  " and I'm starting...")
        print('world_size= %s' %world_size)
        print('nFiles=%s' %nFiles)
        print('output_template=%s%%05d.txt ' %output)
        print('size=%d' %size)
        data = np.arange(nFiles,dtype='i')
        recipient=0
        for chunk in np.array_split(data,n_chunks):
            recipient=(recipient+1)%world_size
            if recipient==0:
                recipient=1
            data_string=np.array2string(chunk)
            comm.Send([chunk,MPI.INT], dest=recipient, tag=77)
    else:
        data=np.empty(int(nFiles/n_chunks),dtype='i')
        comm.Recv([data,MPI.INT],source=0, tag=77)
        data_string=np.array2string(data)
        #print("My names is rank %d"%rank+  " and my data is/are\n"+data_string)
        for i in data:
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
