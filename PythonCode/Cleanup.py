import json
import os
from matplotlib import pyplot as plt
import time
import random


def main():
    start_time = time.time()
    path_in = "C:\\Users\\milan\\Desktop\\realAsts.json"
    path_out = "C:\\Users\\milan\\Desktop\\cleanedAstsEval.json"
    removed_lines = 0
    short_lines = 0
    pre_length = 100000
    target_length = 50000
    red_pre_length = pre_length
    if os.path.exists(path_out):
        os.remove(path_out)
    with open(path_in, "r", encoding ="utf-8") as f, open(path_out, "w") as fout:
        for i, line in enumerate(f):
            if i % 10000 == 0:
                print("read", i , "lines\n")
            if(i - short_lines - removed_lines >= target_length + pre_length):
                break
            try:
                dp = json.loads(line.strip())

                if(len(dp) > 50):
                    if(red_pre_length == 0):
                        print(json.dumps(dp), file=fout)
                    else:
                        red_pre_length -= 1

                else:
                    short_lines += 1
            except:
                print("removed a line")
                removed_lines += 1
                continue

    print("it took ", time.time() - start_time, "seconds to run this program")
    print(removed_lines, "lines were removed")
    print(short_lines, "lines were removed due to short length")



if __name__ == "__main__":
    main()