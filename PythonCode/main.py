import argparse
import json
import logging
import os
import Criteria
import numpy as np
from matplotlib import pyplot as plt
import time


# from python_utils import file_tqdm


def main():
    start_time = time.time()
    path_in = "python50k_eval.json"
    path_out = "output.json"
    criteria = [Criteria.SimpleGaussian(9.87, 1)]
    margin = 20

    if os.path.exists(path_out):
        os.remove(path_out)

    selected = []
    skipped = 0
    skipped2 = 0
    skipped3 = 0
    with open(path_in, "r") as f, open(path_out, "w") as fout:
        for i, line in enumerate(f):  # file_tqdm(f):
            tokenIds = []
            tokens = []
            dp = json.loads(line.strip())
            if len(dp) < 3:
                skipped += 1
                continue
            index = len(dp)
            for j in range(margin):
                index -= 1
                while (("value" not in dp[index]) or ("children" in dp[index])) and (index > 0):
                    index -= 1
                if index == 0:
                    break
                if "value" not in dp[index]:
                    print("somethings going very wrong in line: ", i, " index is: ", index)
                    print("length of dp is: ",  len(dp)-1)
                    print("dp[index] is: ", dp[index])
                    quit()
                tokenIds.append(index)
                tokens.append(dp[index])
            if len(tokens) == 0:
                # print("skipped line ", i, " due to lack of good leaf tokens")
                skipped2 += 1
                continue
            total_scores = np.array([])
            for c in criteria:
                scores = np.array(c.get_score(tokens, i))
                if total_scores.shape != scores.shape:
                    total_scores = np.zeros(scores.shape)
                total_scores = total_scores + scores

            if np.max(total_scores) == -1.0:
                #print("skipped line ", i, " due to lack of good leaf tokens")
                skipped3 += 1
                continue
            if len(tokens[np.argmax(total_scores)]["value"]) >= 50:# or (i % 1000 == 0 and i !=0):
                print("i is: ", i)
                print("tokens are: ")
                tokenval = []
                for t in tokens:
                    tokenval.append(t["value"])
                print(tokenval)
                print()
                print("total_scores is: ")
                print(total_scores)
                print("argmax is: ")
                print(np.argmax(total_scores), " corresponds to length of ", len(tokens[np.argmax(total_scores)]["value"]))
                print("with value: ", tokens[np.argmax(total_scores)]["value"])
                print()
                if len(tokens[np.argmax(total_scores)]["value"]) >= 50:
                    quit()
            selected.append(tokens[np.argmax(total_scores)])
            r = range(0, tokenIds[np.argmax(total_scores)])
            print(json.dumps(dp[0:tokenIds[np.argmax(total_scores)] + 1]), file=fout)

            if i % 1000 == 0:
                print()
                print("finished ", i, " of ", 500000, " lines")
                print()
                print(skipped, " lines were skipped as they had less than 3 tokens")
                print(skipped2, "lines were skipped as no selection was possible")
                print(skipped3, "lines were skipped due to the best score beeing -1")
                for c in criteria:
                    c.update(selected)

        selectedLengths = np.array([])
        for s in selected:
            selectedLengths = np.append(selectedLengths, len(s["value"]))

        print()
        print("successfully executed programm")
        print("it took ", time.time() - start_time, "seconds to run this program")
        print("selected has a length of: ", len(selected), " expected is a length of: ", 50000)
        print("average length of selected tokens is: ", np.average(selectedLengths))
        print("graph of lengths in selected:")
        print()
        print("length of selectedLengths is: ", len(selectedLengths))
        max = np.max(selectedLengths)
        x = np.arange(round(max)+1)
        y = np.zeros(round(max)+1)
        for s in selectedLengths:
            y[round(s)] += 1
        plt.title("selected lengths")
        plt.xlabel("x axis caption")
        plt.ylabel("y axis caption")
        plt.plot(x, y)
        plt.show()





# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()
