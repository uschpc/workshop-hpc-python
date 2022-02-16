#!/usr/local/bin/python3
import numpy as np
import multiprocessing as mp
import queue as q
import time, sys, getopt, os, io, timeit

def generate_data(x,y,n,t):
    value = (x/10)**2*(y/10) + (y/10)**2*(x/10)+t/n
    value = value %1 # Keep number between 0 and 1
    return value

def write_data(X,Y,output,nFiles,i):

    filename=("output/%s%05d" %(output,i))
    Z = generate_data(X,Y,nFiles,i)

    t=time.time()
    np.save(filename,Z)
    elapsed = time.time()-t

    return elapsed

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
            print("plot.py -n <number_of_files> -s <array_size> -w <num_workers> -o <outfile>")
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
        elif opt in ("-w", "--nWorkers"):
            print("Setting output")
            nWorkers = int(arg)

# Summarize params
    print('nFiles=%s' %nFiles)
    print('nWorkers=%s' %nWorkers)
    print('size= %s' %size)
    print('output_template=%s%%06d.txt ' %output)

    return nFiles,size,output, nWorkers

class worker(mp.Process):
    def __init__(self,task_queue,size,output,nFiles,**kwargs):
        super(worker,self).__init__()
        #print("In init(), Process %s starting." %self.pid)
        x_origin=0
        y_origin=500
        x = np.arange(x_origin-size/2,x_origin+size/2,1)
        y = np.arange(y_origin-size/2,y_origin+size/2,1)
        self.X,self.Y = np.meshgrid(x,y)
        self.task_queue=task_queue
        self.nFiles=nFiles
        self.output=output


    def run(self):

        print("Starting Process:%d " % self.pid)
        #time.sleep(1)
        while True:
            try:
                #print("Getting work")
                i = self.task_queue.get(timeout=1)
            except q.Empty:
                print("No more work to do")
                #self.terminate()
                break

            elapsed=write_data(self.X,self.Y,self.output,self.nFiles,i)
            #print("%s is SOO busy with %d" % (self.pid,i) )
            self.task_queue.task_done()
        return
def main(argv):

    nFiles,size,output,nWorkers = set_params(argv)

    os.makedirs("output",exist_ok='True')

    # Set benchmark vars
    elapsed=np.zeros(nFiles)


    workers=[]

    # Create work
    for i in range(0,nFiles):
        task_queue.put(i)

    # start workers
    for i in range(0,nWorkers):
        w=worker(task_queue,size,output,nFiles)
        w.start()
        workers.append(w)

    print("Waiting for work to complete...")
    task_queue.join()

    for w in workers:
        w.join()

    return

if __name__=='__main__':
    __spec__ = None
    task_queue = mp.JoinableQueue()
    main(sys.argv[1:])
