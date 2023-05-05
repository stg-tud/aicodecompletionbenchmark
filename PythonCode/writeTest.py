import time
import os.path
from os import path
import os
import numpy as np

def folder(path_in, path_out,path_mid = ""):
    if not os.path.exists(path.join(path_out, path_mid)):
    #     os.remove(path.join(path_out, path_mid))
        os.mkdir(path.join(path_out, path_mid))
    directory = path.join(path_in, path_mid)


    for file in os.listdir(directory):
        filename = path.join(directory, file)
        if filename[0] == '.':
            continue
        if path.isfile(filename):
            global count
            if count % 10000 == 0:
                print("processed ", count, " files.")

            count += 1
            singlefile(filename,path.join(path_out,path_mid,file))
        elif path.isdir(filename):
            print("recursively starting again with filepath: ", filename)
            folder(path_in, path_out,path_mid = path.join(path_mid,file))


def singlefile(_in_, _out_):
    with open(_in_, "r") as f, open(_out_, "w") as fout:
        for i, line in enumerate(f):  # file_tqdm(f):
            print(line, file=fout)



count = 0
if __name__ == "__main__":

    start_time = time.time()
    _in_ = "Static"
    _out_ = "outputTest"
    if path.isfile(_in_):

        singlefile(_in_, _out_)
    else:
        folder(_in_, _out_)
    print("it took ", time.time() - start_time, "seconds to run this program")
